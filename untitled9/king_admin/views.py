from django.shortcuts import render ,redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.
from king_admin import king_admin
from king_admin.forms import create_model_form
from django.contrib.auth.decorators import login_required

from crm.permissions import permission

@login_required
@permission.check_permissiom
def table_index(request):
    print(king_admin.enabled_admins)
    return render(request,"king_admin/table_index.html",{'table_list':king_admin.enabled_admins})

from king_admin.utils import table_filter, table_sort, table_search

@login_required
@permission.check_permissiom
def display_table_objs(request,app_name,table_name):

    print("-->",app_name,table_name)

    admin_class = king_admin.enabled_admins[app_name][table_name]

    if request.method == "POST":#action  来了
        print(request.POST)
        selected_ids = request.POST.get("selected_ids")
        if selected_ids:
            selected_objs = admin_class.model.objects.filter(id__in=selected_ids.split(','))
        else:
            raise KeyError("No object selected!")

        action = request.POST.get("action")

        if hasattr(admin_class,action):
            action_func=getattr(admin_class,action)
            request._admin_action = action
            return action_func(admin_class ,request,selected_objs)

    #object_list = admin_class.model.objects.all()
    object_list,filter_conditions = table_filter(request,admin_class)

    object_list = table_search(request,admin_class,object_list)

    object_list,orderby_key = table_sort(request, admin_class, object_list)

    paginator = Paginator(object_list, admin_class.list_pre_page) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        query_sets = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        query_sets = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        query_sets = paginator.page(paginator.num_pages)

    print("aaa=",filter_conditions)
    return render(request,"king_admin/table_objs.html",{"admin_class":admin_class,
                                                        "query_sets":query_sets,
                                                        "filter_conditions":filter_conditions,
                                                        "orderby_key":orderby_key,
                                                        "previous_orderby":request.GET.get('o','')})

@login_required
@permission.check_permissiom
def table_obj_change(request,app_name,table_name,obj_id):

    admin_class = king_admin.enabled_admins[app_name][table_name]
    model_form_class = create_model_form(request,admin_class)

    obj = admin_class.model.objects.get(id=obj_id)
    if request.method == "POST":
        #request.POST.copy
        # for field in admin_class.readonly_fields:
        #     field_val = getattr(obj,field)
        #     request.POST[field] = field_val
        print(request.POST)
        form_obj = model_form_class(request.POST ,instance=obj)
        if form_obj.is_valid():
            form_obj.save()
    else:

        form_obj = model_form_class(instance=obj)
        #print("------->",getattr(obj,"name"))
    return render(request,"king_admin/table_obj_change.html",{"form_obj":form_obj,
                                                              "admin_class":admin_class,
                                                              "app_name":app_name,
                                                              "table_name":table_name})

@login_required
def password_reset(request,app_name,table_name,obj_id):

    admin_class = king_admin.enabled_admins[app_name][table_name]
    model_form_class = create_model_form(request,admin_class)

    obj = admin_class.model.objects.get(id=obj_id)
    errors={}
    if request.method == "POST":

        _password1 = request.POST.get("password1")
        _password2 = request.POST.get("password2")

        if _password1 == _password2:
            if len(_password2) > 5 :
                obj.set_password(_password1)
                obj.save()
                return redirect(request.path.rstrip("password/"))
            else:
                errors["password_too_short"] = "must not less than 6 letters"
        else:
            errors['invalid_password'] = "passwords are not the save"

    return render(request,'king_admin/password_reset.html',{"obj":obj,"errors":errors})

@login_required
@permission.check_permissiom
def table_obj_delete(request,app_name,table_name,obj_id):
    admin_class=king_admin.enabled_admins[app_name][table_name]
    obj = admin_class.model.objects.get(id=obj_id)

    errors = {}
    if request.method == "POST":
        if not admin_class.readonly_table:
            obj.delete()
            return redirect("/king_admin/%s/%s"%(app_name,table_name))

        errors = {"readonly_table":"table is readonly ,obj [%s] cannot be deleted"%obj}


    return render(request, "king_admin/table_obj_delete.html",{"objs":[obj],
                                                               "app_name": app_name,
                                                               "table_name": table_name,
                                                               "errors" : errors
                                                                })

# def table_obj_delete(request,app_name,table_name,obj_id):
#     admin_class = king_admin.enabled_admins[app_name][table_name]
#
#     return request(request, 'king_admin/table', {"app_name":app_name})

@login_required
@permission.check_permissiom
def table_obj_add(request,app_name,table_name):

    admin_class = king_admin.enabled_admins[app_name][table_name]
    model_form_class = create_model_form(request,admin_class)

    if request.method == "POST":
        form_obj = model_form_class(request.POST )
        if form_obj.is_valid():
            form_obj.save()
            return redirect(request.path.replace("/add",""))
    else:
        form_obj = model_form_class()

    return render(request,"king_admin/table_obj_add.html",{"form_obj":form_obj})

