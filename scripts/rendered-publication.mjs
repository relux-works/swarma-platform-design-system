// Chromium supplies visible text and the full computed accessibility names/descriptions.
import { mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

export async function renderDocuments(documents) {
  const scratch = resolve(dirname(fileURLToPath(import.meta.url)), '../.temp');
  await mkdir(scratch, { recursive: true });
  let browser;
  const deadline = setTimeout(() => { browser?.close().catch(() => {}); }, 50_000);
  try {
    browser = await chromium.launch({
      executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || undefined,
      args: ['--disable-background-networking'],
      env: { ...process.env, TMPDIR: scratch },
    });
    // Publication is inspected as static content. No author scripts, service workers or remote resources run.
    const context = await browser.newContext({ javaScriptEnabled: false, serviceWorkers: 'block' });
    await context.route('**/*', route => route.abort());
    const page = await context.newPage();
    const session = await context.newCDPSession(page);
    await session.send('Accessibility.enable');
    for (const document of documents) {
      if (document.error || !document.html) continue;
      await page.setContent(document.html, { waitUntil: 'domcontentloaded', timeout: 10_000 });
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
