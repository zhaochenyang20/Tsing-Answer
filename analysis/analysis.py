from tqdm import tqdm
import typing
from collections import Counter, OrderedDict
from IPython import embed
import csv
import functools
import time
import json
from pathlib import Path
import os


order_json = "./order.json"


def metric(fn):
    """装饰器显示函数运行的情况和运行时长"""

    @functools.wraps(fn)
    def wrapper(*args, **kw):
        print('start executing %s' % (fn.__name__))
        start_time = time.time()
        result = fn(*args, **kw)
        end_time = time.time()
        t = 1000 * (end_time - start_time)
        print('%s executed in %s ms' % (fn.__name__, t))
        return result
    return wrapper


@metric
def get_department_list():
    """以列表为返回值，获得所有的院系"""

    json_order_list = []
    with open(order_json, "r", encoding="utf-8", errors="ignore") as f:
        for line in f.readlines():
            dic = json.loads(line)
            json_order_list.append(dic)
    department_list = []
    for each in tqdm(json_order_list):
        try:
            department = each["actionRec"]["pAuthenData"]["department"]
            if department not in department_list:
                department_list.append(department)
        except:
            pass
    return department_list


class Order:
    """每个订单建立一个对象，设计如下接口"""
    """课程名字， 学科划分，发出时间，puid，擦亮次数，是否推送到知识库，回答时间，结束时间，auid，反馈，用户，志愿者"""

    def __init__(self, order_dic):
        self.course = order_dic["courseID"]
        self.subject = order_dic["subjectID"]
        self.post_time = order_dic["actionRec"]["ptime"]
        self.puid = order_dic["actionRec"]["puid"]
        try:
            self.hasPush = order_dic["actionRec"]["hasPush"]
        except:
            self.hasPush = False
        try:
            self.polishCount = int(order_dic["actionRec"]["polishCount"])
        except:
            self.polishCount = 0
        try:
            """因为可能未接单，故而这一部分可能不存在"""
            self.atime = order_dic["actionRec"]["atime"]
            self.ftime = order_dic["actionRec"]["ftime"]
            self.auid = order_dic["actionRec"]["auid"]
            self.feedback_dic = order_dic["feedback"]
            """feedback 为一个 dict，表项如下：abilility, attitude, inspiration, period, satisfication, suggestion"""
            self.volunteer_dic = order_dic["actionRec"]["aAuthenData"]
            """authentication, certificateState, department, realName, school, studentID, volunteerLevel"""
            assert self.volunteer_dic["certificateState"] != "未认证"
        except:
            self.atime = 0
            self.ftime = 0
            self.auid = 0
            self.feedback_dic = {}
            self.volunteer_dic = {}

        self.client_dic = order_dic["actionRec"]["pAuthenData"]
        """authentication, certificateState, department, realName, school, studentID"""


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
            for each in tqdm(self.order_list):
                question_dic[f"{each.course}"] += 1
            self.question_list = question_dic.most_common()
        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")

    def set_duration(self):
        try:
            assert self.order_list
            total_time = 0
            for each in tqdm(self.order_list):
                try:
                    total_time += each.feedback_dic["period"]
                except:
                    continue
            self.duration = total_time
        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")

    @metric
    def report(self):
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

            with open(f"{path}/{self.name}.json", "w+", encoding="utf-8", errors="ignore") as f:
                json.dump(store_dict, f, ensure_ascii=False, indent=2)

            return store_dict

        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")



def compare_student(student):
    """为 department 里比较每个系最积极的学生做的比较器"""

    student.set_total_order_count()
    return student.total_order_count

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
            for each in tqdm(self.order_list):
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
            for each in tqdm(self.order_list):
                total_duration += each.feedback_dic["period"]
            self.duration = total_duration

    def set_total_order_count(self):
        try:
            order_dict = Counter()
            assert self.order_list
            self.total_order_count = len(self.order_list)
            for each in tqdm(self.order_list):
                order_dict[f"{each.course}"] += 1
            self.order_count_list = order_dict.most_common()
        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")

    @metric
    def report(self):
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

            with open(f"{path}/{self.name}.json", "w+", encoding="utf-8", errors="ignore") as f:
                json.dump(store_dict, f, ensure_ascii=False, indent=2)

            return store_dict

        except Exception as e:
            print(e)
            print(self.name + f"{__name__} error")


