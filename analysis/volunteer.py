from tqdm import tqdm
from collections import Counter, OrderedDict
import json
from pathlib import Path
import os

class Volunteer:
    """志愿者"""

    def __init__(self, name, department):
        self.name = name
        self.department = department
        self.order_list = []
        self.duration = 0
        self.total_order_count = 0
        self.average_satisfaction = 0
        self.order_count_list = []

    def append_order(self, order):
        self.order_list.append(order)

    def evaluate_average_satisfaction(self):
        """feedback_dic 一个 key 打错了，satisfication，回头改一下"""

        try:
            total_satisfaction = 0
            bias = 0
            assert self.order_list
            for each in self.order_list:
                try:
                    total_satisfaction += each.feedback_dic["ability"] + each.feedback_dic["attitude"] + each.feedback_dic["inspiration"] + each.feedback_dic["satisfication"]
                except:
                    bias += 1
                    continue
        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")
        else:
            self.average_satisfaction = total_satisfaction / (len(self.order_list) - bias)


    def set_total_duration(self):
        try:
            total_duration = 0
            assert self.order_list
        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")
        else:
            for each in self.order_list:
                total_duration += each.feedback_dic["period"]
            self.duration = total_duration

    def set_total_order_count(self):
        try:
            order_dict = Counter()
            assert self.order_list
            self.total_order_count = len(self.order_list)
            for each in self.order_list:
                order_dict[f"{each.course}"] += 1
            self.order_count_list = order_dict.most_common()
        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")

    def report(self, report_json=True):
        """将需要保存的 dict 返回给主函数，用于写入所有志愿者的 CSV"""

        try:
            assert self.order_list
            self.evaluate_average_satisfaction()
            self.set_total_duration()
            self.set_total_order_count()

            path = Path.cwd() / 'volunteer'
            if not path.is_dir():
                os.makedirs(path)

            store_dict = OrderedDict()
            store_dict["name"] = self.name
            store_dict["department"] = self.department
            store_dict["duration"] = self.duration
            store_dict["total_order_count"] = self.total_order_count
            store_dict["average_satisfaction"] = self.average_satisfaction
            store_dict["order_count_list"] = self.order_count_list

            if report_json:
                with open(f"{path}/{self.name}.json", "w+", encoding="utf-8", errors="ignore") as f:
                    json.dump(store_dict, f, ensure_ascii=False, indent=2)

            return store_dict

        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")





