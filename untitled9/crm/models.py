
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser ,PermissionsMixin
)
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
# Create your models here.

class Customer(models.Model):
    '''客户信息表'''
    name = models.CharField(max_length=32,blank=True,null=True)
    qq = models.CharField(max_length=64,unique=True)
    qq_name = models.CharField(max_length=64,blank=True,null=True)
    phone = models.CharField(max_length=64,blank=True,null=True)
    id_num = models.CharField(max_length=64,blank=True,null=True)
    email = models.EmailField(verbose_name="常用邮箱",blank=True,null=True)
    source_choices = ((0, '转介绍'),
                      (1, 'QQ群'),
                      (2, '官网'),
                      (3, '百度推广'),
                      (4, '51CTO'),
                      (5, '知乎'),
                      (6, '市场推广'),
                      )

    source = models.SmallIntegerField(choices=source_choices)
    referral_from = models.CharField(verbose_name="转介绍人QQ：",max_length=64,blank=True,null=True)

    consult_course = models.ForeignKey("Course",verbose_name="咨询课程")
    content = models.TextField(verbose_name="咨询详情")
    tags = models.ManyToManyField("Tag",blank=True,null=True)
    status_choices = ((0,'已报名'),
                      (1,'未报名'),
                      )
    status = models.SmallIntegerField(choices=status_choices,default=1)
    consultant = models.ForeignKey("UserProfile")
    memo = models.TextField(blank=True,null=True)
    date =  models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.qq

class Tag(models.Model):
    name = models.CharField(unique=True,max_length=32)

    def __str__(self):
        return self.name

class CustomerFollowUp(models.Model):
    '''客户跟进'''
    customer = models.ForeignKey('Customer')
    content = models.TextField(verbose_name="跟进内容")
    consultant = models.ForeignKey("UserProfile")
    date = models.DateTimeField(auto_now_add=True)

    intention_choices = (
        (0,'2周内报名'),
        (1,'1个月内报名'),
        (2,'近期无报名计划'),
        (3,'已在其他机构报名'),
        (4,'已报名'),
        (5,'已拉黑'),
    )
    intention = models.SmallIntegerField(choices=intention_choices)

    def __str__(self):

        return "<%s : %s>"%(self.customer.qq,self.intention)



class Course(models.Model):
    '''课程表'''
    name = models.CharField(max_length=64,unique=True)
    price = models.PositiveIntegerField()
    period = models.PositiveSmallIntegerField(verbose_name="周期（月）")
    outline = models.TextField()

    def __str__(self):
        return self.name


class Branch(models.Model):

    name = models.CharField(max_length=128,unique=True)
    addr = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class ClassList(models.Model):
    '''班级表'''
    branch = models.ForeignKey("Branch")
    course = models.ForeignKey("Course")

    class_type_choices = (
        (0,'面授（脱产）'),
        (1,'面授（周末）'),
        (2,'网络班'),
    )
    contract = models.ForeignKey("ContractTemplate",blank=True,null=True)
    class_type = models.SmallIntegerField(choices=class_type_choices)

    semester = models.PositiveSmallIntegerField(verbose_name="学期")
    teachers = models.ManyToManyField("UserProfile")
    start_date = models.DateField(verbose_name="开班日期")
    end_date = models.DateField(verbose_name="结业日期",blank=True,null=True)

    def __str__(self):
        return "%s %s %s"%(self.branch,self.course,self.semester)

    class Meta:
        unique_together = ("branch","course","semester")


class CourseRecord(models.Model):
    '''上课记录'''
    from_class = models.ForeignKey("ClassList",verbose_name="班级")
    day_num = models.PositiveSmallIntegerField(verbose_name="第几节")
    teacher = models.ForeignKey("UserProfile")
    has_homework = models.BooleanField(default=True)

    homework_title = models.CharField(max_length=128,blank=True,null=True)
    homework_content = models.CharField(max_length=128,blank=True,null=True)
    outline = models.TextField(verbose_name="本届大纲")
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s %s"%(self.from_class,self.day_num)

    class Meta:
        unique_together = ("from_class","day_num")

