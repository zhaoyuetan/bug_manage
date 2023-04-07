from django.http import HttpRequest,JsonResponse
from django.shortcuts import HttpResponse,render,redirect

def index(request:"HttpRequest"):
    return render(request,'index.html')
