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
        i = 1
        punts_ok = 0
        punts_fail = 0
        proves_ok = 0
        proves_fail = 0
        total = myset.prova_set.filter(activa=True).count()
        superades = []
        # Iterem llista de Proves dins el Set
        for prova in myset.prova_set.filter(activa=True):
            resultat += "---------------------------------------------------------------------------\n"
            resultat += "[PROVA {}/{}]: {}\n".format(i,total,prova.nom)
            resultat += "Executant script de prova ({})\n".format(prova.tipus)
            intent.registre = resultat
            intent.save()

            # executem prova
            ok, prova_msg = executa_prova(prova,ip,intent.id,i)
            if ok:
                proves_ok += 1
                punts_ok += prova.pes
                superades.append("OK")
            else:
                proves_fail += 1
                punts_fail += prova.pes
                superades.append("ERROR")

            # Guardem resultat a la BD
            resultat += prova_msg
            intent.registre = resultat
            intent.save()
            i += 1

        # Processar resultat en %
        intent.resultat = punts_ok*100/(punts_ok+punts_fail)
        resultat += "\n---------------------------------------------------------------------------\n"
        resultat += "[RESUM] Intent id {}\n".format(intent.id)
        resultat += "\tProves exitoses: {}/{}. Resultat = {} %\n".format(
                        proves_ok,proves_ok+proves_fail,intent.resultat)
        # Resum proves
        i = 1
        for prova in myset.prova_set.filter(activa=True):
            resultat += "\t[Prova {}/{} - {} punts] {} - {}\n".format(i,
                            total, prova.pes, superades[i-1], prova.nom )
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

def executa_prova(prova,ip,intent_id,prova_num):
    missatge = ""
    nom_arxiu = "/tmp/ioctesterscript_{}_{}.sh".format(intent_id,prova_num)

    # guardem script en arxiu temporal
    script = prova.script.replace("%IP",ip) # substituim %IP per la IP del client
    script2 = script.replace("\r","\n") # corregim salts de línia per a Unix
    f = open(nom_arxiu, "w")
    f.write(script2)
    f.close()

    # executem script
    # opció BASHSRV:
    instruccio = None
    if prova.tipus=="BASHCLI":
        # traslladem script via scp
        completedScp = subprocess.run ("scp {} isard@".format(nom_arxiu)+ip+
                ":{}".format(nom_arxiu), shell=True, capture_output=True)
        if completedScp.returncode!=0:
            # falla la transferència del script
            missatge += "\t[ERROR ssh " + str(completedScp.returncode) + \
                    "] Probablement la teva màquina no es deixa accedir per SSH. Comprova que no hagis malmès l'usuari de connexió (isard).\n"
            return False, missatge
        # si arribem aquí és que s'ha transferit OK l'script per scp
        instruccio = "ssh isard@"+ip+" bash {}".format(nom_arxiu)
    elif prova.tipus=="BASHSRV":
        instruccio = "bash {}".format(nom_arxiu)
    elif prova.tipus=="SELESRV":
        instruccio = "cd /tmp; MOZ_HEADLESS=1 node {}".format(nom_arxiu)
    else:
        missatge += "[ERROR] Error intern del tipus de prova.\n"
        return False, missatge

    # Executar comanda
    completedProc = subprocess.run( instruccio,
                        shell=True, capture_output=True )
    #print(str(completedProc))

    # Elininar scripts temporals
    # script local
    completedRm = subprocess.run ("rm {}".format(nom_arxiu),
                    shell=True, capture_output=True)
    if completedRm.returncode!=0:
        print("[WARNING] no s'ha pogut eliminar script servidor")
        resultat += "\t[WARNING] no s'ha pogut eliminar script servidor"
    if prova.tipus=="BASHCLI" or prova.tipus=="SLNMCLI":
        # script remot (client)
        completedRm = subprocess.run ("ssh isard@"+ip+" rm {}".format(nom_arxiu),
                        shell=True, capture_output=True)
        if completedRm.returncode!=0:
            print("[WARNING] no s'ha pogut eliminar script client")
            resultat += "\t[WARNING] no s'ha pogut eliminar script client"

    # Processar sortida de la comanda
    if completedProc.returncode==0:
        missatge +="[SUCCESS]\n{}\n[SUCCESS] Prova {} - {}\n".format(
            completedProc.stdout.decode("utf-8"),prova_num,prova.nom)
        return True, missatge
    
    # si arribem aquí es que ha fallat l'execució
    missatge += "[FAIL] exit code = {}\n\
\t.....stdout......\n{}\n\
\t.....stderr......\n{}\n\
[FAIL] Prova {} - {}\n".format(
        completedProc.returncode, completedProc.stdout.decode("utf-8"),
        completedProc.stderr.decode("utf-8"),prova_num,prova.nom )
    if prova.tipus=="BASHCLI" and completedProc.returncode==255:
        missatge += "\tProbablement la teva màquina no es deixa accedir per SSH. Comprova que no hagis malmès l'usuari de connexió (isard).\n"
    return False, missatge


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

