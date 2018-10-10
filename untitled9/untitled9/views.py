
from django.shortcuts import render ,redirect

from django.contrib.auth import authenticate , login ,logout
from django.contrib.auth.decorators import login_required

def acc_login(request):
    errors = {}
    if request.method == "POST":
        _email = request.POST.get("email")
        _password = request.POST.get("password")

        print(_email,_password)

        user = authenticate(username=_email,password=_password)

        print("auth res",user)
        if user:
            login(request,user)
            next_url = request.GET.get("next","/")
            return redirect(next_url)
        else:
            errors['error'] = "Username or password is wrong"

    return render(request,"login.html",{"errors":errors})


def acc_logout(request):

    logout(request)

    return redirect("/account/login/")

@login_required
def index(request):
    return render(request,'index.html')