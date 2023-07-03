from django.views.generic import View
from django.http.response import HttpResponse, JsonResponse
from django.http import HttpResponseRedirect
from salary.models import WeekRecord, TotalRecord, Grade, WeekData, TotalRecord
from django.shortcuts import render
import logging
logging.basicConfig(level=logging.INFO,
filename='./log.txt',
filemode='w',
format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
import time


class IndexView(View):

    # 从数据库查询各个等级需要的投注额
    def get_grades(self):
        grades = Grade.objects.all().order_by('total_bet')
        return grades

    # 将各个等级需要的投注额转化未列表
    # [[1, 299999, '玄铁'], [300000, 999999, '青铜'], [1000000, 3499999, '白银'], [3500000, 11999999, '黄金'], [12000000, 29999999, '铂金'], [30000000, 149999999, '水晶'], [150000000, 1499999999, '钻石'], [1500000000, 2999999999, '大师'], [3000000000, 9999999999, '宗师'], [10000000000, 99999999999, '王者']]
    def grade_bet(self):
        grade_bet = []
        grades = self.get_grades()
        if grades:
            i = 0
            while i < len(grades):
                if i == len(grades) - 1:
                    grade_bet.append([grades[i].total_bet, 99999999999, grades[i].grade])
                else:
                    grade_bet.append([grades[i].total_bet, grades[i + 1].total_bet - 1, grades[i].grade])
                i += 1
        return grade_bet

    # 计算每个等级的晋级礼金
    def count_gold(self, grades):
        count = 0
        for grade in grades:
            count = grade.gold
        return count

    # 计算等级礼金
    # {'王者': 188888, '白银': 588, '钻石': 8888, '宗师': 88888, '水晶': 3888, '铂金': 1888, '大师': 58888, '青铜': 188, '玄铁': 0, '黄金': 888}
    def grade_dict(self):
        grade_dict = {}
        grades = self.get_grades()
        if grades:
            i = 0
            while i < len(grades):
                count = self.count_gold(grades[0:i + 1])
                grade_dict[grades[i:i + 1][0].grade] = count
                i += 1
        return grade_dict

    # 计算等级
    def count_grade(self, total_count):
        grade_bet = self.grade_bet()
        for x in grade_bet:
            if x[0] <= total_count <= x[1]:
                obj_grade = Grade.objects.get(grade=x[2])
                return obj_grade

    # 计算等级礼金
    def grade_money(self, total_count):
        # 根据不同的周俸禄来计算不同等级礼金
        grade_bet = self.grade_bet()
        for x in grade_bet:
            if x[0] <= total_count <= x[1]:
                grade_dict = self.grade_dict()
                return grade_dict[x[2]]

    def get(self, request):
        all_records = WeekRecord.objects.filter(compute=False).order_by('week')
        member_list = []
        start_time = time.time()
        for record in all_records:
            try:
                member = TotalRecord.objects.get(account=record.account)
            except Exception as e:
                new_member = TotalRecord()
                new_member.account = record.account  # 会员账号
                new_member.total_bet = record.week_amount  # 总的投注金额
                grate_gold = self.grade_money(record.week_amount)  # 计算等级礼金
                new_member.total_gold = grate_gold
                new_member.total_week_salary = 0  # 周俸禄
                obj_grade = self.count_grade(record.week_amount)  # 计算等级
                new_member.grade_id = obj_grade.id  # 会员等级
                record.gold = grate_gold
                record.week_salary = 0
                record.compute = True
                member_list.append(new_member)
            else:
                member.total_bet += record.week_amount
                new_grade = self.count_grade(member.total_bet)
                if new_grade.id == member.grade_id:
                    # 周俸禄是根据上一周的等级来确定的。
                    if member.grade.week_bet <= record.week_amount:
                        member.total_week_salary += member.grade.week_salary
                        record.week_salary = member.grade.week_salary
                else:
                    if member.grade.week_bet <= record.week_amount:
                        member.total_week_salary += member.grade.week_salary
                        record.week_salary = member.grade.week_salary
                        member.grade_id = new_grade.id
                        grate_gold = self.grade_money(member.total_bet)  # 计算等级礼金
                        member.total_gold += grate_gold
                        record.gold = grate_gold
                record.compute = True
                member_list.append(member)
        end_time = time.time()
        times = end_time - start_time
        logging.info('计算事件%f' % times)
        for record in all_records:
            record.save()
        for member in member_list:
            member.save()
        last_time = time.time()
        times = last_time - end_time
        logging.info('博爱村事件%f' % times)
        return HttpResponseRedirect('/admin/salary/count/')


class SearchView(View):

    def get(self, request):
        return render(request, 'inquire.html')

    def post(self, request):
        account = request.POST['user']
        try:
            member = TotalRecord.objects.get(account=account)
        except Exception as e:
            json_data = {
                "stat": 2,
                "msg": "对不起，没有查到您的信息,请您输入正确的会员账号"
            }
        else:
            weeks = WeekData.objects.filter(weekrecord__account__isnull=False).order_by('-id').first()
            try:
                weekrecord = WeekRecord.objects.filter(account=member.account).get(week_id=weeks.id)
            except Exception as e:
                week = 0
                week_salary = 0
                # downgrade = 1
            else:
                week = weekrecord.week_amount
                week_salary = weekrecord.week_salary
                # downgrade = weekrecord.downgrade
            json_data = {
                "stat": 0,
                "user": member.account,
                "week": week,
                "total": member.total_bet,
                "lottery": week_salary,
                # "is_down": downgrade,
                "level": member.grade_id
            }
        return JsonResponse(json_data)

