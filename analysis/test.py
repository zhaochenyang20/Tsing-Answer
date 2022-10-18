from pathlib import Path
from utils import initialize
from utils import write_csv

order_json = "./order.json"

def write_student_and_volunteer_csv(student_list, volunteer_list):
    """_summary_
        因为很少用到对 Department 的数据分析，这个接口将 student 与 volunteer 的信息按照 csv 格式写出
    Args:
        student_list (list of dict): 学生信息
        volunteer_list (list of dict): 志愿者信息
    """
    store_student = []
    store_volunteer = []
    for each in student_list:
        store_student.append(each.report(report_json=False))
    for each in volunteer_list:
        store_volunteer.append(each.report(report_json=False))
    HOME = Path.cwd()
    write_csv(store_student, HOME / "student.csv")
    write_csv(store_volunteer, HOME / "student.csv")
    return None

def write_student_and_volunteer_json(student_list, volunteer_list):
    """_summary_
        因为很少用到对 Department 的数据分析，这个接口将 student 与 volunteer 的信息按照 json 格式写出（我个人更倾向于使用这个接口）
    Args:
        student_list (list of dict): 学生信息
        volunteer_list (list of dict): 志愿者信息
    """
    for each in student_list:
        each.report()
    for each in volunteer_list:
        each.report()

def write_department(department_list, format="json"):
    """_summary_
        对 Department 的数据分析，这个接口将 student 与 volunteer 的信息按照 json / csv 格式写出（我个人更倾向于使用 json）
    Args:
        department_list (list of dict): 院系信息
        format (str): 存储格式 json 或者 csv
    """
    for each in department_list:
        each.report(format=format)

if __name__ == '__main__':
    """先读取所有的order，加入到 student 和 volunteer 的 order list 里面"""
    """遍历所有的 student helper 和 volunteer，加入到 department 里面"""

    student_list, volunteer_list, department_list = initialize()
    # for each in student_list:
    #     for every in each.order_list:
    #         try:
    #             print(every.feedback_dic["period"])
    #         except:
    #             print(1)
    write_student_and_volunteer_json(student_list, volunteer_list)
