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
            self.atime = order_dic["actionRec"]["atime"] if "atime" in order_dic["actionRec"].keys() else 0
            self.ftime = order_dic["actionRec"]["ftime"] if "ftime" in order_dic["actionRec"].keys() else 0
            self.auid = order_dic["actionRec"]["auid"] if "auid" in order_dic["actionRec"].keys() else 0
            self.feedback_dic = order_dic["feedback"] if "feedback" in order_dic.keys() else {}
            self.volunteer_dic = order_dic["actionRec"]["aAuthenData"] if "aAuthenData" in order_dic["actionRec"].keys() else {}
            self.client_dic = order_dic["actionRec"]["pAuthenData"]
            print(self.feedback_dic)
        except Exception as e:
            from IPython import embed
            embed()
        """authentication, certificateState, department, realName, school, studentID"""