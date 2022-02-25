from django.shortcuts import render

from likes.models import Like


def calculate():
    x = 1
    y = 2
    return x + y


def say_hello(request):
    like = Like.objects.all().first()
    model_name = like.content_type.model
    print(model_name)
    print(model_name == 'comment')
    print(model_name == 'tweet')
    return render(request, 'playground/hello.html', {'name': 'Marvin', 'value': 0})
