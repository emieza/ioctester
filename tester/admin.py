from django.contrib import admin

from .models import *


class IntentAdmin(admin.ModelAdmin):
    model = Intent
    exclude = []
    readonly_fields = ["set","alumne","resultat","registre","ip"]
    list_display = ["set","nom_alumne","resultat","ip","nom_usuari_isard","data"]
    search_fields = ["alumne__first_name","alumne__last_name","alumne__email","set__nom","ip"]

class ProvaAdmin(admin.ModelAdmin):
    model = Prova
    readonly_fields = ["creador"]
    list_display = ["nom","creador"]
    search_fields = ["nom","creador","categoria__nom"]

class ProvaInline(admin.StackedInline):
    model = Prova
    fields = ("nom","tipus","activa","connexio_ssh","pes","script","descripcio" )
    readonly_fields = ("connexio_ssh",)
    extra = 1

class SetAdmin(admin.ModelAdmin):
    model = Set
    readonly_fields = ["creador"]
    list_display = ["nom","actiu","creador"]
    search_fields = ["nom","creador","categoria__nom"]
    inlines = [ProvaInline,]

class InterficieAdmin(admin.ModelAdmin):
    model = InterficieVM
    list_display = ["mac","compte","nom_usuari_isard","nom_escriptori","actualitzat"]
    search_fields = ["mac","nom_usuari_isard","nom_escriptori"]
    readonly_fields = ["mac","compte","nom_escriptori","nom_usuari_isard","usuari_isard_id"]

admin.site.register(Categoria)
admin.site.register(Prova,ProvaAdmin)
admin.site.register(Intent,IntentAdmin)
admin.site.register(Set,SetAdmin)
admin.site.register(InterficieVM,InterficieAdmin)
