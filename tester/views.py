from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

import subprocess, os
from .models import *

def index(request):
    proves = Prova.objects.all()
    return render( request, "index.html", {"proves":proves} )


@login_required
def executa_prova(request,prova_id):
    ip = get_client_ip(request)
    resultat = "Iniciant prova {} per a usuari {} en IP={}\n".format(
                    prova_id, request.user, ip)
    try:
        prova = Prova.objects.get(id=prova_id)
        intent = Intent( prova=prova, alumne=request.user,
                            ip=ip, registre=resultat )
        resultat += "PROVA: {}\n".format(prova.nom)
        instruccio = prova.instruccio.replace("%IP",ip)
        resultat += "Executant instrucció: " + instruccio + "\n"
        intent.save()

        # Afegim connexio SSH si pertoca        
        if prova.connexio_ssh:
            conn_str = "ssh isard@" + ip
            instruccio = conn_str + " " + instruccio

        # Executar comanda
        completedProc = subprocess.run( instruccio, shell=True,
                            capture_output=True )
        #print(str(completedProc))

        if completedProc.returncode==0:
            resultat +="[SUCCESS]\n{}\n[SUCCESS]\n".format(completedProc.stdout.decode("utf-8"))
        else:
            resultat += "[FAIL] exit code = {}\n\t{}\n[FAIL]\n".format(
                completedProc.returncode, completedProc.stderr.decode("utf-8") )
            if prova.connexio_ssh and completedProc.returncode==255:
                resultat += "\tProbablement la teva màquina no es deixa accedir per SSH. Comprova que no hagis malmès l'usuari de connexió (isard)."

        # Guardem a la BD
        intent.registre = resultat
        intent.save()

        # Retornar resultats
        ret = {
            "status": "OK",
            "message": resultat
        }
        return JsonResponse(ret)
    except Exception as e:
        return JsonResponse({
            "status":"ERROR",
            "message":resultat + repr(e)
        })


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

