
enabled_admins = {}


from crm import models
from django.shortcuts import render ,redirect ,HttpResponse

class BaseAdmin(object):
    list_display = []
    list_filter = []
    list_pre_page = 20
    search_fields = []
    filter_horizontal = []
    readonly_fields = []
    modelform_exclude_fields=[]
    actions = ["delete_selected_objs",]
    readonly_table = False

    def delete_selected_objs(self,request,querysets):
        print("----->request admin",request,querysets)
        app_name=self.model._meta.app_label
        table_name=self.model._meta.model_name
        #self.model._meta.model_name

        selected_ids= ','.join([str(i.id) for i in querysets])

        if self.readonly_table:
            errors = {"readonly_table": "This table is readonly ,cannot be delete"}
        else:
            errors = {}

        if request.POST.get("delete_confirm") == "yes":
            if not self.readonly_table:
                querysets.delete()
            return redirect("/king_admin/%s/%s" % (app_name, table_name))

        return render(request,"king_admin/table_obj_delete.html",{"objs":querysets,
                                                                  "admin_class":self,
                                                               "app_name":app_name,
                                                               "table_name":table_name,
                                                                "selected_ids":selected_ids,
                                                                  "action":request._admin_action,
                                                                  "errors":errors
                                                                  })

    def default_form_validation(self):
        """yonghu keyi zaici zidingyi biaodan yanzheng """

        #print("default_form_validation",self)

class CustomerAdmin(BaseAdmin):
    list_display = ['id','qq','name','source','consultant','consult_course','status','date','enroll']
    list_filters = ['source','consultant','consult_course','date']
    list_pre_page = 4
    search_fields = ['qq','name','consultant__name']
    filter_horizontal = ['tags']
    #readonly_fields = ['qq','consultant']
    #readonly_table = True

    def enroll(self):
        if self.instance.status == 1:
            return '''<a href="/crm/customer/%s/enrollment/" >报名</a>'''%self.instance.id
        else:
            return '''<a href="#" >---</a>'''

    enroll.display_name = "报名链接"

    def default_form_validation(self):
        """yonghu keyi zaici zidingyi biaodan yanzheng """

        #print("default_form_validation",self)
        consult_content = self.cleaned_data.get('content','')
        if len(consult_content) < 15:
            return self.ValidationError(
                ("Field %(field)s 咨询内容不能少于15个字符"),
                code='invalid',
                params={'field': "content"},
            )

    def clean_name(self):
        print("name clean validation")
        if not self.cleaned_data.get("name"):
            self.add_error("name","can not be none")

        return self.cleaned_data.get("name")


class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ['customer','consultant','date']

class UserProfileAdmin(BaseAdmin):
    list_display = ["email","name"]
    readonly_fields = ["password"]
    filter_horizontal = ["user_permissions"]
    modelform_exclude_fields = ["last_login"]

class CourseRecordAdmin(BaseAdmin):
    list_display = ['from_class','day_num','teacher','has_homework','homework_title']

    def initialize_studyrecords(self,request,queryset):
        print('--->initialize_studyrecords',self,request,queryset)
        if len(queryset) > 1 :
            return HttpResponse("只能选择一个班级")

        print(queryset[0].from_class.enrollment_set.all())
        for enroll_obj in queryset[0].from_class.enrollment_set.all() :
            pass
            models.StudyRecord.objects.get_or_create(
                student = enroll_obj,
                course_record = queryset[0],
                attendence = 0,
                score = 0,
            )

        return redirect("http://127.0.0.1:8000/king_admin/crm/studyrecord?course_record=%s"%queryset[0].id)

    initialize_studyrecords.short_description = "初始化本节所有学员上课记录"
    actions = ['initialize_studyrecords']

class StudyRecord(BaseAdmin):
    list_display = ['student','course_record','attendence','score','date']
    list_filters = ['course_record','score']

class CourseAdmin(BaseAdmin):
    list_display = ['name','price','period']
    list_filters = ['price']

class BranchAdmin(BaseAdmin):
    list_display = ['name','addr']
    list_filters = ['name']

class ClassListAdmin(BaseAdmin):
    list_display = ['branch','course','class_type','semester']
    list_filters = ['class_type']

class EnrollmentAdmin(BaseAdmin):
    list_display = ['customer','enrolled_class','consultant','contrack_agreed','contrack_approved','date']
    list_filters = ['contrack_agreed']

class PaymentAdmin(BaseAdmin):
    list_display = ['customer','course','amount','consultant','date']
    list_filters = ['course']

class RoleAdmin(BaseAdmin):
    list_display = ['name']
    list_filters = ['name']
    filter_horizontal = ["menus"]

class MenuAdmin(BaseAdmin):
    list_display = ['name','url_type','url_name']
    list_filters = ['url_type']

def register(model_class,admin_class=None):
    if model_class._meta.app_label not in enabled_admins:
        enabled_admins[model_class._meta.app_label]={}

    admin_class.model = model_class
    enabled_admins[model_class._meta.app_label][model_class._meta.model_name]=admin_class


register(models.Customer,CustomerAdmin)
register(models.CustomerFollowUp,CustomerFollowUpAdmin)
register(models.UserProfile,UserProfileAdmin)
register(models.CourseRecord,CourseRecordAdmin)
register(models.StudyRecord,StudyRecord)
register(models.Course,CourseAdmin)
register(models.Branch,BranchAdmin)
register(models.ClassList,ClassListAdmin)
register(models.Enrollment,EnrollmentAdmin)
register(models.Payment,PaymentAdmin)
register(models.Role,RoleAdmin)
register(models.Menu,MenuAdmin)
