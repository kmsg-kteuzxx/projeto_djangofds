"""
Views do Simulador de Decisões IoT.

Fluxo de telas (wireframes do time de design):
  T1 inicio -> T2 como_funciona -> T3 trilhas
     -> [T4 cenario -> T5 resultado -> T6 progresso] x 5 rodadas
     -> T7 relatorio -> "Refazer simulação" volta para T1

Regras da disciplina seguidas aqui:
- Só views em função (sem generic views).
- Sem Django Forms: os dados vêm direto de request.POST e são validados à mão.
- Todas as histórias leem e/ou gravam no banco de dados.
"""
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Cenario, Decisao, Opcao, Rodada, Trilha

# Na sessão guardamos só o id da rodada atual; as decisões ficam no banco.
CHAVE_RODADA = "simulador_rodada_id"

TAMANHO_MAXIMO_NOME = 80
RODADAS_POR_TRILHA = 5


# ---------------------------------------------------------------- utilidades

def reais(valor):
    """Formata um número como dinheiro: 1500 -> 'R$ 1.500'."""
    texto = f"{abs(valor):,.0f}".replace(",", ".")
    sinal = "-" if valor < 0 else ""
    return f"{sinal}R$ {texto}"


def pontos_de_progresso(concluidos, total, atual=None):
    """Lista usada para desenhar os 'dots' de progresso das telas."""
    pontos = []
    for numero in range(1, total + 1):
        if numero <= concluidos:
            estado = "feito"
        elif numero == atual:
            estado = "atual"
        else:
            estado = "vazio"
        pontos.append(estado)
    return pontos


def metricas(perda_restante, custo):
    """Três métricas de um card (prejuízo que continua, custo e resultado)."""
    return {
        "perda_restante_fmt": reais(perda_restante),
        "custo_fmt": reais(custo),
    }


def impacto(opcao):
    """Impacto financeiro de uma alternativa, já formatado para o template."""
    return {
        **metricas(opcao.perda_restante, opcao.custo),
        "resultado": opcao.resultado,
        "resultado_fmt": reais(opcao.resultado),
        "positivo": opcao.resultado > 0,
    }


def rodada_atual(request):
    """Rodada guardada na sessão deste navegador (ou None)."""
    rodada_id = request.session.get(CHAVE_RODADA)
    if rodada_id is None:
        return None
    return Rodada.objects.filter(id=rodada_id).first()


def proximo_cenario_pendente(rodada):
    """Primeiro cenário da trilha que a rodada ainda não respondeu (ou None)."""
    respondidos = rodada.decisoes.values_list("cenario_id", flat=True)
    return rodada.cenarios().exclude(id__in=list(respondidos)).first()


def rodadas_por_trilha():
    """Quantas rodadas a maior trilha tem hoje (só cenários ativos). Padrão: 5."""
    contagens = Trilha.objects.annotate(
        n=Count("cenarios", filter=Q(cenarios__ativo=True))
    ).values_list("n", flat=True)
    return max(contagens, default=0) or RODADAS_POR_TRILHA


def posicao_na_rodada(rodada, cenario_atual):
    """Posição (1, 2, 3...) do cenário entre os da partida, já contando só os ativos."""
    ids = list(rodada.cenarios().values_list("id", flat=True))
    return ids.index(cenario_atual.id) + 1 if cenario_atual.id in ids else cenario_atual.ordem


def minutos_estimados(total_cenarios):
    """Tempo estimado da simulação (cerca de 1 minuto por rodada + leitura)."""
    return max(3, total_cenarios + 1)


def revisao_das_opcoes(cenario, escolha=None):
    """
    Todas as alternativas do cenário com números e explicação, para a pessoa
    entender por que a melhor opção é a melhor e o que deu errado nas outras.
    """
    opcoes = list(cenario.opcoes.all())
    melhor = max(opcoes, key=lambda o: o.resultado) if opcoes else None
    return [
        {
            "opcao": opcao,
            "impacto": impacto(opcao),
            "melhor": opcao == melhor,
            "escolhida": escolha is not None and opcao.id == escolha.id,
        }
        for opcao in opcoes
    ]


