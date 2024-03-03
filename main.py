import math
import time
import sys
import threading
import subprocess
from win11toast import notify, update_progress, toast
from datetime import datetime
import os
import records

activities = ["冥想", "阅读", "探索", "工作", "娱乐"]


# ANSI颜色转义码
class Colors:
    RED = '\033[31m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BLACK = '\033[30m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    END = '\033[0m'


color1 = ''
color2 = Colors.GREEN
color3 = Colors.BLUE
color4 = Colors.YELLOW


def formatting_time(hours, minutes, seconds):
    total_string = ""
    if hours != 0:
        total_string += f' {hours} 时'
    if minutes != 0:
        total_string += f' {minutes} 分'
    if seconds != 0:
        total_string += f' {seconds} 秒'
    if hours == 0 and minutes == 0 and seconds == 0:
        total_string = ' 0'
    return total_string


def print_progress_bar(iteration, total, prefix='', suffix='', length=30, fill='-'):
    # percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '█' * (length - filled_length)
    iteration = total - iteration
    hours = iteration // 3600
    minutes = (iteration % 3600) // 60
    seconds = iteration % 60
    time_left = "剩余" + color2 + f'{formatting_time(hours, minutes, seconds)}' + Colors.END
    sys.stdout.write(f'\r{prefix} |{bar}| {suffix} / ' + time_left)
    sys.stdout.flush()


class DailyTasksManager:

    def __init__(self):
        # 获取当前日期和时间
        current_datetime = datetime.now()

        # 从当前日期和时间中提取日期部分
        self.current_date = current_datetime.date()
        print(self.current_date)

        self.activities = {
            1: {"name": "冥想", "duration": 30 * 60},
            2: {"name": "阅读", "duration": 30 * 60},
            3: {"name": "探索", "duration": 1 * 60 * 60},
            4: {"name": "工作", "duration": 6 * 60 * 60},
            5: {"name": "娱乐", "duration": 2 * 60 * 60}
        }

        self.remaining_times = {activity: activity_info["duration"] for activity, activity_info in
                                self.activities.items()}
        self.plan_times = {activity: activity_info["duration"] for activity, activity_info in
                           self.activities.items()}
        self.read_plan()
        self.stop_timer = False  # 计时停止标志

    def set_activities_time(self, values):
        for i, t in enumerate(values):
            self.plan_times[i + 1] = int(t) * 60
            self.remaining_times[i + 1] = int(t) * 60

    def update_remaining_time(self, activity, elapsed_time):
        if activity in self.remaining_times:
            self.remaining_times[activity] -= elapsed_time

    def get_remaining_time(self, activity):
        remaining_seconds = self.remaining_times.get(activity, 0)
        a = 1
        if remaining_seconds < 0:
            remaining_seconds = -remaining_seconds
            a = -1
        hours = remaining_seconds // 3600 * a
        minutes = (remaining_seconds % 3600) // 60 * a
        seconds = remaining_seconds % 60 * a
        return hours, minutes, seconds

    def get_plan_time(self, activity):
        plan_seconds = self.plan_times.get(activity, 0)
        hours = plan_seconds // 3600
        minutes = (plan_seconds % 3600) // 60
        seconds = plan_seconds % 60
        return hours, minutes, seconds

    def get_activity_name(self, activity):
        return self.activities.get(activity, {}).get("name", "未知活动")

    def save_plan(self):
        # 读取并保留第15行及之后的内容
        after_text = ""
        try:
            with open(fr'F:\OneDriveWH\OneDrive - whu.edu.cn\TIME\{self.current_date}.txt', 'r') as file:
                # 逐行读取文件内容
                for i, line in enumerate(file):
                    if i > 14:
                        after_text += line
        except FileNotFoundError:
            after_text = ""
        # 打开文件以写入模式
        with open(fr'F:\OneDriveWH\OneDrive - whu.edu.cn\TIME\{self.current_date}.txt', 'w') as file:
            file.write(str(self.current_date) + '\n')
            file.write('1冥想 2阅读 3探索 4工作 5娱乐' + '\n')
            file.write('A: PLANED\n')
            for i in range(5):
                ptime = self.plan_times.get(i + 1, 0)
                file.write(str(ptime) + '\n')
            file.write('B: REMAIN\n')
            for i in range(5):
                ptime = self.remaining_times.get(i + 1, 0)
                file.write(str(ptime) + '\n')
            file.write('C: DAIRY\n')
            file.write(after_text)

    def read_plan(self):
        # 打开文件以读取模式
        try:
            with open(fr'F:\OneDriveWH\OneDrive - whu.edu.cn\TIME\{self.current_date}.txt', 'r') as file:
                # 逐行读取文件内容
                times = []
                for i, line in enumerate(file):
                    if 2 < i < 14 and i != 8:
                        times.append(int(line.strip()))
                for i, t in enumerate(times):
                    if i < 5:
                        self.plan_times[i + 1] = int(t)
                    else:
                        self.remaining_times[i - 4] = int(t)
        except FileNotFoundError:
            try:
                with open(fr'F:\OneDriveWH\OneDrive - whu.edu.cn\TIME\plan.txt', 'r') as file:
                    # 逐行读取文件内容
                    times = []
                    for i, line in enumerate(file):
                        if i > 2:
                            times.append(int(line.strip()))
                    for i, t in enumerate(times):
                        if i < 5:
                            self.plan_times[i + 1] = int(t) * 60
                            self.remaining_times[i + 1] = int(t) * 60
            except FileNotFoundError:
                self.plan_times = {activity: activity_info["duration"] for activity, activity_info in
                                   self.activities.items()}
                self.remaining_times = {activity: activity_info["duration"] for activity, activity_info in
                                        self.activities.items()}
            self.save_plan()

    def print_plan(self):
        for activity, remaining_time in self.remaining_times.items():
            activity_name = self.get_activity_name(activity)
            hours1, minutes1, seconds1 = self.get_remaining_time(activity)
            hours2, minutes2, seconds2 = self.get_plan_time(activity)
            print(
                f"{activity_name}：" + color3 + formatting_time(hours1, minutes1, seconds1) + Colors.END +
                "  / " + formatting_time(hours2, minutes2, seconds2))

    def statistic(self):
        pass

def timer_thread(manager, custom_time, selected_activity):
    total_time = custom_time
    total_iterations = total_time

    notify(progress={
        'title': '正在' + activities[selected_activity - 1] + '...',
        'status': '共 ' + str(int(total_time / 60)) + ' 分',
        'value': 1,
        'valueStringOverride': '0/' + str(custom_time) + 'min',
    })
    while custom_time > 0 and not manager.stop_timer:
        if custom_time // 3600 != 0:
            override_string = f"剩余 {custom_time // 3600} 时"
        else:
            override_string = '剩余'
        if custom_time % 3600 // 60 != 0:
            override_string += f" {custom_time % 3600 // 60} 分"
        if custom_time % 60 != 0:
            override_string += f" {custom_time % 60} 秒"
        print_progress_bar(total_time - custom_time, total_iterations,
                           prefix='正在' + activities[selected_activity - 1] + '...',
                           suffix='共 ' + color1 + str(int(total_time / 60)) + ' 分' + Colors.END,
                           length=min(int(math.ceil(total_time / 50)), 60))
        update_progress({'value': custom_time / total_time,
                         'valueStringOverride': override_string})
        time.sleep(1)  # 等待1秒钟
        custom_time -= 1
        manager.update_remaining_time(selected_activity, 1)

        manager.save_plan()
    else:
        # 输出选择的活动剩余时间
        activity_name = manager.get_activity_name(selected_activity)
        hours, minutes, seconds = manager.get_remaining_time(selected_activity)
        current_time = datetime.now()
        plan_left = color3 + formatting_time(hours, minutes, seconds) + Colors.END
        formatted_time = "   ------   " + color4 + current_time.strftime("%H : %M") + Colors.END
        total_string = f"\n{activity_name}计划剩余：" + plan_left + formatted_time
        print(total_string)

        def empty_func(args):
            pass

        update_progress({'status': f'已完成{activity_name}!'})
        if not manager.stop_timer:
            toast(f'已完成{activity_name}!',
                  f"{activity_name}计划剩余：" + formatting_time(hours, minutes, seconds),
                  audio='ms-winsoundevent:Notification.Looping.Alarm3', on_dismissed=empty_func,
                  duration='short'
                  )


if __name__ == "__main__":
    manager = DailyTasksManager()

    manager.print_plan()

    while True:
        # 询问用户选择的活动种类
        try:
            selected_activity = int(input("\n选择活动（0:计划 1:冥想 2:阅读 3:探索 4:工作 5:娱乐 6:设置 7:日志 8:统计）: "))

            if selected_activity == 6:
                os.system("notepad.exe {}".format(fr'F:\OneDriveWH\OneDrive - whu.edu.cn\TIME\plan.txt'))
                continue
            elif selected_activity == 0:
                manager.print_plan()
                continue
            elif selected_activity == 7:
                file_path = fr'F:\OneDriveWH\OneDrive - whu.edu.cn\TIME\{manager.current_date}.txt'
                subprocess.Popen(["notepad.exe", file_path])
                continue
            elif selected_activity == 8:
                records.main()
                continue
            custom_time = int(input("专注时长（分钟）: "))

        except ValueError:
            print("请输入有效的选择和计时时长！")
            continue

        # 检查选择的活动是否有效
        if selected_activity in manager.activities:
            # 创建计时线程
            timer_thread_instance = threading.Thread(target=timer_thread,
                                                     args=(manager, custom_time * 60, selected_activity))
            timer_thread_instance.start()

            # 等待用户输入's'停止计时
            while True:
                catch = input()
                if catch == '7':
                    file_path = fr'F:\OneDriveWH\OneDrive - whu.edu.cn\TIME\{manager.current_date}.txt'
                    subprocess.Popen(["notepad.exe", file_path])
                    sys.stdout.write('\x1b[1A')  # 光标上移一行
                    sys.stdout.write('\x1b[2K')  # 清除光标所在行
                else:

                    break

            manager.stop_timer = True  # 设置停止计时标志
            timer_thread_instance.join()  # 等待计时线程结束
            manager.stop_timer = False  # 重置停止计时标志
        else:
            print("无效的活动选择！")
