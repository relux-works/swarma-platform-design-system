// Bootstrap policy: the same strict ASCII contract as diagnostics.py, without importing Python.
import { readFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';

const invalid = () => { const error = new Error(); error.rule = 'identifier-deny-tokens'; return error; };
export function readTokens() {
  const explicit = process.env.IDENT_DENY_TOKENS ?? '';
  let source = explicit;
  if (!source) {
    if (!['', '0', 'false'].includes((process.env.CI ?? '').toLowerCase())) return [];
    try { source = readFileSync(join(homedir(), '.config/swarma-site/deny-tokens.txt'), 'utf8'); }
    catch (error) { if (error.code === 'ENOENT') return []; throw invalid(); }
  }
  const tokens = source.split(/[,\r\n]+/u).map(token => token.replace(/^[ \t\r\n\v\f]+|[ \t\r\n\v\f]+$/gu, '')).filter(Boolean);
  if (!tokens.length || tokens.some(token => /^[a-z0-9][a-z0-9._-]{2,}$/u.exec(token)?.[0] !== token)) throw invalid();
  return tokens;
}

// Map the Python policy's ASCII/separator comparison back to original UTF-16 spans.
const separator = /[\s\p{Z}\p{Cf}\u001c-\u001f\u0085]/u;
const fold = value => value.replace(/[A-Z]/gu, letter => letter.toLowerCase());
export function redactor(tokens) {
  return value => {
    const positions = [];
    let compact = '', offset = 0;
    for (const character of value) {
      const end = offset + character.length;
      if (!separator.test(character)) {
        compact += fold(character);
        for (let index = offset; index < end; index += 1) positions.push([offset, end]);
      }
      offset = end;
    }
    const spans = [];
    for (const token of tokens) {
      for (let found = compact.indexOf(token); found >= 0; found = compact.indexOf(token, found + 1)) {
        spans.push([positions[found][0], positions[found + token.length - 1][1]]);
      }
    }
    const merged = [];
    for (const [start, end] of spans.sort((a, b) => a[0] - b[0])) {
      const previous = merged.at(-1);
      if (previous && start <= previous[1]) previous[1] = Math.max(previous[1], end);
      else merged.push([start, end]);
    }
    for (const [start, end] of merged.reverse()) value = value.slice(0, start) + '[redacted]' + value.slice(end);
    return value;
  };
}