def exige_trilha(request):
    """
    Rodada atual já com trilha escolhida. Se faltar algo, devolve também para
    onde a pessoa deve ser levada (rodada, redirecionamento).
    """
    rodada = rodada_atual(request)
    if rodada is None:
        return None, redirect("simulador:inicio")
    if rodada.trilha_id is None:
        return rodada, redirect("simulador:trilhas")
    return rodada, None


# ------------------------------------------------- T1 e T2 (História 2)

def inicio(request):
    """T1: tela de abertura do simulador."""
    total = rodadas_por_trilha()
    return render(request, "simulador/inicio.html", {
        "total": total,
        "total_trilhas": Trilha.objects.count(),
        "minutos": minutos_estimados(total),
        "rodada": rodada_atual(request),
    })


def _tela_como_funciona(request, erros=None, valores=None):
    total = rodadas_por_trilha()
    return render(request, "simulador/como_funciona.html", {
        "total": total,
        "minutos": minutos_estimados(total),
        "pontos": pontos_de_progresso(0, total),
        "erros": erros or [],
        "valores": valores or {},
    })


def como_funciona(request):
    """T2: explica as etapas, como o desempenho é calculado e pede nome/empresa."""
    return _tela_como_funciona(request)


def comecar(request):
    """Recebe nome e empresa (sem Django Forms), cria a rodada e vai à escolha da trilha."""
    if request.method != "POST":
        return redirect("simulador:como_funciona")

    jogador = request.POST.get("jogador", "").strip()
    empresa = request.POST.get("empresa", "").strip()

    erros = []
    if not jogador:
        erros.append("Informe o seu nome.")
    if not empresa:
        erros.append("Informe o nome da empresa.")
    if len(jogador) > TAMANHO_MAXIMO_NOME or len(empresa) > TAMANHO_MAXIMO_NOME:
        erros.append(f"Use no máximo {TAMANHO_MAXIMO_NOME} caracteres em cada campo.")

    if erros:
        return _tela_como_funciona(request, erros, {"jogador": jogador, "empresa": empresa})

    rodada = Rodada.objects.create(jogador=jogador, empresa=empresa)
    request.session[CHAVE_RODADA] = rodada.id
    return redirect("simulador:trilhas")


# ------------------------------------------------- T3 (escolha da trilha)

def trilhas(request):
    """
    T3. GET: mostra os 6 segmentos para a pessoa escolher.
    POST: grava a trilha escolhida na rodada e leva à 1ª rodada dessa trilha.
    """
    rodada = rodada_atual(request)
    if rodada is None:
        return redirect("simulador:como_funciona")
    if rodada.finalizada:
        # Partida já terminada: para jogar de novo, começa uma nova pelo início.
        return redirect("simulador:inicio")

    erro = None
    if request.method == "POST":
        trilha = Trilha.objects.filter(slug=request.POST.get("trilha", "")).first()
        if trilha is not None and trilha.primeiro_cenario() is not None:
            if rodada.trilha_id != trilha.id:
                # Trocou de trilha no meio: as respostas da trilha anterior não valem mais.
                rodada.decisoes.all().delete()
                rodada.trilha = trilha
                rodada.save(update_fields=["trilha"])
            pendente = proximo_cenario_pendente(rodada) or trilha.primeiro_cenario()
            return redirect("simulador:cenario", numero=pendente.numero)
        erro = "Escolha uma das trilhas para continuar."

    return render(request, "simulador/trilhas.html", {
        "trilhas": Trilha.objects.all(),
        "rodada": rodada,
        "erro": erro,
    })


# ------------------------------------------------- T4 e T5 (História 1)

