from django.contrib import admin

from .models import Cenario, Decisao, Opcao, Rodada, Trilha, Voz


class VozInline(admin.TabularInline):
    model = Voz
    extra = 0


class OpcaoInline(admin.TabularInline):
    model = Opcao
    extra = 0


@admin.register(Trilha)
class TrilhaAdmin(admin.ModelAdmin):
    list_display = ("numero", "nome", "slug")


@admin.register(Cenario)
class CenarioAdmin(admin.ModelAdmin):
    list_display = ("numero", "trilha", "ordem", "titulo", "setor", "perda_atual", "ativo")
    list_filter = ("trilha", "ativo")
    inlines = [VozInline, OpcaoInline]


class DecisaoInline(admin.TabularInline):
    model = Decisao
    extra = 0


@admin.register(Rodada)
class RodadaAdmin(admin.ModelAdmin):
    list_display = ("jogador", "empresa", "trilha", "iniciada_em", "finalizada_em")
    inlines = [DecisaoInline]
