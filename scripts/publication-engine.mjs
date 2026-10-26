// A single CommonMark/HTML consumer supplies hygiene values, links and real anchors.
// parse5 and github-slugger use the same pinned versions as the site's publication tooling.
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import MarkdownIt from 'markdown-it';
import GithubSlugger from 'github-slugger';
import { parse, serialize } from 'parse5';
import { cssValues, decodePercent } from './css-publication.mjs';

const markdown = new MarkdownIt('commonmark', { html: true }).enable(['table', 'strikethrough']);
const block = new Set(['p', 'div', 'section', 'article', 'header', 'footer', 'li', 'ul', 'ol', 'blockquote', 'pre', 'br', 'hr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'tr', 'td', 'th']);
const urls = new Set(['href', 'src', 'srcset', 'action', 'poster']);
function nodes(node) { return [node, ...(node.childNodes ?? []).flatMap(nodes)]; }
function text(node, prose = false, boundaries = true) {
  if (['style', 'script'].includes(node.tagName) || (prose && ['code', 'pre'].includes(node.tagName))) return '';
  if (node.nodeName === '#text') return node.value;
  const value = (node.childNodes ?? []).map(child => text(child, prose, boundaries)).join('');
  return boundaries && block.has(node.tagName) ? `\n${value}\n` : value;
}
function strings(value) {
  if (typeof value === 'string') return [value];
  if (Array.isArray(value)) return value.flatMap(strings);
  if (value && typeof value === 'object') return Object.entries(value).flatMap(([key, item]) => [key, ...strings(item)]);
  return [];
}
function attribute(name, value) {
  return [value, ...(urls.has(name) ? [decodePercent(value)] : []), ...(name === 'style' ? cssValues(value, 'declarationList') : [])];
}
export function inspectDocument({ suffix, source, xml }) {
  if (suffix === '.css') return { text: '', prose: '', values: cssValues(source), links: [], ids: [] };
  if (xml) return {
    text: xml.text, prose: xml.text,
    values: [...xml.attributes.flatMap(([name, value]) => attribute(name, value)), ...xml.styles.flatMap(style => cssValues(style))], links: [], ids: []
  };
  const dom = parse(suffix === '.md' ? markdown.render(source) : source);
  const all = nodes(dom), slugger = new GithubSlugger();
  if (suffix === '.md') for (const node of all) {
    if (!/^h[1-6]$/u.test(node.tagName ?? '')) continue;
    // Assign IDs to the rendered headings. Code text and formatting follow the renderer's DOM.
    if (!node.attrs.some(attr => attr.name === 'id')) node.attrs.push({ name: 'id', value: slugger.slug(text(node, false, false)) });
  }
  const values = [], links = [], ids = [];
  for (const node of all) {
    if (node.tagName === 'style') values.push(...cssValues((node.childNodes ?? []).map(child => child.value ?? '').join('')));
    if (node.tagName === 'script' && node.attrs?.some(attr => attr.name === 'type' && ['application/json', 'application/ld+json'].includes(attr.value.toLowerCase()))) {
      values.push(...strings(JSON.parse((node.childNodes ?? []).map(child => child.value ?? '').join(''))));
    }
    for (const { name, value } of node.attrs ?? []) {
      values.push(...attribute(name, value));
      if (['href', 'src'].includes(name)) links.push(value);
      if (name === 'id' || (node.tagName === 'a' && name === 'name')) ids.push(value);
    }
  }
  return { text: text(dom), prose: text(dom, true), values, links, ids, html: serialize(dom) };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
try {
  const input = JSON.parse(readFileSync(0, 'utf8'));
  const output = input.map(document => {
    try { return inspectDocument(document); }
    catch { return { error: 'publication-decode' }; }
  });
  process.stdout.write(JSON.stringify(output));
} catch {
  // The Python boundary also captures startup errors from missing Node dependencies.
  process.stdout.write(JSON.stringify({ error: 'publication-decode' }));
  process.exitCode = 1;
}

}