def cenario(request, numero):
    """
    T4. GET: mostra a situação, as vozes da equipe e as alternativas.
    POST: grava a decisão escolhida no banco e leva à consequência (T5).
    """
    rodada, desvio = exige_trilha(request)
    if desvio:
        return desvio
    if rodada.finalizada:
        return redirect("simulador:relatorio")

    cenario_atual = get_object_or_404(Cenario, numero=numero)
    if cenario_atual.trilha_id != rodada.trilha_id:
        # Cenário de outra trilha: volta para a rodada que falta na trilha escolhida.
        pendente = proximo_cenario_pendente(rodada)
        if pendente is None:
            return redirect("simulador:relatorio")
        return redirect("simulador:cenario", numero=pendente.numero)
    if not cenario_atual.ativo and not rodada.decisoes.filter(cenario=cenario_atual).exists():
        # Cenário desativado pelo facilitador: segue para a próxima rodada que está valendo.
        pendente = proximo_cenario_pendente(rodada)
        if pendente is None:
            return redirect("simulador:relatorio")
        return redirect("simulador:cenario", numero=pendente.numero)
    erro = None
    tem_dados = bool(cenario_atual.dados_sensor.strip())
    # História 5: os dados aparecem só quando o jogador pede (?dados=1). Funciona sem JavaScript.
    mostrar_dados = tem_dados and request.GET.get("dados") == "1"

    if request.method == "POST":
        letra = request.POST.get("opcao", "")
        opcao = Opcao.objects.filter(cenario=cenario_atual, letra=letra).first()
        viu_dados = tem_dados and request.POST.get("viu_dados") == "1"
        if viu_dados:
            mostrar_dados = True  # em caso de erro, os dados continuam abertos
        if opcao is not None:
            anterior = Decisao.objects.filter(rodada=rodada, cenario=cenario_atual).first()
            if anterior is not None and anterior.viu_dados_sensor:
                viu_dados = True  # mudou de ideia: continua contando que já consultou
            Decisao.objects.update_or_create(
                rodada=rodada,
                cenario=cenario_atual,
                defaults={"opcao": opcao, "viu_dados_sensor": viu_dados},
            )
            return redirect("simulador:resultado", numero=numero)
        erro = "Escolha uma das alternativas para continuar."

    total = rodada.cenarios().count()
    posicao = posicao_na_rodada(rodada, cenario_atual)
    return render(request, "simulador/cenario.html", {
        "cenario": cenario_atual,
        "vozes": cenario_atual.vozes.all(),
        "opcoes": [
            {"letra": o.letra, "texto": o.texto, "custo_fmt": reais(o.custo)}
            for o in cenario_atual.opcoes.all()
        ],
        "posicao": posicao,
        "total": total,
        "trilha": rodada.trilha,
        "pontos": pontos_de_progresso(posicao - 1, total, atual=posicao),
        "perda_atual_fmt": reais(cenario_atual.perda_atual),
        "tem_dados": tem_dados,
        "mostrar_dados": mostrar_dados,
        "erro": erro,
    })


def resultado(request, numero):
    """T5: consequência da decisão, comparando sem IoT × com IoT."""
    rodada, desvio = exige_trilha(request)
    if desvio:
        return desvio

    cenario_atual = get_object_or_404(Cenario, numero=numero, trilha_id=rodada.trilha_id)
    decisao = Decisao.objects.filter(rodada=rodada, cenario=cenario_atual).select_related("opcao").first()
    if decisao is None:
        return redirect("simulador:cenario", numero=numero)

    escolha = decisao.opcao
    iot = cenario_atual.opcao_iot()

    if escolha.usa_iot or iot is None:
        # Escolheu IoT: compara com a situação de antes, sem dados.
        comparacao = {
            "titulo": "Sem dados · Como estava",
            "texto": "Sem nenhuma mudança, o problema continuava custando isso todo mês.",
            **metricas(cenario_atual.perda_atual, 0),
            "resultado_fmt": reais(0),
            "positivo": False,
            "tipo": "sem",
        }
        ganho_extra = escolha.resultado
        texto_ganho = "Prejuízo evitado com a sua decisão"
    else:
        comparacao = {
            "titulo": "Com IoT · O que mudaria",
            "texto": iot.texto,
            **impacto(iot),
            "tipo": "com",
        }
        ganho_extra = iot.resultado - escolha.resultado
        texto_ganho = "Prejuízo a mais que a IoT evitaria"

    total = rodada.cenarios().count()
    posicao = posicao_na_rodada(rodada, cenario_atual)

    return render(request, "simulador/resultado.html", {
        "cenario": cenario_atual,
        "escolha": escolha,
        "impacto": impacto(escolha),
        "iot": iot,
        "comparacao": comparacao,
        "ganho_extra_fmt": reais(max(0, ganho_extra)),
        "texto_ganho": texto_ganho,
        "revisao": revisao_das_opcoes(cenario_atual, escolha),
        "posicao": posicao,
        "total": total,
        "trilha": rodada.trilha,
        "pontos": pontos_de_progresso(posicao, total),
        "ultima": proximo_cenario_pendente(rodada) is None,
    })


