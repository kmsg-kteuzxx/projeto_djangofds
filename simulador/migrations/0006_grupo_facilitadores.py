"""
Cria o grupo "Facilitadores" (História 4 - Entrega 04).

Quem está nesse grupo (ou é superusuário) acessa as telas de gestão de cenários
em /simulador/facilitador/. Para dar acesso a alguém: /admin/ -> Usuários ->
escolher o usuário -> Grupos -> Facilitadores.
"""
from django.db import migrations

NOME_DO_GRUPO = "Facilitadores"


def criar_grupo(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name=NOME_DO_GRUPO)


def remover_grupo(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name=NOME_DO_GRUPO).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0001_initial"),
        ("simulador", "0005_gestao_cenarios"),
    ]

    operations = [
        migrations.RunPython(criar_grupo, remover_grupo),
    ]
