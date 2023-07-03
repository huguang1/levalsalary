from django.db import models


# 这个是等级表
class Grade(models.Model):
    grade = models.CharField('等级名称', max_length=100)
    total_bet = models.BigIntegerField('历史投注')
    gold = models.IntegerField('晋级彩金')
    week_bet = models.IntegerField('周需投注')
    week_salary = models.IntegerField('每周俸禄')

    class Meta:
        verbose_name = "等级管理"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.grade


# 这个周期表
class WeekData(models.Model):  # 这个类得定期修改
    week_name = models.CharField('周期名称', max_length=100)
    serial = models.IntegerField('排序字段')

    class Meta:
        verbose_name = "周期管理"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.week_name


# 这个是每周的记录表
class WeekRecord(models.Model):  # 周的记录，必须要和周联系在一起
    account = models.CharField('会员账号', max_length=100)
    week_amount = models.BigIntegerField('投注金额', default=1)
    gold = models.IntegerField('晋级彩金', default=0)
    week_salary = models.IntegerField('周俸禄', default=0)
    # downgrade = models.BooleanField('是否降级', default=False)
    compute = models.BooleanField('是否计算', default=False)
    week = models.ForeignKey(WeekData, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "会员投注"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.account)


# 这个是对会员所有信息的统计
class TotalRecord(models.Model):  # 这个平台不用会员注册
    account = models.CharField('会员账号', max_length=100)
    total_bet = models.BigIntegerField('投注金额(总)')
    total_gold = models.IntegerField('等级礼金(总)')
    total_week_salary = models.IntegerField('周俸禄(总)')
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "会员统计"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.account)


class Count(models.Model):
    count = models.IntegerField('开始计算')