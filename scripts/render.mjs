// node scripts/render.mjs <slug> [--still=<секунда>]   →  out/<slug>.mp4
import {execFileSync} from 'node:child_process';
import {readFileSync, mkdirSync} from 'node:fs';
const [slug, ...rest] = process.argv.slice(2);
if (!slug) { console.error('usage: node scripts/render.mjs <slug> [--still=<сек>]'); process.exit(1); }
const run = (args) => execFileSync('npx', ['remotion', ...args], {stdio: 'inherit'});
execFileSync('node', ['scripts/gen-index.mjs'], {stdio: 'inherit'});
mkdirSync('out', {recursive: true});
const still = rest.find((a) => a.startsWith('--still='));
if (still) {
  const fps = JSON.parse(readFileSync(`videos/${slug}/timeline.json`, 'utf8')).fps;
  run(['still', 'src/index.ts', slug, `out/${slug}.png`, `--frame=${Math.round(parseFloat(still.split('=')[1]) * fps)}`]);
} else {
  run(['render', 'src/index.ts', slug, `out/${slug}.mp4`, '--codec=h264', '--crf=18']);
}
