from tqdm import tqdm
import csv
import functools
import time
import json
from order import Order
from student import Student
from department import Department
from volunteer import Volunteer

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

def get_department_list(order_json="./order.json"):
    """
    以列表为返回值，获得所有的院系

    实际上，这个接口的返回值基本上是：
    ['未央书院', '药学院', '探微书院', '新雅书院', '自动化系', '土木系', '电机系', '车辆学院', '工物系', '经管学院', \
    '软件学院', '精仪系', '电子系', '机械系', '生命学院', '环境学院', '物理系', '致理书院', '航院', '计算机系', '材料学院', \
    '法学院', '化工系', '工业工程系', '社科学院', '能动系', '建筑学院', '数学系', '外文系', '医学院', '行健书院', '化学系', \
    '水利系', '日新书院', '交叉信息院', '集成电路学院', '清华大学深圳国际研究', '新闻学院', '美术学院', '求真书院', \
    '为先书院', '马克思主义学院', '人文学院']
    """
    json_order_list = []
    with open(order_json, "r", encoding="utf-8", errors="ignore") as f:
        for line in f.readlines():
            dic = json.loads(line)
            json_order_list.append(dic)
    department_list = []
    for each in json_order_list:
        try:
            department = each["actionRec"]["pAuthenData"]["department"]
            if department not in department_list:
                department_list.append(department)
        except:
            pass
    return department_list

def write_csv(store_list, file_path):
    """传入一个 list of dict，然后写入 CSV 文件"""

    name_list = []
    for key in store_list[0]:
        name_list.append(key)

    with open(file_path, "w+", encoding="utf-8", errors="ignore") as f:
        writer = csv.DictWriter(f, fieldnames=name_list)
        writer.writeheader()
        for each in store_list:
            writer.writerow(each)

def initialize(json_file="./order.json"):
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
        json_order_list = slect_all_order(json_file=json_file)
        json_order_list = select_order_during_(20220613, 20220912, json_order_list=json_order_list)
        try:
            for each in json_order_list:
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
                    continue

        except Exception as e:
                pass

        for key in student_dic:
            student_list.append(student_dic[key])

        for key in volunteer_dic:
            volunteer_list.append(volunteer_dic[key])

        for each in department_name_list:
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
        pass

def compare_student(student):
    """为 department 里比较每个系最积极的学生做的比较器"""

    student.set_total_order_count()
    return student.total_order_count

def compare_volunteer(volunteer):
    """为 department 里比较每个系最积极的志愿者做的比较器"""
    volunteer.set_total_order_count()
    return volunteer.total_order_count

def select_order_personally(student_name, json_order_list, write_down=True):
    """_summary_
        筛选某个同学（sutdent_name）在一个 list of dicts 里的提问情况
    Args:
        student_name (str): 学生姓名
        json_order_list (list of dict)：订单信息，注意这个是原始的 dict，而不是 Order 类
    """
    assert student_name
    order_list = []
    try:
        for _, each in enumerate(json_order_list):
            try:
                name = each["actionRec"]["pAuthenData"]["realName"]
                if name == student_name:
                    order_list.append(each)
            except Exception as e:
                continue
    except Exception as e:
        pass
    if write_down:
            with open(f"./{student_name}.json", "w+", encoding="utf-8", errors="ignore") as f:
                json.dump(order_list, f, ensure_ascii=False, indent=2)
    return order_list

def select_order_during_(date_start: int, date_end: int, json_order_list, writedown=False):
    """选择本学期的订单"""
    """
    注意：这里的 date_start 和 date_end 是 int 类型，而不是 datetime 类型，例如 20200904
    """
    """返回 order_list"""
    try:
        order_list = []
        try:
            for _, each in enumerate(json_order_list):
                try:
                    time = each["actionRec"]["ptime"]
                    year = time[: 4]
                    month = time[5: 7]
                    day = time[8: 10]
                    date = int(year + month + day)
                    if date <= date_start or date >= date_end:
                        continue
                except Exception as e:
                    continue
                order_list.append(each)
            if writedown:
                with open(f"./result_order_during_{date_start}_{date_end}.json", "w+", encoding="utf-8", errors="ignore") as f:
                    json.dump(order_list, f, ensure_ascii=False, indent=2)
            return order_list
        except Exception as e:
            pass
    except Exception as e:
        pass

def select_order_for_student_enrollment(enrollment_start, enrollment_end, json_order_list):
    """_summary_
        单独筛选某个年级段的同学的订单，比如筛选出所有一字班同学的订单或者筛选出所有零字班同学的订单
    Args:
        enrollment_start (int): 入学年份起点，比如 2020
        enrollment_end (int): 入学年份终点，比如 2022
        json_order_list (list of dict): list of dict
    """
    order_list = []
    for each in json_order_list:
        try:
            studentEnrollment = int(str(each["actionRec"]["pAuthenData"]["studentID"])[0:4])
            if (studentEnrollment <= enrollment_start) or ( studentEnrollment > enrollment_end):
                continue
            order_list.append(each)
        except Exception as e:
                continue
    return order_list

def slect_all_order(json_file="./order.json"):
    """返回文件内的所有订单"""
    """返回 order_list"""
    json_order_list = []
    with open(json_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f.readlines():
            dic = json.loads(line)
            json_order_list.append(dic)
    return json_order_list