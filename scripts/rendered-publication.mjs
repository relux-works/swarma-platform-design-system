// Chromium supplies visible text and the full computed accessibility names/descriptions.
import { mkdir, readFile, realpath } from 'node:fs/promises';
import { dirname, extname, isAbsolute, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const origin = 'https://publication.invalid';
const types = { '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp', '.ico': 'image/x-icon',
  '.woff': 'font/woff', '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.html': 'text/html', '.htm': 'text/html' };

function contained(root, path) {
  const suffix = relative(root, path);
  return suffix !== '..' && !suffix.startsWith('../') && !isAbsolute(suffix);
}

export async function renderDocuments(documents, sources, publicationRoot) {
  const scratch = resolve(dirname(fileURLToPath(import.meta.url)), '../.temp');
  await mkdir(scratch, { recursive: true });
  let browser;
  const deadline = setTimeout(() => { browser?.close().catch(() => {}); }, 50_000);
  try {
    const root = await realpath(publicationRoot);
    browser = await chromium.launch({
      executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || undefined,
      args: ['--disable-background-networking'],
      env: { ...process.env, TMPDIR: process.env.TMPDIR || scratch, XDG_CACHE_HOME: resolve(scratch, 'browser-cache') },
    });
    // Static local resources use a synthetic origin and their real document paths. No network server is started.
    // Author scripts, service workers and remote resources remain disabled.
    const context = await browser.newContext({ javaScriptEnabled: false, serviceWorkers: 'block' });
    let currentURL, currentDocument, resourceFailed;
    await context.route('**/*', async route => {
      const url = new URL(route.request().url());
      if (url.origin !== origin || route.request().resourceType() === 'script') return route.abort();
      try {
        if (url.href === currentURL) return await route.fulfill({ contentType: 'text/html; charset=utf-8', body: currentDocument.html });
        const target = resolve(root, '.' + decodeURIComponent(url.pathname));
        if (!contained(root, target) || !contained(root, await realpath(target))) throw new Error('resource boundary');
        const body = await readFile(target);
        await route.fulfill({ contentType: types[extname(target).toLowerCase()] || 'application/octet-stream', body });
      } catch {
        resourceFailed = true;
        await route.abort();
      }
    });
    const page = await context.newPage();
    const session = await context.newCDPSession(page);
    await session.send('Accessibility.enable');
    for (const [index, document] of documents.entries()) {
      if (document.error || !document.html) continue;
      const location = resolve(sources[index].path);
      if (!contained(root, location)) throw new Error('document boundary');
      currentURL = origin + '/' + relative(root, location).split('/').map(encodeURIComponent).join('/');
      currentDocument = document;
      resourceFailed = false;
      await page.goto(currentURL, { waitUntil: 'load', timeout: 10_000 });
      await page.evaluate(() => document.fonts.ready);
      if (resourceFailed) {
        document.error = 'publication-decode';
        continue;
      }
      document.text = await page.locator('body').innerText();
      // Retain individually decoded source text, including hidden values, without reconstructing visible prose.
      document.decoded = await page.evaluate(() => {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT), values = [];
        for (let node; (node = walker.nextNode());) {
          if (node.parentElement?.closest('style, script')) continue;
          values.push([node.textContent, !node.parentElement?.closest('code, pre')]);
        }
        return values;
      });
      // The full tree includes controls that "interesting only" snapshots can omit, and resolves hidden IDREFs.
      const { nodes } = await session.send('Accessibility.getFullAXTree');
      // Static text is already covered by DOM prose with its code exemption. All AX values still receive
      // identifier policy; semantic control names/descriptions also receive prose punctuation policy.
      document.accessible = nodes.flatMap(node => [node.name?.value, node.description?.value, node.value?.value]
        .filter(value => typeof value === 'string')
        .map(value => [value, !['StaticText', 'InlineTextBox', 'code'].includes(node.role?.value)]));
      document.prose = await page.evaluate(() => {
        document.querySelectorAll('pre, code').forEach(node => node.remove());
        return document.body.innerText;
      });
    }
    return documents;
  } finally {
    clearTimeout(deadline);
    await browser?.close();
  }
}
