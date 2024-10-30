from django.contrib import admin

from .models import *


class IntentAdmin(admin.ModelAdmin):
	model = Intent
	exclude = []
	readonly_fields = ["set","alumne","resultat","registre","ip"]
	list_display = ["set","nom_alumne","resultat","ip","data"]
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

admin.site.register(Categoria)
admin.site.register(Prova,ProvaAdmin)
admin.site.register(Intent,IntentAdmin)
admin.site.register(Set,SetAdmin)

