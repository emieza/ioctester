from django.db import models
from django.contrib.auth.models import User


class Categoria(models.Model):
	class Meta:
		verbose_name_plural = "categories"
	nom = models.CharField(max_length=200)
	descriocio = models.TextField(null=True,blank=True)

class Prova(models.Model):
	class Meta:
		verbose_name_plural = "proves"
	nom = models.CharField(max_length=200)
	creador = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
	creacio = models.DateTimeField(auto_now=True)
	actualitzacio = models.DateTimeField(auto_now=True)
	descripcio = models.TextField(
				help_text="Descripció pública per a l'alumnat.")
	anotacions = models.TextField(null=True,blank=True,
				help_text="Anotacions privades per al professorat.")
	instruccio = models.TextField(
				help_text='"Comanda" a executar. Si s\'executa al servidor podeu emprar el codi "%IP" per referenciar la IP del client.')
	connexio_ssh = models.BooleanField(default=True,
				help_text="La instrucció s'executarà al client via SSH. Cal ajustar les claus SSH. Si no es selecciona, la instrucció s'excecutarà al servidor.")

class Intent(models.Model):
	prova = models.ForeignKey(Prova,on_delete=models.SET_NULL,null=True)
	alumne = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
	resultat = models.FloatField(
				help_text="Percentatge de compleció de la prova")
	registre = models.TextField()
	data = models.DateTimeField(auto_now=True)
	ip = models.CharField(max_length=15)
	anotacions_alumne = models.TextField(null=True,blank=True,
				help_text="Anotacions i feedback de l'alumnat.")
	anotacions_docent = models.TextField(null=True,blank=True,
				help_text="Anotacions i feedback del docent.")

class Clau(models.Model):
	nom = models.CharField(max_length=200)
	prova = models.ForeignKey(Prova,on_delete=models.CASCADE)
	clau_publica = models.TextField()
	clau_privada = models.TextField()

