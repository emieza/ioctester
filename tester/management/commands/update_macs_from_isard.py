from django.contrib.auth.models import Group,Permission,ContentType
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings
from datetime import timedelta, datetime
import requests
 
from tester.models import *
from tester.lib import myLog

class Command(BaseCommand):
    help = 'Descarrega les adreces Mac dels escriptoris IsardVDI per verificar els intents dels usuaris'
 
    def handle(self, *args, **options):
        myLog( None, "CMDINIT", LogLevel.DEBUG, "Comanda update_macs_from_isard iniciada" )
        logMessage = ""

        try:
            init_time = datetime.now()
            logMessage += "Temps inici: {}\n".format(str(init_time))
            isard_api_token = settings.ISARD_API_TOKEN
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + isard_api_token
            }

            # USUARIS
            resposta = requests.get('https://elmeuescriptori.gestioeducativa.gencat.cat/api/v4/admin/items/users',
                                    headers=headers)
            if resposta.status_code != 200:
                #print("ERROR d'accés a l'API: el ISARD_API_TOKEN és probablement incorrecte.")
                raise CommandError("ERROR d'accés a l'API: el ISARD_API_TOKEN és probablement incorrecte.")

            macs = {}

            # iterate users
            for user in resposta.json():
                print("\nID: {}\nUsername: {}".format(user["id"],user["name"]))
                #print(user)
                uid = user["id"]

                # DESKTOPS
                resposta2 = requests.get(f'https://elmeuescriptori.gestioeducativa.gencat.cat/api/v4/admin/items/user/{uid}/desktops',
                                    headers=headers)
                # iterate desktops
                for desktop in resposta2.json():
                    #print(str(desktop))
                    #print("\t"+desktop["name"])
                    desktop_id = desktop["id"]
                    resposta3 = requests.get(f'https://elmeuescriptori.gestioeducativa.gencat.cat/api/v4/item/desktop/{desktop_id}/get-networks',
                                    headers=headers)
                    #print(str(resposta3.json()))

                    # iterate interfaces
                    for interface in resposta3.json()["networks"]:
                        mac = interface["mac"]
                        print(mac)
                        if mac in macs.keys():
                            # això no hauria de passar
                            # TODO: notificar error (email?)
                            logMessage += "\nERROR: macs repetides: "+str(mac)+"\n"
                            macs[mac].count += 1
                            print("ERROR: macs repetides: =============================")
                            # print dades anteriors
                            print(macs[mac])
                            # print dades actuals
                            print(resposta2.json())
                            print("====================================================")
                        else:
                            macs[mac] = {
                                "count":1,
                                "uid":uid,
                                "desktop_name": desktop["name"],
                                "username":user["username"],
                                "user_name":user["name"],
                            }

            logMessage += "Trobades {} adreces mac\n".format( str(len(macs)) )
            logMessage += "Temps després de crides API: {}\n".format(str(datetime.now()))

            # store in DB
            for mac in macs.keys():
                dadesMac = macs[mac]
                print(dadesMac["count"],mac,dadesMac["user_name"])
                # busquem si la Mac ja la tenim a la DB
                interf = InterficieVM.objects.filter(mac=mac).first()
                if not interf:
                    # no hi és: creem nova
                    interf = InterficieVM.objects.create(
                            mac=mac,
                            nom_escriptori = dadesMac["desktop_name"],
                            usuari_isard_id = dadesMac["uid"],
                            nom_usuari_isard = dadesMac["user_name"],
                            dades = str(dadesMac),
                            # count es crea per defecte = 1
                        )
                else:
                    if interf.usuari_isard_id != dadesMac["uid"]:
                        # la mac estava registrada a un altre usuari
                        # apuntem +1
                        interf.count = interf.count + 1
                        interf.dades = interf.dades + "\n\n" + str(dadesMac)
                    # actualitzem a les darreres dades
                    interf.nom_escriptori = dadesMac["desktop_name"]
                    interf.usuari_isard_id = dadesMac["uid"]
                    interf.nom_usuari_isard = dadesMac["user_name"]
                    interf.save()

            logMessage += "\nAdreces mac insertades a taula InterficiesVM\n"
            logMessage += "Temps després de inserció a la BD: {}\n".format(str(datetime.now()))

            # Amb les Macs actualitzades, revisem els Intents
            data = timezone.now() - timedelta(hours=12)
            intentsRevisats = 0
            intentsTrobats = 0
            # TODO: filtrar 12h enrera ,data__lt=data ??
            for intent in Intent.objects.filter(nom_usuari_isard=None,mac__isnull=False,data__gt=data):
                interf = InterficieVM.objects.filter(mac=intent.mac).first()
                intentsRevisats += 1
                if interf:
                    intentsTrobats += 1
                    intent.nom_usuari_isard = interf.nom_usuari_isard
                    intent.nom_escriptori = interf.nom_escriptori
                    intent.usuari_isard_id = interf.usuari_isard_id
                    intent.save()

            logMessage += "\nIntents revisats: {} ; Intents trobats: {}\n".format(str(intentsRevisats),str(intentsTrobats))
            logMessage += "Temps després de revisions de Intents: {}\n".format(str(datetime.now()))

            end_time = datetime.now()
            total_time = end_time - init_time
            logMessage += "\nTemps transcorregut: {}\n".format( str(total_time) )

            myLog( None, "CMDEND", LogLevel.DEBUG, "Comanda update_macs_from_isard. Interficies actualitzades.\n\nLogMessage:\n"+ logMessage )
        
        except Exception as e:
            print( "ERROR en la comanda: "+str(e) )
            myLog( None, "CMDERR", LogLevel.ERROR, "Comanda update_macs_from_isard: "+str(e) + "\n\nLogMessage:\n"+logMessage )

