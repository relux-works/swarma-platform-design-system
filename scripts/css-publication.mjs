// Publication values use the pinned CSS Tree parser, independent of contrast's Chromium measurements.
import { parse, walk, generate, ident } from 'css-tree';

// Shared URL decoding from the site's publication module, commit 14e4707a5182cfa02def48e4724a589df2344d69.
export const decodePercent = value => value.replace(/(?:%[0-9a-f]{2})+/giu, bytes => Buffer.from(bytes.replaceAll('%', ''), 'hex').toString('utf8'));

export function cssValues(source, context = 'stylesheet') {
  const ast = parse(source, { context, parseCustomProperty: true, onParseError(error) { throw error; } });
  const values = [generate(ast)];
  walk(ast, node => {
    if (node.type === 'String') values.push(node.value);
    if (node.type === 'Url') values.push(node.value, decodePercent(node.value));
    if (node.type === 'Identifier') values.push(ident.decode(node.name));
    if (node.type === 'Value') {
      // CSS generated content concatenates adjacent strings, including across comments.
      let group = [];
      const flush = () => { if (group.length) values.push(group.join('')); group = []; };
      node.children.forEach(child => { if (child.type === 'String') group.push(child.value); else flush(); });
      flush();
    }
  });
  return values;
}
