# coding: utf-8

import os
import sys

import media as md
import sensor_data as sd

MAKE = "-m"
TRIM = "-t"
CHANGE_SIGN = "-s"
MOVING_AVERAGE_FILTER = "-f"


def main():
    mode = sys.argv[1]

    if mode == MAKE:
        movie_file = input_filename("Input movie file name. > ")
        sound_file = input_filename("Input sound file name. > ")
        accel_file = input_filename("Input accel file name. > ")

        movie = md.Movie(movie_file)
        sound = md.Sound(sound_file)
        accel = sd.SensorData(accel_file)

        begin_sec = get_trim_begin_sec()
        end_sec = get_trim_end_sec()

        time_lag_sec, movie_length_sec = md.calculate_time_lag_sec(movie, sound)

        accel.trim_data(begin_sec + time_lag_sec, end_sec + time_lag_sec)
        accel.output_to_file()

        movie.trim_movie(begin_sec, end_sec)

    elif mode == TRIM:
        # movie_file = input_filename("Input movie file name. > ")
        accel_file = input_filename("Input accel file name. > ")

        begin_sec = get_trim_begin_sec()
        end_sec = get_trim_end_sec()

        accel = sd.SensorData(accel_file)
        accel.trim_data(begin_sec, end_sec)
        accel.output_to_file()

        # movie = md.Movie(movie_file)
        # movie.trim_movie(begin_sec, end_sec)

    elif mode == CHANGE_SIGN:
        accel_file = input_filename("Input accel file name. > ")
        data = sd.SensorData(accel_file)
        data.change_sign(True, False, True)
        data.output_to_file()

    elif mode == MOVING_AVERAGE_FILTER:
        accel_file = input_filename("Input accel file name. > ")
        data = sd.SensorData(accel_file)
        data.moving_average_filter()
        data.output_to_file()

    else:
        accel_file = input_filename("Input accel file name. > ")
        accel = sd.SensorData(accel_file)
        accel.plot_data()


# ファイル名を取得，存在するファイル名を入力するまで聞き返す
def input_filename(sentence_to_display):
    while True:
        filename = input(sentence_to_display)
        if os.path.exists(filename):
            break
        else:
            print("入力した名前のファイルは存在しません。")
            print("もう一度入力してください。")

    return filename


# トリミングの開始点を入力
def get_trim_begin_sec():
    trim_begin_sec = input_trim_time_sec("動画の開始地点[秒] = ")
    return trim_begin_sec


# トリミングで切り出したい長さを入力
def get_trim_end_sec():
    trim_length_sec = input_trim_time_sec("動画の終了時間[秒] = ")
    return trim_length_sec


# get_trim_time_sec用。数値が入力されるまでループ
def input_trim_time_sec(sentence_to_display):
    while True:
        try:
            input_string = float(input(sentence_to_display))
        except ValueError:
            print("入力が正しくありません。数値を入力してください")
        else:
            if input_string < 0:
                print("入力が正しくありません。0以上の数値を入力してください")
            else:
                return input_string


# 指定されたbegin_secからlength_sec分のセンサデータを切り出し
def trim_sensor_data(accel_file, begin_sec, end_sec):
    data = sd.SensorData(accel_file)
    data.edit_trim(begin_sec, end_sec)
    data.output_to_file()


if __name__ == '__main__':
    main()