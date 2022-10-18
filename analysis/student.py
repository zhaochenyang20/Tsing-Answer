from collections import Counter, OrderedDict
import json
from pathlib import Path
import os

class Student:
    """每个学生建立一个对象，且存下每个学生问过的问题"""
    """名字，院系，所有的订单，所有订单数目，提问总时长，question_list:学生所问过问题所述科目的次数排序"""

    def __init__(self, name, department):
        self.name = name
        self.department = department
        self.total_order_count = 0
        self.duration = 0
        self.order_list = []
        self.question_list = []
        """一个学生提问的学科次数按照倒序排列"""

    def append_order(self, order):
        self.order_list.append(order)

    def set_total_order_count(self):
        try:
            assert self.order_list
            self.total_order_count = len(self.order_list)
        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")

    def set_question_list(self):
        try:
            assert self.order_list
            question_dic = Counter()
            for each in self.order_list:
                question_dic[f"{each.course}"] += 1
            self.question_list = question_dic.most_common()
        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")

    def set_duration(self):
        try:
            assert self.order_list
            total_time = 0
            for each in self.order_list:
                try:
                    # from IPython import embed
                    # embed()
                    print(each.feedback_dic["period"])
                    if each.feedback_dic["period"] == "realName":
                        from IPython import embed
                        embed.embed()
                    total_time += each.feedback_dic["period"]
                except:
                    continue
            self.duration = total_time
        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")

    def report(self, report_json=True):
        """"统计每个学生提出的问题所属的学科，提问的总时间与总次数"""
        """将需要保存的 dict 返回给主函数，用于写入所有用户的 CSV"""

        try:
            assert self.order_list
            self.set_question_list()
            self.set_duration()
            self.set_total_order_count()

            path = Path.cwd() / 'result_student'
            if not path.is_dir():
                os.makedirs(path)

            store_dict = OrderedDict()
            store_dict["name"] = self.name
            store_dict["department"] = self.department
            store_dict["duration"] = self.duration
            store_dict["course"] = self.question_list
            store_dict["total_order_count"] = self.total_order_count

            if report_json:
                with open(f"{path}/{self.name}.json", "w+", encoding="utf-8", errors="ignore") as f:
                    json.dump(store_dict, f, ensure_ascii=False, indent=2)

            return store_dict

        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")







