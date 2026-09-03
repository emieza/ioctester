from django.contrib.auth.models import Group,Permission,ContentType
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import requests, json
 
from tester.models import *


class Command(BaseCommand):
    help = 'Descarrega les adreces Mac dels escriptoris IsardVDI per verificar els intents dels usuaris'
 
    #def add_arguments(self, parser):
    #    parser.add_argument('nom_centre', nargs=1, type=str)
 
    def handle(self, *args, **options):
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
            uid = user["id"]

            # DESKTOPS
            #resposta2 = requests.get(f'https://elmeuescriptori.gestioeducativa.gencat.cat/api/v4/admin/items/user/{uid}/desktops',
            #                    headers=headers)
            
            data = {
                'kind': "desktop",
                'user': uid
            }
            resposta2 = requests.post(f'https://elmeuescriptori.gestioeducativa.gencat.cat/api/v4/admin/items/domains',
                                headers=headers, json=data)
            print(json.dumps(resposta2.json(),indent=4,sort_keys=True))
            if resposta2.status_code != 200:
                raise CommandError("ERROR d'accés a l'API")

            # iterate desktops
            for desktop in resposta2.json():
                print("\t"+desktop["name"])
                print("\t"+desktop["id"])
                #print("\t"+str(desktop))

                # iterate interfaces
                desktop_id = desktop["id"]
                resposta3 = requests.get(f'https://elmeuescriptori.gestioeducativa.gencat.cat/api/v4/item/desktop/{desktop_id}/get-info',
                                headers=headers)
                resposta3.raise_for_status()

                desktop_info = resposta3.json()

                print(json.dumps(desktop_info, indent=4, sort_keys=True))

                # iterate desktop interfaces

                for interface in desktop_info["interfaces"]:
                    mac = interface["mac"]
                    #print(mac)
                    if mac in macs.keys():
                        # això no hauria de passar
                        # TODO: notificar error (email?)
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
                            "desktop_name": desktop_info["name"],
                            "username":user["username"],
                            "user_name":user["name"],
                        }

        # store all macs in DB
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

        # Amb les Macs actualitzades, revisem els Intents
        data = timezone.now() - timedelta(hours=12)
        # TODO: filtrar 12h enrera ,data__lt=data ??
        for intent in Intent.objects.filter(nom_usuari_isard=None,mac__isnull=False):
            interf = InterficieVM.objects.filter(mac=intent.mac).first()
            if interf:
                intent.nom_usuari_isard = interf.nom_usuari_isard
                intent.nom_escriptori = interf.nom_escriptori
                intent.usuari_isard_id = interf.usuari_isard_id
