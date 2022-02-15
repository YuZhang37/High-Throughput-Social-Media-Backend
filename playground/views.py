from django.shortcuts import render


def calculate():
    x = 1
    y = 2
    return x + y


def say_hello(request):
    # return HttpResponse('hello, world')
    # return render(request, 'hello.html')
    x = 1
    y = 2
    z = calculate()
    return render(request, 'playground/hello.html', {'name': 'Marvin', 'value': z})
