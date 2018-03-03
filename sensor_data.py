import numpy as np

class sensor_data:
    # --- メンバ変数一覧 ---
    # filename:センサデータのファイル名
    # header: センサデータの1行目
    # col_time: 時間（一番左の列）
    # col_x: x軸 （2番目の列）
    # col_y: y軸 （4番目の列）
    # col_z: z軸 （3番目の列）

    # --- メソッド一覧 ---
    # __init__
    # edit_sign
    # static change_sign_of_list
    # edit_filter
    # static moving_average_filter
    # edit_trim
    # static to_millisecond
    # output_to_file

    # 引数として与えられた名前のセンサデータファイルを読み込む
    def __init__(self, input_filename):
        self.filename = input_filename
        self.col_time, self.col_x, self.col_y, self.col_z = [], [], [], []

        in_file = open(self.filename, "r")

        self.header = in_file.readline()
        # windowsの改行コードに変更
        self.header.replace("\n" or "\r", "\r\n")

        lines = in_file.readlines()

        for line in lines:
            line = line.replace("\n" or "\r", "")
            line = line.split(",")
            self.col_time.append(int(line[0]))
            self.col_x.append(float(line[1]))
            self.col_z.append(float(line[2]))
            self.col_y.append(float(line[3]))

    # 指定された軸の符号を変更
    def edit_sign(self, x, y, z):
        if x:
            self.col_x = sensor_data.change_sign_of_list(self.col_x)
        if y:
            self.col_y = sensor_data.change_sign_of_list(self.col_y)
        if z:
            self.col_z = sensor_data.change_sign_of_list(self.col_z)

    # 受け取った1次元配列の符号を反転する
    @staticmethod
    def change_sign_of_list(column):
        for i in range(len(column)):
            column[i] *= -1
        return column

    # センサ全体に移動平均フィルタをかける
    def edit_filter(self):
        self.col_x = sensor_data.moving_average_filter(self.col_x)
        self.col_y = sensor_data.moving_average_filter(self.col_y)
        self.col_z = sensor_data.moving_average_filter(self.col_z)

    # 受け取った1次元配列に移動平均フィルタをかける
    @staticmethod
    def moving_average_filter(column):
        N = 9
        data = np.array(column)
        ave = np.convolve(data, np.ones(N) / float(N), 'same')
        for i in range(len(ave)):
            ave[i] = round(ave[i], 4)
        return ave

    # 指定した時間でセンサデータをトリミング
    def edit_trim(self, begin_sec, end_sec):
        begin_ms, end_ms = sensor_data.to_millisecond(begin_sec), sensor_data.to_millisecond(end_sec)
        new_col_time, new_col_x, new_col_y, new_col_z = [], [], [], []

        for i in range(len(self.col_time)):
            if begin_ms <= self.col_time[i] <= end_ms:
                new_col_time.append(int(self.col_time[i] - begin_ms))
                new_col_x.append(float(self.col_x[i]))
                new_col_y.append(float(self.col_y[i]))
                new_col_z.append(float(self.col_z[i]))

        self.col_time = new_col_time
        self.col_x = new_col_x
        self.col_y = new_col_y
        self.col_z = new_col_z

    # 入力された秒数をミリ秒にして返す
    @staticmethod
    def to_millisecond(sec):
        return sec * 1000

    # センサデータをファイルに書き出す
    def output_to_file(self):
        out_file = open("edited_" + self.filename, "w")

        out_file.write(self.header)
        for i in range(len(self.col_time)):
            row = "{},{},{},{}\r\n".format(
                self.col_time[i],
                self.col_x[i],
                self.col_z[i],
                self.col_y[i]
            )
            out_file.write(row)
