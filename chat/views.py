# chat/views.py
from django.shortcuts import render
     
def stream(request):
    return render(request,'chat/test.html',{})