def compare_volunteer(volunteer):
    """为 department 里比较每个系最积极的志愿者做的比较器"""
    volunteer.set_total_order_count()
    return volunteer.total_order_count


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

    @metric
    def analysis_specific_department_course(self):
        """学生问过的问题次数，集中的学科"""
        """返回 store_dict 用以生成所有院系的课程分析"""

        try:
            assert self.order_list
            course_dict = Counter()
            for each in tqdm(self.order_list):
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

    @metric
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


    @metric
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

    @metric
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

    @metric
    def report(self):
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

            path = Path.cwd() / 'department_CSV'
            if not path.is_dir():
                os.makedirs(path)

            name_list = []
            for key in store_dict:
                name_list.append(key)

            with open(f"{path}/{self.name}.csv", "w+", encoding="utf-8", errors="ignore") as f:
                writer = csv.DictWriter(f, fieldnames=name_list)
                writer.writeheader()
                writer.writerow(store_dict)

        except Exception as e:
            print(e)
        print(self.name + f"{__name__} error")

def select_order_this_semister():
    """选择本学期的订单"""
    """返回 order_list"""
    try:
        order_list = []
        json_order_list = []
        total_count = 0
        count = 0
        with open(order_json, "r", encoding="utf-8", errors="ignore") as f:
            for line in f.readlines():
                dic = json.loads(line)
                json_order_list.append(dic)
        try:
            for index, each in tqdm(enumerate(json_order_list)):
            #! 这一段单独筛选了 2022 年 2 月 21 日到 6 月 12 日的订单

                try:
                    time = each["actionRec"]["ptime"]
                    year = time[:4]
                    month = time[5:7]
                    day = time[8:10]
                    date = int(year + month + day)
                    if date < 20220221 or date > 20220612:
                        print(date)
                        count += 1
                        continue
                except Exception as e:
                    continue
                order_list.append(each)
            total_count = len(json_order_list) - count
            with open("./result_order_this_semister.json", "w+", encoding="utf-8", errors="ignore") as f:
                json.dump(order_list, f, ensure_ascii=False, indent=2)
            print(total_count)
            print(count)
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)

def select_order_personally():
    """选择一个人的订单"""
    """返回 order_list"""
    selector = "赵晨阳"
    try:
        order_list = []
        json_order_list = []
        with open(order_json, "r", encoding="utf-8", errors="ignore") as f:
            for line in f.readlines():
                dic = json.loads(line)
                json_order_list.append(dic)
        try:
            for index, each in tqdm(enumerate(json_order_list)):
            #! 这一段单独筛选了某个人的订单
                try:
                    name = each["actionRec"]["pAuthenData"]["realName"]
                    if name == selector:
                        order_list.append(each)
                except Exception as e:
                    continue
            with open(f"./{selector}.json", "w+", encoding="utf-8", errors="ignore") as f:
                json.dump(order_list, f, ensure_ascii=False, indent=2)
            embed()
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)

