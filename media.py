import os
import sys
import ffmpy3
import scipy.signal as sig
import matplotlib.pyplot as plt
import numpy as np
from pydub import AudioSegment
from scipy import signal as sg
from fractions import Fraction

MOVIE_WAVE = "m_output.wav"
SOUND_WAVE = "s_output.wav"

class Movie:
    # ---メンバ変数一覧---
    # filename:ファイル名
    # sample_rate: サンプリング周波数
    # data:データ配列（未実装）
    # length_sec:再生時間

    # ---メソッド一覧---

    def __init__(self, input_filename):
        self.filename = input_filename
        movie_file = AudioSegment.from_file(self.filename)
        self.sample_late = movie_file.frame_rate
        self.length_sec = movie_file.duration_seconds
        self.data = np.array(movie_file.get_array_of_samples())

    # 指定されたbegin_secからlength_sec秒間の動画を書き出し
    def trim_movie(self, begin_sec, end_sec):
        if end_sec - begin_sec > self.length_sec:
            sys.exit(1)
        else:
            length_sec = end_sec - begin_sec

        cmd1 = "-ss " + str(begin_sec)
        cmd2 = "-t " + str(length_sec)
        out_name = "trim_" + str(self.filename)

        remove_wav(out_name)

        fc = ffmpy3.FFmpeg(
            inputs={self.filename: cmd1},
            outputs={out_name: cmd2}
        )
        fc.run()

    # sample_rateで指定した周波数でリサンプリングしてwavに書き出し
    def to_wave_with_subsampling(self, sample_rate):
        # HACK: wavを書き出さなくてもできる方法を探す
        ff = ffmpy3.FFmpeg(
            inputs={self.filename: None},
            outputs={MOVIE_WAVE: '-ac 1 -ar %d' % sample_rate}
        )
        ff.run()

    def sub_sampling(self, target_sample_rate):
        n_lpf = 4096
        cutoff_hz = target_sample_rate / 2

        frac = Fraction(target_sample_rate, self.sample_late)

        up = frac.numerator
        down = frac.denominator

        # up sampling
        wav_up = np.zeros(np.alen(self.data) * up)
        wav_up[::up] = up * self.data
        fs_up = self.sample_late * up

        cutoff = cutoff_hz / (fs_up / 2.0)
        lpf = sg.firwin(n_lpf, cutoff)

        # filtering and down sampling
        wav_down = sg.lfilter(lpf, [1], wav_up)[n_lpf // 2::down]

class Sound:
    # ---メンバ変数一覧---
    # filename:ファイル名
    # sample_rate: サンプリング周波数
    # length_sec: 再生時間

    # ---メソッド一覧---

    def __init__(self, input_filename):
        self.filename = input_filename

        sound_file = AudioSegment.from_file(self.filename)
        self.sample_late = sound_file.frame_rate
        self.length_sec = sound_file.duration_seconds
        self.data = np.array(sound_file.get_array_of_samples())

    # sample_rateで指定した周波数でリサンプリングしてwavに書き出し
    def to_wave_with_subsampling(self, sample_rate):
        # HACK: wavを書き出さなくてもできる方法を探す
        ff = ffmpy3.FFmpeg(
            inputs={self.filename: None},
            outputs={SOUND_WAVE: '-ac 1 -ar %d' % sample_rate}
        )
        ff.run()


# 動画と音声の時間差を計測。動画の方が進んでいれば符号はプラス，反対だとマイナス
def calculate_time_lag_sec(movie, sound):
    remove_wav(MOVIE_WAVE)
    remove_wav(SOUND_WAVE)

    sample_rate = get_lower_sample_rate(movie.sample_late, sound.sample_late)

    movie.to_wave_with_subsampling(sample_rate)
    sound.to_wave_with_subsampling(sample_rate)

    data1, data2 = read_and_tidy_up_data_for_calculation(movie.data, sound.data)

    movie_length_sec = len(data1) / sample_rate

    corr = sig.correlate(data1, data2, "full")
    output_waveform2(corr)

    time_lag_sec = (len(data1) - corr.argmax()) / sample_rate
    time_lag_sec = round(time_lag_sec, 2)

    display_time_lag_sec(time_lag_sec)

    remove_wav(MOVIE_WAVE)
    remove_wav(SOUND_WAVE)

    return time_lag_sec, movie_length_sec


# calculate_time_lag_sec用。filenameで指定したファイルの存在を確認して削除
def remove_wav(filename):
    if os.path.exists(filename):
        os.remove(filename)


# calculate_time_lag_sec用。ダウンサンプリングのため，２つのファイルのうち，低い方のサンプリング周波数の値を返す。
def get_lower_sample_rate(m_rate, s_rate):
    if m_rate < s_rate:
        sample_rate = m_rate
    else:
        sample_rate = s_rate

    return sample_rate


# calculate_time_lag_sec用。データを読み込んで計算用に整形
def read_and_tidy_up_data_for_calculation(movie_data, sound_data):
    # 2データの長さを揃える
    if len(movie_data) < len(sound_data):
        sound_data = sound_data[:len(movie_data)]
    elif len(movie_data) > len(sound_data):
        movie_data = movie_data[:len(sound_data)]

    # 相互相関関数の計算に影響が出る可能性があるため，平均を0に
    data1 = movie_data - movie_data.mean()
    data2 = sound_data - sound_data.mean()

    return data1, data2


# calculate_time_lag_sec用。時間差を画面表示
def display_time_lag_sec(time_lag_sec):
    if time_lag_sec > 0:
        print("音声は映像より" + str(time_lag_sec) + "秒遅れています。")
    elif time_lag_sec < 0:
        print("音声は映像より" + str(time_lag_sec * -1) + "秒進んでいます")
    else:
        print("映像と音声の間に時間差はありません。")


def output_waveform(data1, data2):
    plt.plot(data1, label="data1")
    plt.plot(data2, label="data2")
    plt.title("WAVE")
    plt.xlabel(' data num ')
    plt.ylabel(' Amplitude ')
    plt.legend()
    plt.show()


def output_waveform2(data):
    plt.figure(figsize=(7, 4))
    # plt.get_xaxis().get_major_formatter().set_scientific(False)
    plt.plot(data, color='black')
    plt.xlabel(' data num ')
    plt.ylabel(' amplitude ')
    plt.show()
