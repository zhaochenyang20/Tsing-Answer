from tqdm import tqdm
from collections import Counter, OrderedDict
import csv
import json
from pathlib import Path
import os

def compare_volunteer(volunteer):
    """为 department 里比较每个系最积极的志愿者做的比较器"""
    volunteer.set_total_order_count()
    return volunteer.total_order_count

def compare_student(student):
    """为 department 里比较每个系最积极的学生做的比较器"""

    student.set_total_order_count()
    return student.total_order_count

class Department:
    """每个院系，存下这个院系的所有学生"""
    """volunteer 为这个系的志愿者，而 helper 为帮助过这个系的学生的志愿者"""

    def __init__(self, department_name, student_list, volunteer_list, helper_list, order_list):
        self.name = department_name
        self.total_order_count = 0
        self.total_student_count = 0
        self.total_helper_count = 0
        self.total_volunteer_count = 0
        self.student_list = student_list
        self.volunteer_list = volunteer_list
        self.helper_list = helper_list
        self.order_list = order_list

    def append_student(self, student):
        self.student_list.append(student)

    def append_order(self, order):
        self.order_list.append(order)

    def append_volunteer(self, volunteer):
        self.volunteer_list.append(volunteer)

    def append_helper(self, helper):
        self.helper_list.append(helper)

    def set_total_student_count(self):
        try:
            assert self.student_list
            self.total_student_count = len(self.student_list)
        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")

    def set_total_volunteer_count(self):
        try:
            assert self.volunteer_list
            self.total_volunteer_count = len(self.volunteer_list)
        except Exception as e:
            print(self.name + f" 没有志愿者")

    def set_total_order_count(self):
        try:
            assert self.order_list
            self.total_order_count = len(self.order_list)
        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")

    def set_total_helper_count(self):
        try:
            assert self.helper_list
            self.total_helper_count = len(self.helper_list)
        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")

    def analysis_specific_department_course(self):
        """学生问过的问题次数，集中的学科"""
        """返回 store_dict 用以生成所有院系的课程分析"""

        try:
            assert self.order_list
            course_dict = Counter()
            for each in self.order_list:
                course_dict[f"{each.course}"] += 1

            course_list = course_dict.most_common()
            store_dict = OrderedDict()
            store_dict["department"] = self.name
            store_dict["total_student_count"] = self.total_student_count
            store_dict["total_order_count"] = self.total_order_count
            store_dict["all_course"] = course_list

            path = Path.cwd() / 'result_department_course'
            if not path.is_dir():
                os.makedirs(path)

            with open(f"{path}/{self.name}.json", "w+", encoding="utf-8", errors="ignore") as f:
                json.dump(store_dict, f, ensure_ascii=False, indent=2)

            return store_dict

        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")

    def analysis_specific_department_student(self):
        """统计该系所有学生的问答情况"""
        """返回 store_dict 用以生成所有院系的学生分析"""

        try:
            store_dict = OrderedDict()
            assert len(self.student_list) != 0

            self.student_list.sort(key=compare_student)
            self.student_list.reverse()
            neo_student_list = []

            for each in self.student_list:
                pair = (each.name, each.total_order_count)
                neo_student_list.append(pair)

            store_dict["department"] = self.name
            store_dict["student_list"] = neo_student_list

            path = Path.cwd() / 'result_department_student'
            if not path.is_dir():
                os.makedirs(path)
            with open(f"{path}/{self.name}.json", "w+", encoding="utf-8", errors="ignore") as f:
                json.dump(store_dict, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")

    def analysis_specific_department_helper(self):
        """帮助该系的志愿者"""
        """返回 store_dict 用以生成所有院系的 helper 分析"""

        try:
            assert self.helper_list
            self.helper_list.sort(key=compare_volunteer)
            self.helper_list.reverse()

            neo_helper_list = []
            store_dict = OrderedDict()

            for each in self.helper_list:
                pair = (each.name, each.total_order_count)
                neo_helper_list.append(pair)

            store_dict["department"] = self.name
            store_dict["helper"] = neo_helper_list

            path = Path.cwd() / 'result_department_helper'
            if not path.is_dir():
                os.makedirs(path)

            with open(f"{path}/{self.name}.json", "w+", encoding="utf-8", errors="ignore") as f:
                json.dump(store_dict, f, ensure_ascii=False, indent=2)
                return store_dict

        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")

    def analysis_specific_department_volunteer(self):
        """该系的志愿者"""
        """返回 store_dict 用以生成所有院系的志愿者分析"""

        try:
            assert self.volunteer_list
            self.volunteer_list.sort(key=compare_volunteer)
            self.volunteer_list.reverse()

            neo_volunteer_list = []
            store_dict = OrderedDict()

            for each in self.volunteer_list:
                pair = (each.name, each.total_order_count)
                neo_volunteer_list.append(pair)

            store_dict["department"] = self.name
            store_dict["volunteer"] = neo_volunteer_list

            path = Path.cwd() / 'result_department_volunteer'
            if not path.is_dir():
                os.makedirs(path)


            return store_dict

        except Exception as e:
            print(e)
        print(self.name + f"{__name__} error")

    def report(self, format="json"):
        try:
            assert self.order_list
            self.set_total_order_count()
            assert self.student_list
            self.set_total_student_count()
            assert self.helper_list
            self.set_total_helper_count()
            assert self.volunteer_list
            self.set_total_volunteer_count()
            store_dict = {}

            store_dict["student"] = self.analysis_specific_department_student()
            store_dict["course"] = self.analysis_specific_department_course()
            store_dict["helper"] = self.analysis_specific_department_helper()
            store_dict["volunteer"] = self.analysis_specific_department_volunteer()

            if format == "json":
                path = Path.cwd() / "department_json"
                if not path.is_dir():
                    os.makedirs(path)
                with open(f"{path}/{self.name}.json", "w+", encoding="utf-8", errors="ignore") as f:
                    json.dump(store_dict, f, ensure_ascii=False, indent=2)

            elif format == "csv":
                path = Path.cwd() / 'department_json'
                if not path.is_dir():
                    os.makedirs(path)
                with open(f"{path}/{self.name}.csv", "w+", encoding="utf-8", errors="ignore") as f:
                    writer = csv.DictWriter(f, fieldnames=list(store_dict.keys()))
                    writer.writeheader()
                    writer.writerow(store_dict)

        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")