#!/usr/bin/env python

from django.http import HttpResponse

from redd.tasks import add 

def test_task(request):
    result = add.delay(4, 4)
    result.get()

    return HttpResponse(result.get())

