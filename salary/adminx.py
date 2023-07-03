from extra_apps import xadmin
from salary.models import Grade, WeekData, WeekRecord, TotalRecord, Count
from xadmin import views
from import_export import resources


class BaseSetting(object):

    enable_themes = True
    use_bootswatch = True

xadmin.site.register(views.BaseAdminView, BaseSetting)


class Globalsettings(object):

    site_title = '等级俸禄查询系统-后台管理'
    site_footer = '© 2017 boy'
xadmin.site.register(views.CommAdminView, Globalsettings)


class WeekRecordResources(resources.ModelResource):
    """会员导入类"""
    class Meta:
        model = WeekRecord
        import_id_fields = ('id',)
        fields = ('id', 'account', 'week_amount', 'week')


class GradeAdmin(object):
    list_display = ['id', 'grade', 'total_bet', 'gold', 'week_bet', 'week_salary']
    ordering = ['total_bet']


class WeekDateAdmin(object):
    list_display = ['id', 'week_name', 'serial']
    ordering = ['-serial']


class WeekRecordAdmin():
    list_display = ['id', 'account', 'week_amount', 'gold', 'week_salary', 'week', 'compute']
    readonly_fields = ['compute']
    ordering = ['-week', '-week_amount']
    search_fields = ['account']
    list_filter = ['week']
    import_export_args = {'import_resource_class': WeekRecordResources}
    list_per_page = 10

    def queryset(self):
        qs = super(WeekRecordAdmin, self).queryset()
        return qs


class TotalRecordAdmin(object):
    list_display = ['id', 'account', 'grade', 'total_bet', 'total_gold', 'total_week_salary']
    ordering = ['-total_bet']
    search_fields = ['account']


class CountAdmin(object):
    list_display = ['skip']

    def skip(self, id):
        from django.utils.safestring import mark_safe
        return mark_safe("<a href='/salary/index'>开始计算</>")
    skip.short_description = "开始计算"


xadmin.site.register(Grade, GradeAdmin)
xadmin.site.register(WeekData, WeekDateAdmin)
xadmin.site.register(WeekRecord, WeekRecordAdmin)
xadmin.site.register(TotalRecord, TotalRecordAdmin)
xadmin.site.register(Count, CountAdmin)
