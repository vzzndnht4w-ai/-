#!/usr/bin/env bash
# Установка инструментов для видео «Шлюз 9» в новой (пустой) сессии.
# Контейнер временный: всё, что стоит вне репозитория, нужно ставить заново.
set -e
export HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# 1. Python: 2D-рендер (skia), озвучка, распознавание
apt-get install -y -q libegl1 libgl1 >/dev/null 2>&1 || true
pip install -q skia-python pycairo numpy pillow piper-tts faster-whisper

# 2. Remotion + Lottie (проект shluz9/remotion)
(cd "$ROOT/remotion" && npm install --no-audit --no-fund)

# 3. HyperFrames CLI
npm install -g hyperframes

# 4. OpenMontage (только чтение/использование; лежит вне репозитория)
if [ ! -d /home/user/openmontageinc/openmontage ]; then
  GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/OpenMontageInc/openmontage /home/user/openmontageinc/openmontage
fi
(cd /home/user/openmontageinc/openmontage && pip install -q -r requirements.txt && cd remotion-composer && npm install --no-audit --no-fund)

# 5. Голоса Piper (русский) — модель не хранится в git
mkdir -p "$ROOT/tools/voices" && cd "$ROOT/tools/voices"
for e in onnx onnx.json; do
  [ -f ru_RU-ruslan-medium.$e ] || curl -sL -o ru_RU-ruslan-medium.$e https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/ruslan/medium/ru_RU-ruslan-medium.$e
done
# Silero v3 RU (зеркало HuggingFace; лицензия CC BY-NC-SA — только некоммерческое использование).
# Файл — torch.package (pickle), поэтому сверяем контрольную сумму с проверенной версией.
SILERO_SHA=cf60b47ec8a9c31046021d2d14b962ea56b8a5bf7061c98accaaaca428522f85
if [ ! -f silero_v3_ru.pt ]; then
  curl -sL -o silero_v3_ru.pt https://huggingface.co/imperialwool/silero-model-v3-ru/resolve/main/model.pt
fi
echo "$SILERO_SHA  silero_v3_ru.pt" | sha256sum -c - || { echo "Контрольная сумма Silero не совпала — файл удалён"; rm -f silero_v3_ru.pt; exit 1; }
echo "Готово. Проверка: hyperframes doctor"
