import {build} from 'esbuild';
import {mkdir, stat} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {resolve, dirname} from 'node:path';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const outdir = resolve(root, '.generated/vendor');
await mkdir(outdir, {recursive: true});
const common = {
  platform: 'browser',
  bundle: true,
  minify: true,
  target: ['chrome110'],
  legalComments: 'eof',
  logLevel: 'warning',
  absWorkingDir: root
};
await Promise.all([
  build({
    ...common,
    entryPoints: ['fontkit'],
    format: 'esm',
    outfile: resolve(outdir, 'fontkit.mjs')
  }),
  build({
    ...common,
    entryPoints: ['tools/fflate-entry.mjs'],
    format: 'iife',
    outfile: resolve(outdir, 'fflate.js')
  })
]);
for (const filename of ['fontkit.mjs', 'fflate.js']) {
  const file = resolve(outdir, filename);
  const info = await stat(file);
  if (info.size < 1000) throw new Error('Incomplete vendor bundle: ' + filename);
  console.log(filename + ': ' + info.size + ' bytes');
}
