from django.http import HttpResponse


def orders(request):
    return HttpResponse("Hello, world. You're at the polls orders.")