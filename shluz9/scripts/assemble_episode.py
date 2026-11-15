#!/usr/bin/env python3
"""
Скрипт автоматической сборки вертикального видео (1080x1920, 9:16) для проекта «Шлюз 9».
Использование:
    python3 scripts/assemble_episode.py episodes/ep00_last_turn
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def run(cmd):
    print(">>", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main():
    if len(sys.argv) < 2:
        print("Укажите путь к папке серии, например: python3 scripts/assemble_episode.py episodes/ep00_last_turn")
        sys.exit(1)

    ep_dir = Path(sys.argv[1]).resolve()
    prompts_file = ep_dir / "prompts.json"
    images_dir = ep_dir / "images"
    audio_dir = ep_dir / "audio"
    srt_file = ep_dir / "subtitles.srt"
    temp_dir = ep_dir / "_temp_clips"
    temp_dir.mkdir(exist_ok=True)

    with open(prompts_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    fps = data.get("fps", 30)
    clips = []

    for frame in data["frames"]:
        idx = frame["id"]
        img_path = images_dir / frame["filename"]
        if not img_path.exists():
            raise FileNotFoundError(f"Не найден кадр: {img_path}")

        dur = frame["duration_sec"]
        total_frames = int(dur * fps)
        motion = frame.get("motion", "zoom_in")
        clip_path = temp_dir / f"clip_{idx:02d}.mp4"

        # Настройка движения камеры (Ken Burns) для 1080x1920
        if motion == "zoom_out":
            zoom_expr = f"z='1.08-0.08*(on/{total_frames})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        elif motion == "pan_right":
            zoom_expr = f"z='1.08':x='(iw-iw/zoom)*(on/{total_frames})':y='ih/2-(ih/zoom/2)'"
        elif motion == "pan_left":
            zoom_expr = f"z='1.08':x='(iw-iw/zoom)*(1-on/{total_frames})':y='ih/2-(ih/zoom/2)'"
        elif motion == "tilt_up":
            zoom_expr = f"z='1.08':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1-on/{total_frames})'"
        elif motion == "pan_down":
            zoom_expr = f"z='1.08':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(on/{total_frames})'"
        elif motion == "shake":
            zoom_expr = "z='1.06':x='iw/2-(iw/zoom/2)+sin(on*1.8)*8':y='ih/2-(ih/zoom/2)+cos(on*2.1)*8'"
        else:  # zoom_in / static_slow
            zoom_expr = f"z='1.0+0.08*(on/{total_frames})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"

        vf = (
            f"scale=2160:3840:force_original_aspect_ratio=increase,"
            f"crop=2160:3840,"
            f"zoompan={zoom_expr}:d={total_frames}:s=1080x1920:fps={fps},"
            f"format=yuv420p"
        )

        run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(img_path),
            "-vf", vf, "-t", str(dur), "-c:v", "libx264", "-pix_fmt", "yuv420p",
            str(clip_path)
        ])
        clips.append(clip_path)

    concat_list = temp_dir / "concat.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for c in clips:
            f.write(f"file '{c.as_posix()}'\n")

    video_no_subs = temp_dir / "video_raw.mp4"
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c", "copy", str(video_no_subs)
    ])

    # Наложение субтитров и аудио (если файлы присутствуют)
    vo_file = audio_dir / "voiceover.mp3"
    amb_file = audio_dir / "ambient.mp3"
    final_output = ep_dir / "output.mp4"

    cmd = ["ffmpeg", "-y", "-i", str(video_no_subs)]
    has_vo = vo_file.exists()
    has_amb = amb_file.exists()

    if has_vo:
        cmd += ["-i", str(vo_file)]
    if has_amb:
        cmd += ["-i", str(amb_file)]

    vf_subs = []
    if srt_file.exists():
        escaped_srt = srt_file.as_posix().replace(":", "\:")
        style = "FontName=Arial,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=120,Bold=1"
        vf_subs.append(f"subtitles='{escaped_srt}':force_style='{style}'")

    if vf_subs:
        cmd += ["-vf", ",".join(vf_subs)]

    if has_vo and has_amb:
        cmd += [
            "-filter_complex", "[1:a]volume=1.0[vo];[2:a]volume=0.25[amb];[vo][amb]amix=inputs=2:duration=first[aout]",
            "-map", "0:v", "-map", "[aout]"
        ]
    elif has_vo:
        cmd += ["-map", "0:v", "-map", "1:a"]
    elif has_amb:
        cmd += ["-map", "0:v", "-map", "1:a"]

    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", str(final_output)]
    run(cmd)
    print(f"Готово! Итоговое видео сохранено: {final_output}")


if __name__ == "__main__":
    main()
