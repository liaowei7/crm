

from django import template

from django.utils.safestring import mark_safe

from datetime import datetime , timedelta

from django.core.exceptions import FieldDoesNotExist

register = template.Library()

@register.simple_tag
def render_app_name(admin_class):
    return admin_class.model._meta.verbose_name

@register.simple_tag
def get_query_sets(admin_class):
    return admin_class.model.objects.all()

@register.simple_tag
def build_table_row(request, obj, admin_class):
    row_ele = ""
    for index ,column in enumerate(admin_class.list_display):
        try:
            field_obj = obj._meta.get_field(column)
            if field_obj.choices:
                column_data = getattr(obj, "get_%s_display" % column)()
            else:
                column_data = getattr(obj, column)

            if type(column_data).__name__ == "datetime":
                column_data = column_data.strftime("%Y-%m-%d %H:%M:%S")

            if index == 0:
                column_data = '''<a href="{request_path}{obj_id}/change/">{data}</a>'''.format(request_path=request.path,
                                                                                                obj_id=obj.id,
                                                                                                data=column_data)
        except FieldDoesNotExist as e:
            if hasattr(admin_class,column):
                column_func = getattr(admin_class,column)
                admin_class.instance = obj
                admin_class.request = request
                column_data = column_func()

        row_ele +="<td>%s</td>"%column_data

    return mark_safe(row_ele)

@register.simple_tag
def render_page_ele(loop_counter,query_sets ,filter_condtions):

    filters = ""

    for k,v in filter_condtions.items():
        filters += "&%s=%s"%(k,v)

    if loop_counter <3 or loop_counter>query_sets.paginator.num_pages-2:
        ele_class = ""
        if query_sets.number == loop_counter:
            ele_class="active"
        ele='''<li class="%s"><a href="?page=%s%s">%s</a></li>'''%(ele_class,loop_counter,filters,loop_counter)

        return mark_safe(ele)


    if abs(query_sets.number - loop_counter)<2:
        ele_class=""
        if query_sets.number == loop_counter:
            ele_class="active"
        ele='''<li class="%s"><a href="?page=%s%s">%s</a></li>'''%(ele_class,loop_counter,filters,loop_counter)

        return mark_safe(ele)

    else:
        return ""


@register.simple_tag
def render_filter_ele(condtion,admin_class,filter_conditions):
    select_ele = '''<select class="form-control" name='{filter_field}' ><option value=''>----------</option>'''
    field_obj = admin_class.model._meta.get_field(condtion)

    print("filter_conditions=",filter_conditions ,type(filter_conditions))

    if field_obj.choices:
        selected = ''
        for choice_item in field_obj.choices:
            if filter_conditions.get(condtion) == str(choice_item[0]):
                selected = "selected"
            select_ele += '''<option value='%s' %s>%s</option>'''%(choice_item[0],selected,choice_item[1])
            selected = ''

    if type(field_obj).__name__ == 'ForeignKey':

        for choice_item in field_obj.get_choices()[1:]:
            selected = ''
            if filter_conditions.get(condtion) == str(choice_item[0]):
                selected = "selected"
            select_ele += '''<option value='%s' %s>%s</option>'''%(choice_item[0],selected,choice_item[1])
            selected = ''
    if type(field_obj).__name__ in ['DateTimeField','DateField']:
        date_els=[]
        today_ele = datetime.now().date()
        date_els.append(['今天',today_ele])
        date_els.append(['昨天',today_ele - timedelta(days=1)])
        date_els.append(['近7天',today_ele - timedelta(days=7)])
        date_els.append(['本月',today_ele.replace(day=1)])
        date_els.append(['近30天',today_ele - timedelta(days=30)])

        selected = ''
        for item in date_els:
            select_ele += '''<option value='%s' %s>%s</option>'''%(item[1],selected,item[0])
        filter_field_name = "%s__gte" % condtion
    else:
        filter_field_name = condtion

    select_ele += "</select>"

    return mark_safe(select_ele.format(filter_field= filter_field_name))

@register.simple_tag
def build_paginators(query_sets, filter_conditions, previous_orderby):
    '''返回整个的分页元素'''
    filters = ""

    for k,v in filter_conditions.items():
        filters += "&%s=%s"%(k,v)

    page_btns=''

    for page_num in query_sets.paginator.page_range:
        if page_num <3 or page_num > query_sets.paginator.num_pages - 2  or \
                        abs(query_sets.number-page_num) <=1:

            if query_sets.number == page_num:
                ele_class = "active"
            else:
                ele_class = ""
            page_btns+='''<li class="%s"><a href="?page=%s%s&o=%s">%s</a></li>''' % (
            ele_class, page_num, filters, previous_orderby,page_num)

        else:#显示...
            if (page_num == 3 or page_num == (query_sets.number+2)) and abs(query_sets.number - page_num) > 1 :
                page_btns += '<li><a>...</a></li>'

    return mark_safe(page_btns)

