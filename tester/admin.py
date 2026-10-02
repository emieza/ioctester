from django.contrib import admin, messages
from django.core import serializers
from django.http import HttpResponse

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

@admin.action(description="Exporta els sets de proves.")
def exporta_sets(modeladmin, request, queryset):
    # exportem sets de proves (primer i abans de les proves, important)
    json_str = serializers.serialize('json', queryset, indent=2)
    json_str = json_str[:-2] + "," # eliminem el final del array json ] per concatenar
    # exportem proves (dp dels sets)
    queryset2 = Prova.objects.filter(set__in=queryset)
    json_str2 = serializers.serialize('json', queryset2, indent=2)
    json_str += json_str2[1:] # concatenem el 2n array sense [
    msg = "Exportat numero de sets="+str(len(queryset))
    modeladmin.message_user(request, msg, messages.SUCCESS)
    response = HttpResponse(json_str, content_type='application/json; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="export.json"'
    return response

class SetAdmin(admin.ModelAdmin):
    model = Set
    readonly_fields = ["creador"]
    list_display = ["nom","actiu","creador"]
    search_fields = ["nom","creador","categoria__nom"]
    inlines = [ProvaInline,]
    actions = [exporta_sets,]

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

#
# CUSTOM VIEWS
#
from django.views.generic import TemplateView
from django_custom_admin_pages.views.admin_base_view import AdminBaseView
from django import forms
from django.shortcuts import render
from django.apps import apps
import json

class ImportForm(forms.Form):
    sets_file = forms.FileField()

class ImportSets(AdminBaseView, TemplateView):
    view_name = "Importar sets de proves"
    template_name = "admin/import_sets.html"

    # Formulari d'importació
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = ImportForm()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = ImportForm(request.POST, request.FILES)
        context = self.get_context_data(*args, **kwargs)
        context['form'] = form
        if not form.is_valid():
            context['error'] = "Si us plau, selecciona un fitxer vàlid."
        else:
            try:
                dades_importades = ""
                mapa_pks = {} # per guardar pks antigues (claus) i noves
                # llegir dades JSON de l'arxiu i crear objectes del model
                arxiu = request.FILES['sets_file']
                dades = json.loads(arxiu.read())
                dadesStr = json.dumps(dades,indent=2)
                for item in dades:
                    if item["model"]=="tester.set":
                        pk_antiga = item["pk"]
                        camps = dict(item["fields"])
                        # Afegim marca de set importat
                        # TODO: afegir num per evitar repetició del nom
                        camps["nom"] = "IMPORTAT " + camps["nom"]
                        # eliminem la categoria per evitar problemes de m2m
                        del camps["categoria"]
                        obj = Set(**camps)
                        obj.pk = None
                        obj._state.adding = True
                        obj.save()
                        mapa_pks[pk_antiga] = obj.pk
                        # TODO: afegir item a la categoria IMPORTED
                    elif item["model"]=="tester.prova":
                        camps = dict(item["fields"])
                        # mapejem a nova PK del set
                        pk_set_antic = camps["set"]
                        mySet = Set.objects.get(pk=mapa_pks[pk_set_antic])
                        camps["set"] = mySet
                        obj = Prova(**camps)
                        obj.pk = None
                        obj._state.adding = True
                        obj.save()
                    else:
                        raise Exception("Objecte no identficat: "+str(type(dobj.object)))
                # preview dades carregades
                context["message"] = "Arxiu correcte. Dades importades:\n\n"
                context["message"] += dadesStr
            except Exception as e:
                context["error"] = "Error al llegir l'arxiu JSON. " + repr(e)
        
        return render(request, self.template_name, context)


admin.site.register_view(ImportSets)
