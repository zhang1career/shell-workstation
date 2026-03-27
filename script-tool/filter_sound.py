#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音高 WAV 滤波与音量均衡脚本

功能：
    对按音高命名的 WAV 文件（如 C4.wav、A#5.wav）进行校验、带通滤波和音量均衡。
    文件名（不含扩展名）视为期望音高，仅当检测到的音高与文件名一致时才处理；
    通过带通滤波减弱无关频段噪声，并统一输出音量到目标 RMS。

用法：
    python filter_sound.py <输入目录> <输出目录>

示例：
    python filter_sound.py ./samples ./filtered
    python filter_sound.py ~/Music/raw_notes ~/Music/clean_notes

依赖：
    - Python 3.6+
    - numpy, librosa, soundfile, scipy
"""

import os
import sys

import librosa
import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter

# ================= 参数 =================
SR = 44100  # 统一采样率
FMIN = librosa.note_to_hz("C1")  # 音高检测下限
FMAX = librosa.note_to_hz("C8")  # 音高检测上限
RMS_TARGET_DB = -18.0  # 目标 RMS 音量（dB）
BANDWIDTH_OCT = 1.0  # 带通带宽（以检测到的音高为中心，±1 个八度）
# =======================================


def rms_db(signal):
    """计算信号 RMS 对应的分贝值（dB）。"""
    rms = np.sqrt(np.mean(signal ** 2))
    return 20 * np.log10(rms + 1e-9)


def normalize_rms(signal, target_db):
    """将信号 RMS 归一化到目标分贝。"""
    current_db = rms_db(signal)
    gain = 10 ** ((target_db - current_db) / 20)
    return signal * gain


def detect_pitch(signal, sr):
    """使用 YIN 算法检测主音高（Hz），无法检测时返回 None。"""
    f0 = librosa.yin(signal, fmin=FMIN, fmax=FMAX, sr=sr)
    f0 = f0[np.isfinite(f0)]
    if len(f0) == 0:
        return None
    return np.median(f0)


def bandpass_filter(signal, sr, center_hz, octaves):
    """以 center_hz 为中心、带宽 ±octaves 个八度的带通滤波。"""
    low = center_hz / (2 ** octaves)
    high = center_hz * (2 ** octaves)
    nyq = sr / 2
    low /= nyq
    high /= nyq
    b, a = butter(4, [low, high], btype="band")
    return lfilter(b, a, signal)


def process_directory(input_dir, output_dir):
    """
    遍历输入目录中的 WAV，按文件名音高校验、带通滤波、音量均衡后写入输出目录。
    仅处理「检测音高与文件名一致」的文件。
    """
    input_path = os.path.abspath(input_dir)
    output_path = os.path.abspath(output_dir)
    os.makedirs(output_path, exist_ok=True)

    print("=" * 50)
    print("音高 WAV 滤波与音量均衡")
    print("=" * 50)
    print(f"输入目录: {input_path}")
    print(f"输出目录: {output_path}")
    print(f"目标音量: {RMS_TARGET_DB} dB，带通带宽: ±{BANDWIDTH_OCT} 八度")
    print("=" * 50)

    wav_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".wav")]
    if not wav_files:
        print("⚠️ 输入目录下没有 WAV 文件")
        return

    print(f"找到 {len(wav_files)} 个 WAV 文件，开始校验与处理...")
    print()

    accepted = []

    for fname in wav_files:
        # 文件名（不含扩展名）即期望音高，如 C4.wav -> C4
        expected_note = os.path.splitext(fname)[0]
        in_path = os.path.join(input_dir, fname)

        y, sr = librosa.load(in_path, sr=SR, mono=True)

        pitch_hz = detect_pitch(y, sr)
        if pitch_hz is None:
            print(f"❌ {fname}：无法识别音高")
            continue

        detected_note = librosa.hz_to_note(pitch_hz, octave=True)

        if detected_note != expected_note:
            print(f"❌ {fname}：音高不匹配（检测 {detected_note}，期望 {expected_note}）")
            continue

        print(f"✅ {fname}：音高校验通过")

        # 以检测到的音高为中心做带通滤波，减弱带外噪声
        y_filtered = bandpass_filter(y, sr, pitch_hz, BANDWIDTH_OCT)
        accepted.append((fname, y_filtered))

    if not accepted:
        print("⚠️ 没有任何文件通过校验")
        return

    # 统一音量并写出
    print()
    print("🔊 开始音量均衡并写入输出目录")
    for fname, y in accepted:
        y_norm = normalize_rms(y, RMS_TARGET_DB)
        out_path = os.path.join(output_dir, fname)
        sf.write(out_path, y_norm, SR)
        print(f"💾 已输出：{out_path}")

    print()
    print("🎉 处理完成")
    print(f"通过校验并输出：{len(accepted)} 个文件")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法：python filter_sound.py <输入目录> <输出目录>")
        print("示例：python filter_sound.py ./samples ./filtered")
        sys.exit(1)

    process_directory(sys.argv[1], sys.argv[2])
