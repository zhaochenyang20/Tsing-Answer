# Readme

小程序自身维护过导出 Excel 的接口，然而微信框架的窠臼太强，很多操作非常繁琐，所以编写了这个项目用于在本地处理订单。

项目维护者主要是 [Chenytang Zhao](https://github.com/zhaochenyang20) 本人。

# 数据来源

数据需要每次定期从答疑坊小程序的数据库中导出，导出 `Order` 对象为 `./order.json`，其对应的字段如下：

```sql
subjectID,courseID,abstract,state,online,actionRec.atime,actionRec.ptime,actionRec.ftime,feedback.period,feedback.suggestion
```

导出 `UserInfo` 为 `user.json`:

```
role,volunteerData,authenData
```

**请不要将导出的数据上传至 github，以免造成数据泄漏。**

# 使用方法

将导出后的 json 文件命名为 `order.json` 并放置在项目目录下（也即和所有的 `.py` 文件放置在同一级目录）。

随后，在 `utils.py` 下修改 `initialize` 方法，具体需要修改 `select_order_during_` 方法的参数，第一个参数为 `date_start`，第二个参数为 `date_end`。

```python
json_order_list = select_order_during_(20220613, 20220912, json_order_list)
```

而后，在命令行运行 `python3 main.py` 即可。

`./utils.py` 下的 `get_volunteer_salary_rank` 可以拿到志愿者等级。

# 文件说明

```shell
.
├── department.py
├── main.py
├── order.json
├── order.py
├── readme.md
├── student.py
├── utils.py
└── volunteer.py

0 directories, 8 files
```

## Department

`department.py` 构造了 `Department` 类：

1. `analysis_specific_department_course` 方法主要针对学科，能够分析某个院系的所有学生所提出问题集中的学科，每个学科提问次数；

2. `analysis_specific_department_student` 方法主要针对学生，分析这个系所有学生的提问情况；
3. `analysis_specific_department_helper` 方法主要针对回答过这个院系学生问题的志愿者；
4. `analysis_specific_department_volunteer` 方法针对来自这个院系的志愿者；
5. `report` 方法将以 `csv` 或者 `json` 格式输出这个院系的所有情况。

## Order

`order.py` 构造了 `Order` 类，储存了这些信息：

课程名字， 学科划分，发出时间，puid，擦亮次数，是否推送到知识库，回答时间，结束时间，auid，反馈，用户，志愿者。

## Student

`student.py` 构造了 `Student` 类，能够分析每个学生提出问题的总时长和各个学科提问的次数。

## Volunteer

`voluntter.py` 构造了 `Volunteer` 类，能够计算分析志愿者在传入的订单内答疑的总时长，平均满意度，总的订单数目。

## Utils

`utils.py` 定义了主要的筛选函数，**在使用时烦请自己修改**：

1. `slect_all_order` 将会载入 `order.json` 内所有的志愿者清单；
2. `select_order_for_student_enrollment` 将会选择出某些年级的同学提出的问题，比如选定九字班和零字班同学提出的问题；
3. `select_order_during_` 将会以左闭右开的方式选取出一段时间内的订单；
4. `select_order_personally` 将会选出某个人提出的订单；
5. `initialize` 方法最为重要，构造了 list of {Student, Order, Volunteer, Department}，需要用到扩展功能可以自行修改相关逻辑。

