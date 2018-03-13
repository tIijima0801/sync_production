import numpy as np
import matplotlib.pyplot as plt

class SensorData:
    # --- メンバ変数一覧 ---
    filename = []
    header = []
    column_time = []
    column_x = []
    column_y = []
    column_z = []

    # --- メソッド一覧 ---
    # __init__
    # change_sign
    # edit_filter
    # static moving_average_filter
    # edit_trim
    # static to_millisecond
    # output_to_file

    # 引数として与えられた名前のセンサデータファイルを読み込む
    def __init__(self, input_filename):
        time = []
        x = []
        y = []
        z = []

        self.filename = input_filename
        in_file = open(self.filename, "r")

        self.header = in_file.readline()
        self.header = self.header.replace("\n" or "\r", "")

        lines = in_file.readlines()
        for line in lines:
            line = line.replace("\n" or "\r", "")
            line = line.split(",")
            time.append(int(line[0]))
            x.append(float(line[1]))
            y.append(float(line[3]))
            z.append(float(line[2]))

        self.column_time = np.array(time, dtype=int)
        self.column_x = np.array(x, dtype=float)
        self.column_y = np.array(y, dtype=float)
        self.column_z = np.array(z, dtype=float)

    # 指定された軸の符号を変更
    def change_sign(self, x_bool, y_bool, z_bool):
        if x_bool:
            self.column_x *= -1
        if y_bool:
            self.column_y *= -1
        if z_bool:
            self.column_z *= -1

    # センサ全体に移動平均フィルタをかける
    def moving_average_filter(self):
        self.column_x = SensorData.moving_average_filter_list(self.column_x)
        self.column_y = SensorData.moving_average_filter_list(self.column_y)
        self.column_z = SensorData.moving_average_filter_list(self.column_z)

    # 受け取った1次元配列に移動平均フィルタをかける
    @staticmethod
    def moving_average_filter_list(column):
        n = 20
        ave = np.convolve(column, np.ones(n) / float(n), 'same')
        for i in range(len(ave)):
            ave[i] = round(ave[i], 4)
        return ave

    # 指定した時間でセンサデータをトリミング
    def trim_data(self, begin_sec, end_sec):
        begin_ms, end_ms = SensorData.to_millisecond(begin_sec), SensorData.to_millisecond(end_sec)
        new_column_time = np.array([], dtype=int)
        new_column_x = new_column_y = new_column_z = np.array([], dtype=float)

        for i in range(len(self.column_time)):
            if begin_ms <= self.column_time[i] <= end_ms:
                new_column_time = np.append(new_column_time, self.column_time[i] - int(begin_ms))
                new_column_x = np.append(new_column_x, self.column_x[i])
                new_column_y = np.append(new_column_y, self.column_y[i])
                new_column_z = np.append(new_column_z, self.column_z[i])
            elif self.column_time[i] > end_ms:
                break

        self.column_time = new_column_time
        self.column_x = new_column_x
        self.column_y = new_column_y
        self.column_z = new_column_z

    def plot_data(self):
        plt.figure(figsize=(7, 4))
        plt.plot(self.column_x, color='black')
        plt.xlabel(' data num ')
        plt.ylabel(' amplitude ')
        plt.ylim(-1.5, 1.5)
        # plt.xlim(2000, 3000)
        plt.show()

    # 入力された秒数をミリ秒にして返す
    @staticmethod
    def to_millisecond(sec):
        return sec * 1000

    # センサデータをファイルに書き出す
    def output_to_file(self):
        out_file = open("edited_" + self.filename, "w")

        out_file.write(self.header + "\r\n")
        for i in range(len(self.column_time)):
            row = "{},{},{},{}\r\n".format(
                self.column_time[i],
                self.column_x[i],
                self.column_z[i],
                self.column_y[i]
            )
            out_file.write(row)
