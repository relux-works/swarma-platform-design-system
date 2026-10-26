// Chromium resolves the shipped stylesheet; this bridge never parses CSS declarations.
import { readFileSync } from 'node:fs';
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises';
import { dirname, join, resolve, sep } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
let browser, fixture;
const deadline = setTimeout(() => { browser?.close().catch(() => {}); }, 60_000);
try {
  const input = JSON.parse(readFileSync(0, 'utf8'));
  const scratch = join(root, '.temp');
  await mkdir(scratch, { recursive: true });
  fixture = await mkdtemp(join(scratch, 'contrast-browser-'));
  const cssURL = pathToFileURL(resolve(input.tokens)).href;
  await writeFile(join(fixture, 'index.html'), `<!doctype html><html><head><link rel="stylesheet" href="${cssURL.replaceAll('&', '&amp;').replaceAll('"', '&quot;')}"></head><body></body></html>`);
  process.env.TMPDIR = scratch;
  browser = await chromium.launch({
    executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || undefined,
    args: ['--disable-background-networking'],
    env: { ...process.env, TMPDIR: scratch },
  });
  const page = await browser.newPage();
  const blocked = [];
  await page.route('**/*', route => {
    const url = route.request().url();
    if (url.startsWith('file:') && fileURLToPath(url).startsWith(root + sep)) return route.continue();
    blocked.push(true);
    return route.abort();
  });
  page.on('requestfailed', () => blocked.push(true));
  await page.goto(pathToFileURL(join(fixture, 'index.html')).href);
  const session = await page.context().newCDPSession(page);
  const appearances = [];
  for (const mode of input.modes) {
    const features = [
      { name: 'prefers-color-scheme', value: mode.scheme },
      { name: 'prefers-contrast', value: mode.contrast },
      { name: 'prefers-reduced-transparency', value: mode.reduced },
      { name: 'forced-colors', value: mode.forced },
    ];
    await session.send('Emulation.setEmulatedMedia', { media: 'screen', features });
    const result = await page.evaluate(async ({ mode, features, pairs, roles, control }) => {
      if (!features.every(({ name, value }) => matchMedia(`(${name}: ${value})`).matches)) throw new Error('media emulation unavailable');
      document.body.replaceChildren();
      const controlStyle = document.createElement('style');
      if (control && mode.name === 'light') controlStyle.textContent = ':root {--color-text-faint:#9aa1ab !important;}';
      document.body.append(controlStyle);
      const probe = style => {
        const element = document.createElement('div');
        element.textContent = 'Sample';
        element.style.cssText = 'forced-color-adjust:none;';
        Object.assign(element.style, style);
        document.body.append(element);
        return element;
      };
      const tokenProbes = Object.fromEntries(Object.keys(roles).map(key => [key, probe({ color: `var(--color-${key})` })]));
      const pairProbes = pairs.map(pair => probe({ color: `var(--color-${pair.fg})`, backgroundColor: `var(--color-${pair.bg})` }));
      const references = Object.fromEntries([...new Set(Object.values(roles))].map(color => [color, probe({ color })]));
      await new Promise(done => requestAnimationFrame(() => requestAnimationFrame(done)));
      const colors = Object.fromEntries(Object.entries(tokenProbes).map(([key, element]) => {
        const computed = getComputedStyle(element), value = computed.getPropertyValue(`--color-${key}`).trim();
        if (!value || !CSS.supports('color', value)) throw new Error('missing or invalid semantic color');
        return [key, computed.color];
      }));
      return {
        colors,
        pairs: pairProbes.map(element => {
          const computed = getComputedStyle(element);
          return { foreground: computed.color, background: computed.backgroundColor };
        }),
        system: Object.fromEntries(Object.entries(references).map(([role, element]) => [role, getComputedStyle(element).color])),
      };
    }, { mode, features, pairs: input.pairs, roles: input.roles, control: input.control });
    appearances.push({ name: mode.name, forced: mode.forced === 'active', ...result });
  }
  if (blocked.length) throw new Error('stylesheet resource unavailable');
  process.stdout.write(JSON.stringify({ appearances, browser: browser.version() }));
} catch {
  process.stdout.write(JSON.stringify({ error: 'contrast-browser' }));
  process.exitCode = 1;
} finally {
  clearTimeout(deadline);
  await browser?.close();
  if (fixture) await rm(fixture, { recursive: true, force: true });
}
