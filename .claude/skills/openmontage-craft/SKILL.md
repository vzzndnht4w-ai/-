---
name: openmontage-craft
description: Ремесло видеопроизводства из OpenMontage — принципы 2D-анимации (easing, anticipation, hold, staging), звукорежиссура (громкость, ducking, SFX, LUFS), режиссура озвучки (voice_performance, паузы, акценты, sample gate) и пайплайн анимации персонажей (риг, библиотека поз, сцены). Читать перед любой работой над анимацией, озвучкой, звуком и монтажом сериала «Шлюз 9».
---

# OpenMontage craft (адаптировано для проекта «Шлюз 9»)

Источник: github.com/OpenMontageInc/OpenMontage (AGPL-3.0). Здесь только знания (markdown-скилы), без их Python-фреймворка. Мы не запускаем их пайплайн целиком; берём приёмы и контрольные списки.

## Когда что читать
- Движение, тайминги, переходы: `references/animation-pipeline.md`
- Звук, громкость, SFX, дакинг, LUFS: `references/sound-design.md`
- Озвучка (TTS): план исполнения, паузы, акценты, проверка образца: `references/voice-performance-director.md`
- Персонажи как данные: риги, шарниры, позы, действия: `references/character-animation/`
- Выбор рантайма (HyperFrames, Remotion или свой рендер): `references/animation-runtime-selector.md`
- Сюжет и ритм коротких вертикальных видео: `references/storytelling.md`, `references/short-form.md`
- Вкус и самопроверка: `references/taste-direction.md`, `references/reviewer.md`

## Правила проекта поверх них
1. Канон проекта (`bible.md`, `prompts.md`, описания героев) важнее любых рекомендаций отсюда.
2. Перед платной или внешней генерацией сказать пользователю, что и чем делаем.
3. Озвучка: сначала образец самой трудной реплики, потом остальное; разборчивость проверять автоматическим распознаванием речи.
4. Движение: никакого linear для камеры и персонажей; anticipation, overshoot, hold на ключевых позах.
5. Громкость: диалог около −14 LUFS, музыка и эмбиент на 18–20 дБ ниже речи, SFX между ними.