def initialize():
    """"返回 student list，volunteer list， department list"""
    """这几个 department dict 都是二级词典，一级的 key 为院系，二级的 key 为相应列表项"""

    json_order_list = []
    order_list = []
    department_list = []
    student_list = []
    volunteer_list = []
    student_dic = {}
    volunteer_dic = {}
    department_order_dic = {}
    department_student_dic = {}
    department_volunteer_dic = {}
    department_helper_dic = {}
    department_name_list = get_department_list()

    for each in department_name_list:
        """department_order_dic 是个 dict of list，而其他都是 dict of dict"""

        department_order_dic[f"{each}"] = []
        department_helper_dic[f"{each}"] = {}
        department_volunteer_dic[f"{each}"] = {}
        department_student_dic[f"{each}"] = {}


    try:
        with open(order_json, "r", encoding="utf-8", errors="ignore") as f:
            for line in f.readlines():
                dic = json.loads(line)
                json_order_list.append(dic)


        try:
            for each in tqdm(json_order_list):
            # # ! 这一段是单独筛选了零字班和九字班的学生订单
                # try:
                #     embed()
                #     studentEnrollment = int(str(each["actionRec"]["pAuthenData"]["studentID"])[0:4])
                #     if (studentEnrollment != 2020) and ( studentEnrollment != 2019):
                #         continue
                # except Exception as e:
                #         continue
            #     # ! 这一段是单独筛选了零字班和九字班的学生订单

            #! 这一段单独筛选了 2022 年 2 月 21 日到 6 月 12 日的订单

                try:
                    time = each["actionRec"]["ptime"]
                    year = time[:4]
                    month = time[5:7]
                    day = time[8:10]
                    date = int(year + month + day)
                    if date < 20210221 or date > 20200612:
                        continue
                except Exception as e:
                    continue

            #! 这一段单独筛选了 2022 年 2 月 21 日到 6 月 12 日的订单
                order = Order(each)
                order_list.append(order)
                try:
                    client_name = order.client_dic["realName"]
                except:
                    continue
                client_department = order.client_dic["department"]


                if f"{client_name}" in student_dic:
                    student_dic[f"{client_name}"].append_order(order)
                else:
                    student_dic[f"{client_name}"] = Student(client_name, client_department)
                    student_dic[f"{client_name}"].append_order(order)


                department_order_dic[f"{client_department}"].append(order)

                if f"{client_name}" in department_student_dic[f"{client_department}"]:
                    department_student_dic[f"{client_department}"][f"{client_name}"].append_order(order)
                else:
                    department_student_dic[f"{client_department}"][f"{client_name}"] = Student(client_name, client_department)
                    department_student_dic[f"{client_department}"][f"{client_name}"].append_order(order)


                try:
                    volunteer_name = order.volunteer_dic["realName"]
                    volunteer_department = order.volunteer_dic["department"]
                    if f"{volunteer_name}" in department_volunteer_dic[f"{volunteer_department}"]:
                        department_volunteer_dic[f"{volunteer_department}"][f"{volunteer_name}"].append_order(order)
                    else:
                        department_volunteer_dic[f"{volunteer_department}"][f"{volunteer_name}"] = Volunteer(volunteer_name,
                                                                                                            volunteer_department)
                        department_volunteer_dic[f"{volunteer_department}"][f"{volunteer_name}"].append_order(order)

                    if f"{volunteer_name}" in department_helper_dic[f"{client_department}"]:
                        department_helper_dic[f"{client_department}"][f"{volunteer_name}"].append_order(order)
                    else:
                        department_helper_dic[f"{client_department}"][f"{volunteer_name}"] = Volunteer(volunteer_name,
                                                                                                    volunteer_department)
                        department_helper_dic[f"{client_department}"][f"{volunteer_name}"].append_order(order)

                    if f"{volunteer_name}" in volunteer_dic:
                        volunteer_dic[f"{volunteer_name}"].append_order(order)
                    else:
                        volunteer_dic[f"{volunteer_name}"] = Volunteer(volunteer_name, volunteer_department)
                        volunteer_dic[f"{volunteer_name}"].append_order(order)

                except Exception as e:
                    print(e)
                    pass

        except Exception as e:
                print(e)

        for key in student_dic:
            student_list.append(student_dic[key])

        for key in volunteer_dic:
            volunteer_list.append(volunteer_dic[key])

        for each in tqdm(department_name_list):
            neo_student_list = []
            neo_volunteer_list = []
            neo_helper_list = []
            neo_order_list = department_order_dic[f"{each}"]
            for key in department_student_dic[each]:
                neo_student_list.append(department_student_dic[each][key])
            for key in department_volunteer_dic[each]:
                neo_volunteer_list.append(department_volunteer_dic[each][key])
            for key in department_helper_dic[each]:
                neo_helper_list.append(department_helper_dic[each][key])

            department_list.append(Department(each, neo_student_list, neo_volunteer_list, neo_helper_list, neo_order_list))
        return student_list, volunteer_list, department_list

    except Exception as e:
        print(e)


def write_csv(store_list, file_name):
    """传入一个 list of dict，然后写入 CSV 文件"""

    name_list = []
    for key in store_list[0]:
        name_list.append(key)

    path = Path.cwd() / 'student_volunteer_CSV'
    if not path.is_dir():
        os.makedirs(path)

    with open(f"{path}/{file_name}.csv", "w+", encoding="utf-8", errors="ignore") as f:
        writer = csv.DictWriter(f, fieldnames=name_list)
        writer.writeheader()
        for each in store_list:
            writer.writerow(each)


if __name__ == '__main__':
    """先读取所有的order，加入到 student 和 volunteer 的 order list 里面"""
    """遍历所有的 student helper 和 volunteer，加入到 department 里面"""

    # student_list, volunteer_list, department_list = initialize()
    # store_student = []
    # store_volunteer = []

    # for each in student_list:
    #     store_student.append(each.report())
    # for each in volunteer_list:
    #     store_volunteer.append(each.report())
    # for each in department_list:
    #     each.report()
    # write_csv(store_student, "student")
    # write_csv(store_volunteer, "volunteer")
    # select_order_this_semister()
    select_order_personally()
