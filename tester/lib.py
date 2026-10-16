from django.contrib.auth.models import Group,Permission,ContentType
import os, string, unicodedata, inspect
 
from .models import *

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def myLog(request,tag,level,message):
    stack = inspect.stack()
    origen = "fun: {} - File: {}:{}".format(stack[1].function,
                os.path.basename(stack[1].filename), stack[1].lineno )
    ip = get_client_ip(request) if request else None
    usuari = request.user.username if request else None
    userid = request.user.id if request else None
    log_obj = Log(  usuari="{} [id:{}]".format(usuari,userid),
                    tag=tag, text=message, level=level,
                    ip=ip, origen=origen
        )
    log_obj.save()
