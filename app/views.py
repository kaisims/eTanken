from django.shortcuts import render
from ecrterm.ecr import ECR
from django.http import HttpResponse
from ecrterm.packets.types import ConfigByte
from app.terminalController import *


# Create your views here.
def start(request):

    if checkConnection():
        return render(request, 'app/start.html')
    else:
        return render(request, 'Leider kein KreditkartenDing verfügbar')


def startpayment(request):

    context = {
        'euro': 12
    }
    if checkConnection():
        asyncio.run(main())
        return render(request, 'app/startpayment.html', context)
    else:
        return render(request, 'Leider kein KreditkartenDing verfügbar')