# ------------------------------------------------- T6 (acompanhamento entre rodadas)

def progresso(request):
    """T6: quantas rodadas já foram e o prejuízo acumulado até aqui."""
    rodada, desvio = exige_trilha(request)
    if desvio:
        return desvio

    pendente = proximo_cenario_pendente(rodada)
    if pendente is None:
        return redirect("simulador:relatorio")

    total = rodada.cenarios().count()
    decisoes = list(rodada.decisoes.select_related("opcao", "cenario"))
    concluidas = len(decisoes)
    acumulado = sum(d.opcao.perda_restante for d in decisoes)
    acumulado_iot = sum((d.cenario.opcao_iot() or d.opcao).perda_restante for d in decisoes)

    return render(request, "simulador/progresso.html", {
        "trilha": rodada.trilha,
        "concluidas": concluidas,
        "total": total,
        "porcentagem": round(concluidas * 100 / total) if total else 0,
        "acumulado_fmt": reais(acumulado),
        "acumulado_iot_fmt": reais(acumulado_iot),
        "decisoes_iot": sum(1 for d in decisoes if d.opcao.usa_iot),
        "proximo": pendente,
    })


# ------------------------------------------------- T7 (História 1)

def diagnostico(rodada, itens, acertos):
    """Os 2 parágrafos do card de diagnóstico do segmento (T7)."""
    trilha = rodada.trilha
    primeiro = trilha.diagnostico if trilha else (
        "Em qualquer segmento, decidir com dados significa medir antes de agir: "
        "descobrir a causa real do problema antes de gastar com a solução."
    )
    total = len(itens)
    erradas = [item["cenario"].titulo for item in itens if not item["acertou"]]
    if total and acertos == total:
        segundo = (
            f"Você escolheu a solução baseada em dados nas {total} rodadas. É exatamente "
            f"esse raciocínio que a Bzu Tech leva para empresas como a {rodada.empresa}: "
            "primeiro medir, depois decidir."
        )
    elif acertos == 0:
        segundo = (
            f"Nesta simulação, nenhuma das decisões usou dados em tempo real. Não é "
            f"falta de experiência: sem medição, todo mundo decide no escuro. Revise as "
            f"rodadas abaixo e veja quanto a {rodada.empresa} deixaria de perder."
        )
    else:
        exemplos = "; ".join(f"“{titulo}”" for titulo in erradas[:2])
        segundo = (
            f"Você acertou o caminho dos dados em {acertos} de {total} rodadas. As "
            f"maiores oportunidades estão em situações como {exemplos}, onde a "
            "intuição levou a uma solução mais cara. Abra essas rodadas abaixo para "
            "entender cada opção."
        )
    return [primeiro, segundo]


