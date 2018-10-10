
from django.shortcuts import HttpResponse,render,redirect,Http404

from django.core.urlresolvers import resolve
from crm.permissions import permission_list

def perm_check(*args,**kwargs):
    request = args[0]
    if request.user.is_authenticated():
        print('request.user.is_admin',request.user.is_admin)
        if request.user.is_admin:
            return True
        for permission_name, v in permission_list.perm_dic.items():
            print("匹配URL")
            print(permission_name, v)
            url_matched = False
            if v['url_type'] == 1: #absoluite
                if v['url'] == request.path: #绝对URL匹配上了
                    url_matched = True
            else:
                #把绝对的url请求转成相对的url name
                print("resolve(request)")
                resolve_url_obj = resolve(request.path)
                print(resolve_url_obj,resolve_url_obj.url_name, v['url'])

                if resolve_url_obj.url_name == v['url']:#相对的url匹配上了
                    url_matched = True
            print("请求方法匹配上了",url_matched)
            if url_matched:
                print("请求方法匹配上了")
                if v['method'] == request.method:#请求方法匹配上了
                    arg_matched = True
                    for request_arg in v['args']:
                        request_method_func = getattr(request,v['method'])
                        if not request_method_func.get(request_arg):
                            arg_matched = False

                    if arg_matched:#权限匹配完了
                        print("权限匹配完了")
                        if request.user.has_perm(permission_name):
                            #有权限
                            print("有权限",permission_name)
                            return True



    else:
        return redirect("/account/login")


def check_permissiom(func):

    def inner(*args,**kwargs):
        print("---->",*args,**kwargs)
        print("---->",func)
        if perm_check(*args,**kwargs) is True:
            return func(*args,**kwargs)
        else:
            print("没权限")
            return HttpResponse("没权限")
    return inner

