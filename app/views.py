from django.shortcuts import render
from ecrterm.ecr import ECR
from django.http import HttpResponse

# Create your views here.
def start(request):
    # Kreditkarten Terminal anmelden
    e = ECR(device='socket://192.168.178.89:22001', password='000000')
    if e.detect_pt():
        return render(request, 'app/start.html')
    else:
        return render(request, 'Leider kein KreditkartenDing verfügbar')