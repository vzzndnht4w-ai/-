import {Config} from '@remotion/cli/config';
Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
// В облачной среде Chromium лежит здесь; на обычной машине файла нет — Remotion скачает свой.
import {existsSync} from 'node:fs';
if (existsSync('/opt/pw-browsers/chromium')) Config.setBrowserExecutable('/opt/pw-browsers/chromium');
