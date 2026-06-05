from django.contrib.auth.models import Group,Permission,ContentType
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import requests
 
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
        resposta = requests.get('https://elmeuescriptori.gestioeducativa.gencat.cat/api/v3/admin/users',
                                headers=headers)
        macs = {}

        # iterate users
        for user in resposta.json():
            print("\nID: {}\nUsername: {}".format(user["id"],user["name"]))
            uid = user["id"]

            # DESKTOPS
            resposta2 = requests.get(f'https://elmeuescriptori.gestioeducativa.gencat.cat/api/v3/admin/user/{uid}/desktops',
                                headers=headers)

            # iterate desktops
            for desktop in resposta2.json():
                print("\t"+desktop["name"])
                #print("\t"+str(desktop))
                # iterate interfaces
                for interface in desktop["interfaces"]:
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
                            "desktop_name": desktop["name"],
                            "username":user["username"],
                            "user_name":user["name"],
                        }

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

        # Amb les Macs actualitzades, revisem els Intents
        data = timezone.now() - timedelta(hours=12)
        # TODO: filtrar 12h enrera ,data__lt=data ??
        for intent in Intent.objects.filter(nom_usuari_isard=None,mac_isnull=False):
            interf = InterficieVM.objects.filter(mac=intent.mac).first()
            if interf:
                intent.nom_usuari_isard = interf.nom_usuari_isard
                intent.nom_escriptori = interf.nom_escriptori
                intent.usuari_isard_id = interf.usuari_isard_id