def _montar_relatorio(request, rodada, eh_meu):
    itens = []
    sua = {"perda": 0, "custo": 0, "resultado": 0}
    bzu = {"perda": 0, "custo": 0, "resultado": 0}

    for decisao in rodada.decisoes.select_related("cenario", "opcao__cenario"):
        escolha = decisao.opcao
        iot = decisao.cenario.opcao_iot() or escolha
        sua["perda"] += escolha.perda_restante
        sua["custo"] += escolha.custo
        sua["resultado"] += escolha.resultado
        bzu["perda"] += iot.perda_restante
        bzu["custo"] += iot.custo
        bzu["resultado"] += iot.resultado
        itens.append({
            "cenario": decisao.cenario,
            "escolha": escolha,
            "melhor": iot,
            "acertou": escolha.id == iot.id,
            "impacto": impacto(escolha),
            "impacto_iot": impacto(iot),
            "revisao": revisao_das_opcoes(decisao.cenario, escolha),
        })

    diferenca = bzu["resultado"] - sua["resultado"]
    acertos = sum(1 for item in itens if item.get("acertou"))
    return render(request, "simulador/relatorio.html", {
        "rodada": rodada,
        "trilha": rodada.trilha,
        "eh_meu": eh_meu,
        "itens": itens,
        "total": len(itens),
        "acertos_iot": rodada.decisoes_iot(),
        "decisoes_com_dados": rodada.decisoes_com_dados(),
        "diagnostico": diagnostico(rodada, itens, acertos),
        "pontuacao": rodada.pontuacao(),
        "sua": {
            "perda_fmt": reais(sua["perda"]),
            "custo_fmt": reais(sua["custo"]),
            "resultado_fmt": reais(sua["resultado"]),
        },
        "bzu": {
            "perda_fmt": reais(bzu["perda"]),
            "custo_fmt": reais(bzu["custo"]),
            "resultado_fmt": reais(bzu["resultado"]),
        },
        "resultado_anual_fmt": reais(sua["resultado"] * 12),
        "resultado_positivo": sua["resultado"] > 0,
        "diferenca": diferenca,
        "diferenca_fmt": reais(diferenca),
        "diferenca_anual_fmt": reais(diferenca * 12),
    })


def relatorio(request):
    """T7: resultado final da rodada atual. Marca a rodada como finalizada."""
    rodada, desvio = exige_trilha(request)
    if desvio:
        return desvio

    pendente = proximo_cenario_pendente(rodada)
    if pendente is not None:
        return redirect("simulador:cenario", numero=pendente.numero)

    if not rodada.finalizada:
        rodada.finalizada_em = timezone.now()
        rodada.save(update_fields=["finalizada_em"])

    return _montar_relatorio(request, rodada, eh_meu=True)


# ------------------------------------------------- Ranking (História 3)

def ranking(request):
    """Ranking das rodadas finalizadas por toda a equipe (pode filtrar por trilha)."""
    filtro = Trilha.objects.filter(slug=request.GET.get("trilha", "")).first()
    rodadas = Rodada.objects.filter(finalizada_em__isnull=False).select_related("trilha")
    if filtro is not None:
        rodadas = rodadas.filter(trilha=filtro)

    linhas = []
    for rodada in rodadas:
        resultado_total = rodada.resultado_total()
        linhas.append({
            "rodada": rodada,
            "pontuacao": rodada.pontuacao(),
            "decisoes_iot": rodada.decisoes_iot(),
            "total_cenarios": rodada.cenarios().count(),
            "resultado_fmt": reais(resultado_total),
            "positivo": resultado_total > 0,
        })
    linhas.sort(key=lambda linha: (-linha["pontuacao"], linha["rodada"].finalizada_em))

    for posicao, linha in enumerate(linhas, start=1):
        linha["posicao"] = posicao

    minha = rodada_atual(request)
    return render(request, "simulador/ranking.html", {
        "linhas": linhas,
        "trilhas": Trilha.objects.all(),
        "filtro": filtro,
        "minha_rodada_id": minha.id if minha else None,
    })


def rodada_detalhe(request, rodada_id):
    """Resultado final de uma rodada finalizada de outra pessoa (vindo do ranking)."""
    rodada = get_object_or_404(Rodada, id=rodada_id, finalizada_em__isnull=False)
    minha = rodada_atual(request)
    return _montar_relatorio(request, rodada, eh_meu=(minha is not None and minha.id == rodada.id))
