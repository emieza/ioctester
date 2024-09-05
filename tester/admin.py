from django.contrib import admin

from .models import *


class IntentAdmin(admin.ModelAdmin):
	model = Intent
	exclude = []
	readonly_fields = ["prova","alumne","resultat","registre","ip"]
	list_display = ["prova","alumne","resultat"]
	search_fields = ["alumne__first_name","prova__nom"]

class ProvaAdmin(admin.ModelAdmin):
	model = Prova
	readonly_fields = ["creador"]
	list_display = ["nom","creador","categoria"]
	search_fields = ["nom","creador","categoria__nom"]

admin.site.register(Categoria)
admin.site.register(Prova,ProvaAdmin)
admin.site.register(Intent,IntentAdmin)
admin.site.register(Clau)