@register.simple_tag
def build_table_header_column(column,orderby_key,filter_conditions ,admin_class):
    ele="""<th><a href="?{filters}&o={orderby_key}">{column}</a>
    {sort_icon}
    </th>"""

    filters = ""

    for k,v in filter_conditions.items():
        filters += "&%s=%s"%(k,v)

    if orderby_key:
        if orderby_key.startswith("-"):
            sort_icon = """<span class="glyphicon glyphicon-chevron-up" aria-hidden="true"></span>"""
        else:
            sort_icon = """<span class="glyphicon glyphicon-chevron-down" aria-hidden="true"></span>"""
        if orderby_key.strip("-") == column:
            orderby_key = orderby_key

        else:
            orderby_key = column
            sort_icon = ""
    else:
        orderby_key = column
        sort_icon = ""
    try:
        column_verbose_name = admin_class.model._meta.get_field(column).verbose_name
        ele = ele.format(orderby_key=orderby_key,column=column_verbose_name,sort_icon=sort_icon,filters=filters)
    except FieldDoesNotExist:
        column_verbose_name = getattr(admin_class,column).display_name
        ele = """<th><a href="javascript:void(0);">{column}</a></th>""".format(column=column_verbose_name)
    return mark_safe(ele)

@register.simple_tag
def get_model_name(admin_class):

    return admin_class.model._meta.verbose_name


@register.simple_tag
def get_m2m_obj_list(admin_class, field , form_obj):
    '''dai xuan shu ju'''
    #
    field_obj = getattr(admin_class.model,field.name)
    all_obj_list = field_obj.rel.to.objects.all()

    #
    obj_instance_field = getattr(form_obj.instance,field.name)
    selected_obj=obj_instance_field.all()

    standby_obj_list = []
    for obj in all_obj_list:
        if obj not in selected_obj:
            standby_obj_list.append(obj)

    return standby_obj_list


@register.simple_tag
def get_m2m_selected_obj_list(form_obj, field):
    '''fanhui yixuanzhe de m2m shuju'''
    field_obj = getattr(form_obj.instance,field.name)
    return field_obj.all()

def recursive_related_objs_lookup(objs):
    uls_ele=''
    for obj in objs:
        uls_ele+=recursive_related_obj_lookup(obj)

    return uls_ele

def recursive_related_obj_lookup(obj):
    #model_name = objs._meta.model_name
    ul_ele = "<ul>"

    #for obj in objs:
        # li_ele = '''<li>
        #     <a href="/configure/web_hosts/change/%s/" >%s</a> </li>''' % (obj.id,obj.__repr__().strip("<>"))
        # ul_ele += li_ele
        # print("-----li",li_ele)
    li_ele = '''<li> %s: %s </li>'''%(obj._meta.verbose_name,obj.__str__().strip("<>"))
    ul_ele +=li_ele

    for m2m_field in obj._meta.local_many_to_many:
        sub_ul_ele = "<ul>"
        m2m_field_obj = getattr(obj,m2m_field.name)
        for o in m2m_field_obj.select_related():
            li_ele = '''<li> %s %s </li>'''%(m2m_field.verbose_name, o.name)
            sub_ul_ele += li_ele

        sub_ul_ele+="</ul>"
        ul_ele += sub_ul_ele


    for related_obj in obj._meta.related_objects:
        if 'ManyToManyRel' not in related_obj.__repr__():
            if hasattr(obj, related_obj.get_accessor_name()):
                accessor_obj = getattr(obj, related_obj.get_accessor_name())

                if hasattr(accessor_obj, 'select_related'):
                    target_objs = accessor_obj.select_related()  # .filter(**filter_coditions)

                    sub_ul_ele = "<ul style='color:red'>"
                    for o in target_objs:
                        li_ele = '''<li> %s %s </li>''' % (o._meta.verbose_name, o.__str__())
                        sub_ul_ele += li_ele

                    sub_ul_ele += "</ul>"
                    ul_ele += sub_ul_ele


        elif hasattr(obj,related_obj.get_accessor_name()):
        #if hasattr(obj,related_obj.get_accessor_name()):
            accessor_obj = getattr(obj,related_obj.get_accessor_name())

            if hasattr(accessor_obj,'select_related'):
                target_objs = accessor_obj.select_related() #.filter(**filter_coditions)

            else:
                #print("one to one i guess:",accessor_obj)
                target_objs = accessor_obj
            if len(target_objs) >0:
                print("\033[31;1mdeeper layer lookup -------\033[0m")
                for sub_obj in target_objs:
                    nodes = recursive_related_objs_lookup(sub_obj)
                ul_ele += nodes

    ul_ele +="</ul>"
    return ul_ele

@register.simple_tag
def display_obj_related(objs):
    '''把对象及所有相关联的数据取出来'''
    #if objs:
        #model_class = objs[0]._meta.model
    #mode_name = obj._meta.model_name
    return mark_safe(recursive_related_objs_lookup(objs))
