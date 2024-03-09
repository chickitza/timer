from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
import os

# matplotlib.use('Qt5Agg')  # 使用PySide6


class Record:
    def __init__(self, date_string) -> None:
        self.date = datetime.strptime(date_string, "%Y-%m-%d")
        self.date = date_string

        self.plan_times = [0] * 5
        remaining_times = [0] * 5
        self.used_times = [0] * 5
        with open(fr'F:\OneDriveWH\OneDrive - whu.edu.cn\TIME\{date_string}.txt', 'r') as file:
            # 逐行读取文件内容
            times = []
            for i, line in enumerate(file):
                if 2 < i < 14 and i != 8:
                    times.append(int(line.strip()))
            for i, t in enumerate(times):
                if i < 5:
                    self.plan_times[i] = int(t) / 3600
                else:
                    remaining_times[i - 5] = int(t) / 3600
                    self.used_times[i - 5] = self.plan_times[i - 5] - remaining_times[i - 5]


class Records:
    def __init__(self) -> None:
        self.records: list[Record] = []
        self.dates = []
        self.useds = [[] for _ in range(5)]
        self.plans = [[] for _ in range(5)]

    def add_record(self, date_string):
        new_record = Record(date_string)
        self.records.append(new_record)


class RecordsManager:
    def __init__(self) -> None:
        # 定义要遍历的文件夹路径
        self.folder_path = 'F:\OneDriveWH\OneDrive - whu.edu.cn\TIME'
        self.records = Records()

    def read_records(self):
        # 遍历文件夹
        date_list = []

        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if file.endswith(".txt"):
                    # 构造完整的文件路径
                    full_path = os.path.join(root, file)
                    # 对每个txt文件的处理逻辑

                    file_string = full_path.split('\\')[-1]
                    date_string = file_string.split('.')[0]

                    try:
                        date_object = datetime.strptime(date_string, "%Y-%m-%d")
                        date_list.append(date_string)
                    except:
                        pass

        for date_string in date_list:
            self.records.add_record(date_string)

    def statistic_record(self):
        for record in self.records.records:
            self.records.dates.append(record.date)
            for i in range(5):
                self.records.useds[i].append(record.used_times[i])
                self.records.plans[i].append(record.plan_times[i])

    def draw_items(self):
        for i in range(5):
            # 创建图形和轴
            item = i + 1
            fig, ax1 = plt.subplots()

            dates = self.records.dates

            plans = self.records.plans[item - 1]

            useds = self.records.useds[item - 1]

            # 绘制第一组数据
            color = 'tab:blue'
            ax1.set_xlabel('日期')
            ax1.set_ylabel('计划(h)', color=color)
            ax1.bar(dates, plans, width=0.4, color=color)
            ax1.tick_params(axis='y', labelcolor=color)

            # 设置x轴刻度标签并旋转45度
            ax1.set_xticks(dates)
            ax1.set_xticklabels(dates, rotation=45, ha="right")  # ha="right" 使得标签稍微倾斜，看起来更美观

            # 创建共享x轴的第二个y轴
            ax2 = ax1.twinx()
            color = 'tab:red'
            ax2.set_ylabel('使用(h)', color=color)

            ax2.bar(dates, useds, width=0.4, color=color)
            ax2.tick_params(axis='y', labelcolor=color)

            if item == 1:
                plt.title('冥想时间统计')
            elif item == 2:
                plt.title('阅读时间统计')
            elif item == 3:
                plt.title('探索时间统计')
            elif item == 4:
                plt.title('工作时间统计')
            elif item == 5:
                plt.title('娱乐时间统计')

            # 手动设置两个y轴的刻度范围
            y_min = min(min(plans), min(useds))
            y_max = max(max(plans), max(useds))

            ax1.set_ylim(y_min, y_max)
            ax2.set_ylim(y_min, y_max)

            plt.get_current_fig_manager().window.setGeometry((4 - i) * 250, 30 + i * 100, 500, 380)

        plt.show()


# Define the entry point function
def main():
    # 设置中文字体
    matplotlib.rc('font', family='SimHei', weight='bold')
    recordsManager = RecordsManager()
    recordsManager.read_records()
    recordsManager.statistic_record()
    recordsManager.draw_items()


# Check if this script is the entry point
if __name__ == "__main__":
    main()
