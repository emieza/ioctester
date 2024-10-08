# Generated by Django 4.2 on 2024-09-05 11:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=200)),
                ('descriocio', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Prova',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=200)),
                ('creacio', models.DateTimeField(auto_now=True)),
                ('actualitzacio', models.DateTimeField(auto_now=True)),
                ('descripcio', models.TextField(help_text="Descripció pública per a l'alumnat.")),
                ('anotacions', models.TextField(blank=True, help_text='Anotacions privades per al professorat.', null=True)),
                ('instruccio', models.TextField(help_text='"Comanda" a executar. Si s\'executa al servidor podeu emprar el codi "%IP" per referenciar la IP del client.')),
                ('connexio_ssh', models.BooleanField(default=True, help_text="La instrucció s'executarà al client via SSH. Cal ajustar les claus SSH. Si no es selecciona, la instrucció s'excecutarà al servidor.")),
                ('creador', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Intent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resultat', models.FloatField(help_text='Percentatge de compleció de la prova')),
                ('registre', models.TextField()),
                ('data', models.DateTimeField(auto_now=True)),
                ('ip', models.CharField(max_length=15)),
                ('anotacions_alumne', models.TextField(blank=True, help_text="Anotacions i feedback de l'alumnat.", null=True)),
                ('anotacions_docent', models.TextField(blank=True, help_text='Anotacions i feedback del docent.', null=True)),
                ('alumne', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('prova', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tester.prova')),
            ],
        ),
        migrations.CreateModel(
            name='Clau',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=200)),
                ('clau_publica', models.TextField()),
                ('clau_privada', models.TextField()),
                ('prova', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tester.prova')),
            ],
        ),
    ]
