"""
Painel de resultados do facilitador (História 6 - Entrega 04).

Mostra como as pessoas estão jogando, para o facilitador saber quais cenários
funcionam e quais precisam de ajuste:
- taxa de conclusão por trilha (rodadas finalizadas ÷ rodadas iniciadas);
- pontuação média por trilha (só rodadas finalizadas);
- ponto de desistência: em qual cenário as rodadas não finalizadas pararam;
- adoção de IoT por cenário, com o cenário de menor adoção como "ponto de atenção";
- filtros por trilha e período, e exportação da tabela em CSV.

Fica dentro da área do facilitador (link "Resultados" no menu) e usa a mesma
proteção da História 4 (facilitador_required). Só lê o banco, não grava nada.
"""
import csv
from datetime import date, datetime, time, timedelta

from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from .gestao import facilitador_required
from .models import Cenario, Decisao, Rodada, Trilha


def _data(texto, rotulo, erros):
    """Converte 'AAAA-MM-DD' (formato do <input type=date>) em date; inválido vira erro."""
    texto = (texto or "").strip()
    if not texto:
        return None
    try:
        return date.fromisoformat(texto)
    except ValueError:
        erros.append(f"{rotulo} inválida. Use o formato dia/mês/ano.")
        return None


def _filtros(get):
    """Lê os filtros da URL (?trilha=&inicio=&fim=) e devolve (filtros, erros)."""
    erros = []
    trilha = Trilha.objects.filter(slug=get.get("trilha", "")).first()
    inicio = _data(get.get("inicio"), "Data inicial", erros)
    fim = _data(get.get("fim"), "Data final", erros)
    if inicio and fim and inicio > fim:
        erros.append("A data inicial não pode ser depois da data final.")
        inicio = fim = None
    return {"trilha": trilha, "inicio": inicio, "fim": fim}, erros


def _rodadas(filtros):
    """Rodadas que já escolheram uma trilha, dentro dos filtros."""
    rodadas = Rodada.objects.filter(trilha__isnull=False)
    if filtros["trilha"]:
        rodadas = rodadas.filter(trilha=filtros["trilha"])
    fuso = timezone.get_current_timezone()
    if filtros["inicio"]:
        rodadas = rodadas.filter(iniciada_em__gte=datetime.combine(filtros["inicio"], time.min, fuso))
    if filtros["fim"]:  # inclui o dia final inteiro
        fim = datetime.combine(filtros["fim"] + timedelta(days=1), time.min, fuso)
        rodadas = rodadas.filter(iniciada_em__lt=fim)
    return rodadas


def _por_trilha(rodadas):
    """Critérios 2 e 3: conclusão e pontuação média de cada trilha."""
    linhas = []
    contagens = (
        rodadas.values("trilha")
        .annotate(iniciadas=Count("id"), finalizadas=Count("id", filter=Q(finalizada_em__isnull=False)))
    )
    trilhas = Trilha.objects.in_bulk([c["trilha"] for c in contagens])
    for c in contagens:
        finalizadas = rodadas.filter(trilha_id=c["trilha"], finalizada_em__isnull=False)
        pontos = [r.pontuacao() for r in finalizadas]
        linhas.append({
            "trilha": trilhas[c["trilha"]],
            "iniciadas": c["iniciadas"],
            "finalizadas": c["finalizadas"],
            "conclusao": round(c["finalizadas"] * 100 / c["iniciadas"]),
            "media": round(sum(pontos) / len(pontos)) if pontos else None,
        })
    return sorted(linhas, key=lambda linha: linha["trilha"].numero)


def _desistencias(rodadas):
    """
    Critério 4: para cada rodada não finalizada, o cenário em que ela parou
    (o primeiro da trilha ainda sem decisão). Devolve {cenario_id: quantidade}.
    """
    paradas = {}
    for rodada in rodadas.filter(finalizada_em__isnull=True):
        respondidos = rodada.decisoes.values_list("cenario_id", flat=True)
        parou_em = rodada.cenarios().exclude(id__in=list(respondidos)).first()
        if parou_em is not None:
            paradas[parou_em.id] = paradas.get(parou_em.id, 0) + 1
    return paradas


def _por_cenario(rodadas, filtros):
    """Critérios 4 e 5: decisões, adoção de IoT e desistências de cada cenário."""
    decisoes = Decisao.objects.filter(rodada__in=rodadas)
    totais = {
        d["cenario"]: d
        for d in decisoes.values("cenario").annotate(
            total=Count("id"), iot=Count("id", filter=Q(opcao__usa_iot=True))
        )
    }
    paradas = _desistencias(rodadas)
    cenarios = Cenario.objects.select_related("trilha").order_by("trilha__numero", "ordem", "numero")
    if filtros["trilha"]:
        cenarios = cenarios.filter(trilha=filtros["trilha"])

    linhas = []
    for cenario in cenarios:
        dados = totais.get(cenario.id, {"total": 0, "iot": 0})
        desistencias = paradas.get(cenario.id, 0)
        if not dados["total"] and not desistencias:
            continue  # ninguém chegou neste cenário no filtro escolhido
        linhas.append({
            "cenario": cenario,
            "decisoes": dados["total"],
            "adocao": round(dados["iot"] * 100 / dados["total"]) if dados["total"] else None,
            "desistencias": desistencias,
            "atencao": False,
        })

    # Ponto de atenção: menor adoção de IoT (empate: o que aparece primeiro na trilha).
    com_decisoes = [linha for linha in linhas if linha["adocao"] is not None]
    if com_decisoes:
        min(com_decisoes, key=lambda linha: linha["adocao"])["atencao"] = True
    return linhas


def _csv(linhas_cenario, filtros):
    """Critério 7: a tabela filtrada em CSV (abre direto no Excel, separado por ;)."""
    nome = "resultados"
    if filtros["trilha"]:
        nome += f"-{filtros['trilha'].slug}"
    resposta = HttpResponse(content_type="text/csv; charset=utf-8")
    resposta["Content-Disposition"] = f'attachment; filename="{nome}.csv"'
    resposta.write("﻿")  # BOM: o Excel reconhece os acentos
    escritor = csv.writer(resposta, delimiter=";")
    escritor.writerow(["Trilha", "Rodada", "Cenário", "Título", "Decisões",
                       "Adoção de IoT (%)", "Desistências", "Ponto de atenção"])
    for linha in linhas_cenario:
        c = linha["cenario"]
        escritor.writerow([
            c.trilha.nome if c.trilha else "Sem trilha", c.ordem, c.numero, c.titulo,
            linha["decisoes"], "" if linha["adocao"] is None else linha["adocao"],
            linha["desistencias"], "sim" if linha["atencao"] else "",
        ])
    return resposta


@facilitador_required
def resultados(request):
    filtros, erros = _filtros(request.GET)
    rodadas = _rodadas(filtros)
    linhas_cenario = _por_cenario(rodadas, filtros)

    if request.GET.get("formato") == "csv":
        return _csv(linhas_cenario, filtros)

    return render(request, "simulador/gestao_resultados.html", {
        "filtros": filtros,
        "erros": erros,
        "trilhas": Trilha.objects.all(),
        "linhas_trilha": _por_trilha(rodadas),
        "linhas_cenario": linhas_cenario,
        "atencao": next((linha for linha in linhas_cenario if linha["atencao"]), None),
        "tem_dados": rodadas.exists(),
        "query_csv": _query_csv(request.GET),
    })


def _query_csv(get):
    """Mesma URL dos filtros, pedindo o CSV."""
    copia = get.copy()
    copia["formato"] = "csv"
    return copia.urlencode()
