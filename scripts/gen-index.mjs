// Собирает src/videos.generated.ts из всех videos/*/{script,timeline}.json
import {readdirSync, existsSync, writeFileSync} from 'node:fs';
const slugs = readdirSync('videos', {withFileTypes: true}).filter((d) => d.isDirectory() && existsSync(`videos/${d.name}/timeline.json`)).map((d) => d.name);
const lines = [`// АВТОГЕНЕРАЦИЯ: node scripts/gen-index.mjs`];
slugs.forEach((s, i) => {
  lines.push(`import script${i} from '../videos/${s}/script.json';`, `import timeline${i} from '../videos/${s}/timeline.json';`);
});
lines.push(`export const VIDEOS: Record<string, {script: unknown; timeline: unknown}> = {`);
slugs.forEach((s, i) => lines.push(`  '${s}': {script: script${i}, timeline: timeline${i}},`));
lines.push(`};`, ``);
writeFileSync('src/videos.generated.ts', lines.join('\n'));
console.log('videos:', slugs.join(', ') || '(пусто)');
