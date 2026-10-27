// Supervisor pattern adapted from the site's scripts/run.mjs at 3abce0f348126bf7ec5d1bf68461a2fed94aad9c.
// Start this trusted bootstrap before parsing/importing any checker or its dependencies.
import { spawn } from 'node:child_process';
import { StringDecoder } from 'node:string_decoder';
import { constants } from 'node:os';

let child, failed = false;
const fail = () => {
  if (failed) return;
  failed = true;
  child?.kill('SIGTERM');
  process.stderr.write('diagnostic-boundary: command unavailable\n');
  process.exitCode = 1;
};
process.on('uncaughtException', fail);
process.on('unhandledRejection', fail);

try {
  // Policy import/parse failures remain inside a fixed-diagnostic boundary.
  const { readTokens, redactor } = await import('./diagnostic-policy.mjs');
  const sanitize = redactor(readTokens());
  const args = process.argv.slice(2);
  if (!args.length) throw new Error();
  child = spawn(args[0], args.slice(1), { stdio: ['inherit', 'pipe', 'pipe'] });
  const streams = [[child.stdout, process.stdout], [child.stderr, process.stderr]].map(([source, destination]) => {
    const decoder = new StringDecoder('utf8');
    let pending = '';
    source.on('data', bytes => { pending += decoder.write(bytes); });
    source.on('end', () => { pending += decoder.end(); });
    source.on('error', fail);
    // Buffer the complete stream so a literal split by writes or line breaks cannot escape.
    return () => destination.write(sanitize(pending));
  });
  child.on('error', fail);
  for (const signal of ['SIGINT', 'SIGTERM', 'SIGHUP']) process.on(signal, () => child.kill(signal));
  child.on('close', (code, signal) => {
    if (failed) return;
    for (const flush of streams) flush();
    process.exitCode = code ?? 128 + (constants.signals[signal] ?? 1);
  });
} catch (error) {
  if (error?.rule === 'identifier-deny-tokens') {
    process.stderr.write('configuration:0: identifier-deny-tokens\n');
    process.exitCode = 1;
  } else fail();
}