class StudyRecord(models.Model):
    '''学习记录'''
    student = models.ForeignKey('Enrollment')
    course_record = models.ForeignKey('CourseRecord')
    attendence_choices =  (
        (0,'已签到'),
        (1,'迟到'),
        (2,'缺勤'),
        (3,'早退'),
    )
    attendence = models.SmallIntegerField(choices=attendence_choices)

    score_choices = (
        (100,'A+'),
        (90,'A'),
        (85,'B+'),
        (80,'B'),
        (75,'B-'),
        (70,'C+'),
        (0, 'N/A'),
                     )
    score = models.SmallIntegerField(choices=score_choices)

    memo = models.TextField(blank=True,null = True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s %s %s"%(self.student,self.course_record,self.score)

class Enrollment(models.Model):
    '''报名表'''
    customer = models.ForeignKey('Customer')
    enrolled_class = models.ForeignKey('ClassList',verbose_name="所在班级")

    consultant = models.ForeignKey('UserProfile',verbose_name='课程顾问')
    contrack_agreed = models.BooleanField(default=False,verbose_name="学院同意")
    contrack_approved = models.BooleanField(default=False,verbose_name="已审核")
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s %s"%(self.customer,self.enrolled_class)

    class Meta:
        unique_together = ('customer','enrolled_class')


class Payment(models.Model):
    '''缴费记录'''
    customer = models.ForeignKey('Customer')
    course = models.ForeignKey('Course',verbose_name='所报课程')
    amount = models.PositiveIntegerField()
    consultant = models.ForeignKey('UserProfile')
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return '%s %s'%(self.customer,self.amount)


from django.contrib.auth.models import User

# class UserProfile(models.Model):
#     '''账号表'''
#     user = models.OneToOneField(User)
#     name = models.CharField(max_length=32)
#     roles = models.ManyToManyField('Role',blank=True,null=True)
#
#     def __str__(self):
#         return self.name
#

class ContractTemplate(models.Model):
    '''hetongmoban'''
    name = models.CharField("合同名称",max_length=64,unique=True)
    template = models.TextField()
    def __str__(self):
        return self.name

class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class UserProfile(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )

    password = models.CharField(_('password'), max_length=128,
                                help_text=mark_safe('''<a href='password/'>修改密码</a>'''))
    name = models.CharField(max_length=32)
    roles = models.ManyToManyField('Role', blank=True, null=True)
    #date_of_birth = models.DateField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    objects = UserProfileManager()

    stu_account = models.ForeignKey("Customer",verbose_name="关联学员账号",blank=True,null=True,
                                    help_text="只有报名学员才能帮其创建账户")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email
    """
    def has_perm(self, perm, obj=None):
       "Does the user have a specific permission?"
        #Simplest possible answer: Yes, always

       return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    #"""

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    class Meta:
        permissions = (

            ('can_access_my_course','可以访问我的课程'),
            ('can_access_customer_list','可以访问客户列表'),
            ('can_access_customer_detail','可以访问客户详情'),
            ('can_access_studyrecords','可以访问学习记录页面'),
            ('can_access_homework_detail','可以访问作业详情'),
            ('can_upload_homework','可以交作业'),

            ('access_kingadmin_table_index','查看表格列表'),
            ('access_kingadmin_table_objs','查看每个表格'),
            ('change_kingadmin_table_objs','筛查每个表格'),
            ('access_kingadmin_table_obj_change','访问kingadmin每个表的对象'),
            ('change_kingadmin_table_obj_change','修改kingadmin每个表的对象'),
            ('access_kingadmin_obj_delete','查看删除对象'),
            ('change_kingadmin_obj_delete','删除对象'),
            ('access_kingadmin_table_obj_add','添加对象表'),
            ('change_kingadmin_table_obj_add','保存添加对象'),

            ('access_student_stu_my_classes', '查看我的课程'),
            ('access_student_studyrecords', '查看我的学习记录'),
            ('access_student_homework_detail', '提交作业'),
            ('access_student_stu_my_course', '查看自己的课程'),
            ('change_student_stu_my_course', '修改自己的课程'),
        )

class Role(models.Model):
    '''角色表'''
    name = models.CharField(max_length=32,unique=True)
    menus = models.ManyToManyField("Menu",blank=True,null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "角色"


class Menu(models.Model):
    '''菜单'''
    name = models.CharField(max_length=32)
    url_type_choices = ((0,"alais"),(1,"absolute_url"))
    url_type = models.SmallIntegerField(choices=url_type_choices,default=0)
    url_name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


