from django.db import models
from django.contrib.auth.models import User


class Categoria(models.Model):
    class Meta:
        verbose_name_plural = "categories"
    nom = models.CharField(max_length=200)
    descripcio = models.TextField(null=True,blank=True)
    def __str__(self):
        return self.nom

class Set(models.Model):
    nom = models.CharField(max_length=200)
    actiu = models.BooleanField(default=True)
    categoria = models.ManyToManyField(Categoria)
    creador = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    creacio = models.DateTimeField(auto_now=True)
    actualitzacio = models.DateTimeField(auto_now=True)
    descripcio = models.TextField(
                help_text="Descripció pública per a l'alumnat.")
    anotacions = models.TextField(null=True,blank=True,
                help_text="Anotacions privades del docent.")
    def __str__(self):
        return self.nom
    def save_model(self, request, instance, form, change):
        user = request.user
        if not change or not instance.creador:
            instance.creador = user
        instance.save()
        return instance

class Prova(models.Model):
    class Meta:
        verbose_name_plural = "proves"
    nom = models.CharField(max_length=200)
    activa = models.BooleanField(default=True)
    set = models.ForeignKey(Set,on_delete=models.CASCADE,null=True)
    creador = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    creacio = models.DateTimeField(auto_now=True)
    actualitzacio = models.DateTimeField(auto_now=True)
    descripcio = models.TextField(
                help_text="Descripció pública per a l'alumnat.")
    anotacions = models.TextField(null=True,blank=True,
                help_text="Anotacions privades per al professorat.")
    instruccio = models.TextField(
                help_text='"Comanda" a executar. Si s\'executa al servidor podeu emprar el codi "%IP" per referenciar la IP del client. No utilitzar cometes simples, o escapar-les amb \\ si son imprescindibles.')
    connexio_ssh = models.BooleanField(default=True,
                help_text="La instrucció s'executarà al client via SSH. Cal ajustar les claus SSH. Si no es selecciona, la instrucció s'excecutarà al servidor.")
    pes = models.FloatField(default=1.0);
    def __str__(self):
        return self.nom
    def save_model(self, request, instance, form, change):
        user = request.user
        if not change or not instance.creador:
            instance.creador = user
        instance.save()
        return instance

class Intent(models.Model):
    set = models.ForeignKey(Set,on_delete=models.CASCADE,null=True)
    alumne = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    resultat = models.FloatField(default=0.0,
                help_text="Percentatge de compleció de les proves")
    registre = models.TextField()
    data = models.DateTimeField(auto_now=True)
    ip = models.CharField(max_length=15)
    anotacions_alumne = models.TextField(null=True,blank=True,
                help_text="Anotacions i feedback de l'alumnat.")
    anotacions_docent = models.TextField(null=True,blank=True,
                help_text="Anotacions i feedback del docent.")
    def __str__(self):
        return "{} - {} {} ({})".format( self.set.nom, self.alumne.first_name,
                self.alumne.last_name, self.alumne.email)
    def nom_alumne(self):
        return "{} {} ({})".format( self.alumne.first_name,
                self.alumne.last_name, self.alumne.email)

