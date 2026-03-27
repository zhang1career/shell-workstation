#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音高拾音脚本（Pick Sound / 采样）

功能：
    从麦克风实时采集音频，检测音高（基频），将不同音高分别保存为 WAV 文件。
    适用于乐器/人声采样、音高素材收集等场景。每个音高只保存一次，按 Enter 结束拾音。

用法：
    python pick_sound.py <输出目录>

示例：
    python pick_sound.py ./samples
    python pick_sound.py ~/Music/piano_notes

依赖：
    - Python 3.6+
    - sounddevice（录音）
    - soundfile（写 WAV）
    - librosa（音高检测 YIN、音高转音名）
    - numpy
"""

import os
import queue
import sys
import threading
import time

import librosa
import numpy as np
import sounddevice as sd
import soundfile as sf

# ================= 配置参数 =================
SAMPLE_RATE = 44100
CHANNELS = 1
CHUNK_DURATION = 0.5  # 每次分析的音频块时长（秒）
MAX_RECORD_DURATION = 1.0  # 每个音高最多保存的时长（秒）
ENERGY_THRESHOLD = 0.01  # 能量阈值，低于此值视为静音/环境噪声，不处理
FMIN = librosa.note_to_hz("C2")  # 检测音高下限（约 65 Hz）
FMAX = librosa.note_to_hz("C7")  # 检测音高上限（约 2093 Hz）
# ===========================================

# 录音数据队列（由 sounddevice 回调写入，主循环读取）
audio_queue = queue.Queue()
# 已采集过的音高（音名，如 C4、A#5），避免重复保存
captured_notes = set()
# 主循环是否继续运行；按 Enter 后由后台线程设为 False
running = True


def audio_callback(indata, frames, time_info, status):
    """sounddevice 录音回调：将收到的音频块放入队列。"""
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(indata.copy())


def rms_energy(audio):
    """计算音频块 RMS 能量，用于过滤静音。"""
    return np.sqrt(np.mean(audio ** 2))


def detect_pitch(audio):
    """
    使用 YIN 算法检测音频块的主音高（基频，Hz）。
    若无法可靠检测则返回 None。
    """
    audio = audio.flatten()
    f0 = librosa.yin(
        audio,
        fmin=FMIN,
        fmax=FMAX,
        sr=SAMPLE_RATE,
    )
    f0 = f0[np.isfinite(f0)]
    if len(f0) == 0:
        return None
    return np.median(f0)


def _wait_enter_stop():
    """后台线程：等待用户按 Enter 后设置 running=False，无需管理员权限。"""
    global running
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        pass
    running = False


def main(output_dir):
    """主流程：打开麦克风，循环检测音高并保存新音高到输出目录，直到用户按 Enter。"""
    global running
    output_path = os.path.abspath(output_dir)
    os.makedirs(output_path, exist_ok=True)

    print("=" * 50)
    print("音高拾音")
    print("=" * 50)
    print(f"输出目录: {output_path}")
    print(f"采样率: {SAMPLE_RATE} Hz，单声道")
    print(f"音高范围: C2 ~ C7")
    print("=" * 50)
    print("🎙️ 开始拾音（按 Enter 键停止）...")
    print()

    # 用后台线程等待 Enter，避免在 macOS 上需要管理员权限的按键监听
    stop_thread = threading.Thread(target=_wait_enter_stop, daemon=True)
    stop_thread.start()

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        callback=audio_callback,
        blocksize=int(SAMPLE_RATE * CHUNK_DURATION),
    ):
        while running:
            try:
                audio_chunk = audio_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            # 过滤静音与环境噪声
            if rms_energy(audio_chunk) < ENERGY_THRESHOLD:
                continue

            pitch_hz = detect_pitch(audio_chunk)
            if pitch_hz is None:
                continue

            note = librosa.hz_to_note(pitch_hz, octave=True)

            # 该音高已保存过则跳过
            if note in captured_notes:
                continue

            print(f"🎵 识别到音高：{note}")

            # 再采集若干块，凑足 MAX_RECORD_DURATION 时长后保存
            frames_needed = int(SAMPLE_RATE * MAX_RECORD_DURATION)
            collected = [audio_chunk]
            while sum(len(x) for x in collected) < frames_needed:
                try:
                    collected.append(audio_queue.get(timeout=0.1))
                except queue.Empty:
                    break

            audio_data = np.concatenate(collected, axis=0)[:frames_needed]
            filename = os.path.join(output_dir, f"{note}.wav")
            sf.write(filename, audio_data, SAMPLE_RATE)

            captured_notes.add(note)
            print(f"💾 已保存：{filename}")

            time.sleep(0.2)  # 防抖，避免同一音高连续触发

    print()
    print("✅ 拾音完成")
    print("已采集音高：", sorted(captured_notes))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法：python pick_sound.py <输出目录>")
        print("示例：python pick_sound.py ./samples")
        sys.exit(1)
    main(sys.argv[1])
