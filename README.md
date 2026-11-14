# video-factory
Вертикальные объясняющие ролики, собранные кодом (Remotion) + озвучка TTS.

```bash
npm install
pip install edge-tts
python3 scripts/tts.py demo --fake      # без сети: проверка вёрстки
node scripts/render.mjs demo --still=7  # кадр → out/demo.png
npm run studio                          # живой предпросмотр
```
Правила проекта и команды агентов — в `CLAUDE.md`. Новый ролик: `/make-video <тема>`.
