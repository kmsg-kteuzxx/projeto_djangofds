from django.urls import path
from . import gestao, painel, views

app_name = "simulador"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("como-funciona/", views.como_funciona, name="como_funciona"),
    path("comecar/", views.comecar, name="comecar"),
    path("trilhas/", views.trilhas, name="trilhas"),
    path("cenario/<int:numero>/", views.cenario, name="cenario"),
    path("cenario/<int:numero>/resultado/", views.resultado, name="resultado"),
    path("progresso/", views.progresso, name="progresso"),
    path("relatorio/", views.relatorio, name="relatorio"),
    path("ranking/", views.ranking, name="ranking"),
    path("rodada/<int:rodada_id>/", views.rodada_detalhe, name="rodada"),
    # Gestão de cenários pelo facilitador (História 4)
    path("facilitador/entrar/", gestao.entrar, name="login_facilitador"),
    path("facilitador/sair/", gestao.sair, name="logout_facilitador"),
    path("facilitador/", gestao.lista, name="gestao_lista"),
    path("facilitador/cenarios/novo/", gestao.novo, name="gestao_novo"),
    path("facilitador/cenarios/<int:numero>/editar/", gestao.editar, name="gestao_editar"),
    path("facilitador/cenarios/<int:numero>/alternar/", gestao.alternar, name="gestao_alternar"),
    path("facilitador/cenarios/<int:numero>/excluir/", gestao.excluir, name="gestao_excluir"),
    # Painel de resultados do facilitador (História 6)
    path("facilitador/resultados/", painel.resultados, name="gestao_resultados"),
]
