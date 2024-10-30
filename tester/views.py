from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

import subprocess, sys, os
from .models import *

def index(request):
    sets = Set.objects.filter(actiu=True)
    return render( request, "index.html", {"sets":sets} )

@login_required
def executa_set(request,set_id):
    ip = get_client_ip(request)
    resultat = "---------------------------------------------------------------------------\n"
    resultat += "Iniciant set de proves {} per a usuari {} en IP={}\n".format(
                    set_id, request.user, ip)
    try:
        myset = Set.objects.get(id=set_id)
        intent = Intent( set=myset, alumne=request.user,
                            ip=ip, registre=resultat )

        # Iterem llista de Proves dins el Set
        i = 1
        punts_ok = 0
        punts_fail = 0
        proves_ok = 0
        proves_fail = 0
        total = myset.prova_set.filter(activa=True).count()
        superades = []
        for prova in myset.prova_set.filter(activa=True):
            resultat += "---------------------------------------------------------------------------\n"
            resultat += "[PROVA {}/{}]: {}\n".format(i,total,prova.nom)
            i += 1
            resultat += "Executant instrucció...(ssh={})\n".format(prova.connexio_ssh)
            intent.registre = resultat
            intent.save()

            # guardem script en arxiu temporal
            instruccio = prova.instruccio.replace("%IP",ip)
            script = instruccio.replace("\r","\n") # corregim salts de línia per a Unix
            f = open("/tmp/ioctesterscript.sh", "w")
            f.write(script)
            f.close()

            # executem comanda
            instruccio = "bash /tmp/ioctesterscript.sh"
            if prova.connexio_ssh:
                # traslladem script via scp
                completedScp = subprocess.run ("scp /tmp/ioctesterscript.sh isard@"+ip+
                        ":/tmp/ioctesterscript.sh", shell=True, capture_output=True)
                if completedScp.returncode!=0:
                    # falla la transferència del script
                    proves_fail += 1
                    punts_fail += prova.pes
                    superades.append("ERROR")
                    resultat += "\t[ERROR scp "+completedScp.returncode+"] Probablement la teva màquina no es deixa accedir per SSH. Comprova que no hagis malmès l'usuari de connexió (isard).\n"
                    # Guardem resultat a la BD
                    intent.registre = resultat
                    intent.save()
                    continue
                # si arribem aquí és que s'ha transferit el script per scp
                instruccio = "ssh isard@"+ip+" bash /tmp/ioctesterscript.sh"
                print(instruccio)

            # Executar comanda
            completedProc = subprocess.run( instruccio,
                                shell=True, capture_output=True )
            #print(str(completedProc))

            # Elininar scripts temporals
            if prova.connexio_ssh:
                # script local
                completedRm = subprocess.run ("rm /tmp/ioctesterscript.sh",
                                shell=True, capture_output=True)
                if completedRm.returncode!=0:
                    print("[WARNING] no s'ha pogut eliminar script local")
                    resultat += "\t[WARNING] no s'ha pogut eliminar script local"
                # script remot
                completedRm = subprocess.run ("ssh isard@"+ip+" rm /tmp/ioctesterscript.sh",
                                shell=True, capture_output=True)
                if completedRm.returncode!=0:
                    print("[WARNING] no s'ha pogut eliminar script remot")
                    resultat += "\t[WARNING] no s'ha pogut eliminar script remnot"

            # Processar sortida de la comanda
            if completedProc.returncode==0:
                resultat +="[SUCCESS]\n{}\n[SUCCESS] Prova {}/{} - {}\n".format(
                    completedProc.stdout.decode("utf-8"),i-1,total,prova.nom)
                proves_ok += 1
                punts_ok += prova.pes
                superades.append("OK")
            else:
                proves_fail += 1
                punts_fail += prova.pes
                superades.append("ERROR")
                resultat += "[FAIL] exit code = {}\n\t{}\n[FAIL]\n".format(
                    completedProc.returncode, completedProc.stderr.decode("utf-8") )
                if prova.connexio_ssh and completedProc.returncode==255:
                    resultat += "\tProbablement la teva màquina no es deixa accedir per SSH. Comprova que no hagis malmès l'usuari de connexió (isard).\n"

            # Guardem resultat a la BD
            intent.registre = resultat
            intent.save()

        # Processar resultat en %
        intent.resultat = punts_ok*100/(punts_ok+punts_fail)
        resultat += "---------------------------------------------------------------------------\n"
        resultat += "[RESUM] Intent id {}\n".format(intent.id)
        resultat += "\tProves exitoses: {}/{}. Resultat = {} %\n".format(
                        proves_ok,proves_ok+proves_fail,intent.resultat)
        # Resum proves
        i = 0
        for prova in myset.prova_set.filter(activa=True):
            resultat += "\t[Prova {}/{} - {} punts] {} - {}\n".format(i+1,
                            total, prova.pes, superades[i], prova.nom )
            i += 1
        intent.registre = resultat
        intent.save()

        # Retornar resultats
        ret = {
            "status": "OK",
            "message": resultat
        }
        return JsonResponse(ret)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_tb.tb_lineno)
        print("ERROR "+repr(e)+"\nError en línia "+str(exc_tb.tb_lineno))
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

