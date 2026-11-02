"""
Gestão de cenários pelo facilitador (História 4 - Entrega 04).

O facilitador é o consultor da Bzu Tech que conversa com o cliente. Aqui ele
transforma a dor relatada em um cenário jogável: cadastra, edita, ativa/desativa
e exclui cenários com suas alternativas (Opcao) e as opiniões da equipe (Voz),
tudo por telas do sistema, sem mexer em código nem no banco.

Mesmas regras do resto do projeto:
- só views em função (sem generic views);
- sem Django Forms: os dados vêm direto de request.POST e são validados à mão;
- em caso de erro, a tela volta com a mensagem e com o que já foi digitado.

Quem é facilitador: superusuário ou usuário do grupo "Facilitadores"
(grupo criado pela migração 0006; o vínculo é feito em /admin/).
"""
from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Max
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import Cenario, Decisao, Opcao, Trilha, Voz

GRUPO_FACILITADORES = "Facilitadores"

MIN_OPCOES = 2
MAX_OPCOES = 4
LETRAS = "abcd"  # a posição da linha na tela define a letra da alternativa
VOZES_EM_BRANCO = 2  # linhas vazias oferecidas para novas opiniões da equipe
MAX_VOZES = 20
VALOR_MAXIMO = 1_000_000_000  # limite de sanidade para valores em R$ e horas


# ------------------------------------------------------------ acesso (critério 1)

def eh_facilitador(usuario):
    """Superusuário ou membro do grupo 'Facilitadores'."""
    if not usuario.is_authenticated:
        return False
    return usuario.is_superuser or usuario.groups.filter(name=GRUPO_FACILITADORES).exists()


def facilitador_required(view):
    """
    Protege uma view: sem login vai para a tela de login do facilitador;
    logado, mas sem ser facilitador, recebe 403 (acesso negado).
    """
    @wraps(view)
    def protegida(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), reverse("simulador:login_facilitador"))
        if not eh_facilitador(request.user):
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return protegida


def entrar(request):
    """Tela de login do facilitador (usuário e senha conferidos com authenticate)."""
    destino = request.POST.get("next") or request.GET.get("next") or ""
    if not url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()}):
        destino = ""

    if request.user.is_authenticated and eh_facilitador(request.user):
        return redirect(destino or "simulador:gestao_lista")

    erro = None
    usuario_digitado = ""
    if request.method == "POST":
        usuario_digitado = request.POST.get("usuario", "").strip()
        senha = request.POST.get("senha", "")
        usuario = authenticate(request, username=usuario_digitado, password=senha)
        if usuario is None:
            erro = "Usuário ou senha incorretos."
        elif not eh_facilitador(usuario):
            erro = "Este usuário não tem permissão de facilitador."
        else:
            login(request, usuario)
            return redirect(destino or "simulador:gestao_lista")

    return render(request, "simulador/gestao_login.html", {
        "erro": erro,
        "usuario_digitado": usuario_digitado,
        "next": destino,
    })


@require_POST
def sair(request):
    logout(request)
    return redirect("simulador:inicio")


# ------------------------------------------------------------ leitura do formulário

def _numero(texto, rotulo, erros, obrigatorio=True):
    """Converte texto em inteiro >= 0. Devolve None (e registra o erro) se for inválido."""
    texto = (texto or "").strip()
    if not texto:
        if obrigatorio:
            erros.append(f"{rotulo}: informe um valor.")
        return None
    if not texto.isdigit() or int(texto) > VALOR_MAXIMO:
        erros.append(f"{rotulo}: use um número inteiro maior ou igual a zero.")
        return None
    return int(texto)


def _valores_do_post(post, total_vozes):
    """Tudo que foi digitado, como texto, para a tela poder mostrar de novo."""
    return {
        "titulo": post.get("titulo", "").strip(),
        "setor": post.get("setor", "").strip(),
        "trilha": post.get("trilha", ""),
        "ordem": post.get("ordem", "").strip(),
        "problema": post.get("problema", "").strip(),
        "perda_atual": post.get("perda_atual", "").strip(),
        "conceito_titulo": post.get("conceito_titulo", "").strip(),
        "conceito_resumo": post.get("conceito_resumo", "").strip(),
        "conceito_passos": post.get("conceito_passos", "").strip(),
        "conceito_economia": post.get("conceito_economia", "").strip(),
        "ativo": post.get("ativo") == "on",
        "iot": post.get("iot", ""),
        "opcoes": [
            {
                "letra": letra,
                "texto": post.get(f"op_{letra}_texto", "").strip(),
                "custo": post.get(f"op_{letra}_custo", "").strip(),
                "perda_restante": post.get(f"op_{letra}_perda_restante", "").strip(),
                "horas_perdidas": post.get(f"op_{letra}_horas_perdidas", "").strip(),
                "explicacao": post.get(f"op_{letra}_explicacao", "").strip(),
            }
            for letra in LETRAS
        ],
        "vozes": [
            {
                "nome": post.get(f"voz_{i}_nome", "").strip(),
                "papel": post.get(f"voz_{i}_papel", "").strip(),
                "fala": post.get(f"voz_{i}_fala", "").strip(),
            }
            for i in range(total_vozes)
        ],
    }


def _valores_do_cenario(cenario):
    """Valores para a tela de edição (mesmo formato de _valores_do_post)."""
    por_letra = {o.letra: o for o in cenario.opcoes.all()}
    opcoes = []
    iot = ""
    for letra in LETRAS:
        o = por_letra.get(letra)
        opcoes.append({
            "letra": letra,
            "texto": o.texto if o else "",
            "custo": o.custo if o else "",
            "perda_restante": o.perda_restante if o else "",
            "horas_perdidas": o.horas_perdidas if o else "",
            "explicacao": o.explicacao if o else "",
        })
        if o and o.usa_iot:
            iot = letra
    vozes = [{"nome": v.nome, "papel": v.papel, "fala": v.fala} for v in cenario.vozes.all()]
    vozes += [{"nome": "", "papel": "", "fala": ""}] * VOZES_EM_BRANCO
    return {
        "titulo": cenario.titulo,
        "setor": cenario.setor,
        "trilha": cenario.trilha.slug if cenario.trilha_id else "",
        "ordem": cenario.ordem,
        "problema": cenario.problema,
        "perda_atual": cenario.perda_atual,
        "conceito_titulo": cenario.conceito_titulo,
        "conceito_resumo": cenario.conceito_resumo,
        "conceito_passos": cenario.conceito_passos,
        "conceito_economia": cenario.conceito_economia,
        "ativo": cenario.ativo,
        "iot": iot,
        "opcoes": opcoes,
        "vozes": vozes,
    }


def _valores_novos():
    return {
        "titulo": "", "setor": "", "trilha": "", "ordem": "", "problema": "", "perda_atual": "",
        "conceito_titulo": "", "conceito_resumo": "", "conceito_passos": "", "conceito_economia": "",
        "ativo": True,
        "iot": "",
        "opcoes": [
            {"letra": letra, "texto": "", "custo": "", "perda_restante": "",
             "horas_perdidas": "", "explicacao": ""}
            for letra in LETRAS
        ],
        "vozes": [{"nome": "", "papel": "", "fala": ""}] * (VOZES_EM_BRANCO + 1),
    }


def _validar(valores, cenario=None):
    """
    Confere os critérios de aceitação. Devolve (erros, dados), onde dados é o que
    será gravado (ou None se houve erro).
    """
    erros = []

    # Cenário (critério 2)
    textos_obrigatorios = [
        ("titulo", "Título", 120),
        ("setor", "Setor", 60),
        ("problema", "Descrição do problema", None),
        ("conceito_titulo", "Título do conceito de IoT", 120),
        ("conceito_resumo", "Resumo do conceito de IoT", None),
        ("conceito_passos", "Passos do conceito de IoT", None),
        ("conceito_economia", "Economia gerada pelo conceito de IoT", None),
    ]
    for campo, rotulo, limite in textos_obrigatorios:
        if not valores[campo]:
            erros.append(f"{rotulo}: preencha este campo.")
        elif limite and len(valores[campo]) > limite:
            erros.append(f"{rotulo}: use no máximo {limite} caracteres.")

    perda_atual = _numero(valores["perda_atual"], "Prejuízo mensal estimado (R$)", erros)
    ordem = _numero(valores["ordem"], "Posição na trilha", erros, obrigatorio=False)
    if ordem == 0:
        erros.append("Posição na trilha: use 1 ou mais.")

    trilha = Trilha.objects.filter(slug=valores["trilha"]).first()
    if trilha is None:
        erros.append("Escolha a trilha (segmento) em que o cenário vai aparecer.")

    # Alternativas (critério 3)
    preenchidas = []
    for linha in valores["opcoes"]:
        if any(linha[campo] != "" and linha[campo] is not None for campo in
               ("texto", "custo", "perda_restante", "horas_perdidas", "explicacao")):
            preenchidas.append(linha)

    if len(preenchidas) < MIN_OPCOES:
        erros.append(f"Cadastre pelo menos {MIN_OPCOES} alternativas.")
    # as alternativas têm de ocupar as primeiras linhas (A, B, C...), sem buracos
    letras_usadas = "".join(linha["letra"] for linha in preenchidas)
    if letras_usadas != LETRAS[: len(preenchidas)]:
        erros.append("Preencha as alternativas em ordem (A, depois B, depois C...), sem pular linhas.")

    opcoes = []
    for linha in preenchidas:
        letra = linha["letra"].upper()
        if not str(linha["texto"]).strip():
            erros.append(f"Alternativa {letra}: escreva o texto da alternativa.")
        elif len(str(linha["texto"])) > 200:
            erros.append(f"Alternativa {letra}: use no máximo 200 caracteres no texto.")
        if not str(linha["explicacao"]).strip():
            erros.append(f"Alternativa {letra}: escreva a explicação do que acontece.")
        custo = _numero(str(linha["custo"]), f"Alternativa {letra}, custo (R$/mês)", erros)
        restante = _numero(str(linha["perda_restante"]), f"Alternativa {letra}, prejuízo que continua (R$/mês)", erros)
        horas = _numero(str(linha["horas_perdidas"]), f"Alternativa {letra}, horas perdidas/mês", erros, obrigatorio=False)
        opcoes.append({
            "letra": linha["letra"],
            "texto": str(linha["texto"]).strip(),
            "custo": custo,
            "perda_restante": restante,
            "horas_perdidas": horas or 0,
            "explicacao": str(linha["explicacao"]).strip(),
            "usa_iot": linha["letra"] == valores["iot"],
        })

    # exatamente uma solução IoT (um único radio, então "exatamente" = "marcou uma que existe")
    if not any(o["usa_iot"] for o in opcoes):
        erros.append("Marque uma alternativa como solução IoT.")

    # Opiniões da equipe (critério 4): linha vazia é ignorada, meio preenchida é erro
    vozes = []
    for i, voz in enumerate(valores["vozes"], start=1):
        if not (voz["nome"] or voz["papel"] or voz["fala"]):
            continue
        if not (voz["nome"] and voz["papel"] and voz["fala"]):
            erros.append(f"Opinião da equipe {i}: preencha nome, cargo e fala (ou deixe a linha vazia).")
        elif len(voz["nome"]) > 60 or len(voz["papel"]) > 60:
            erros.append(f"Opinião da equipe {i}: nome e cargo aceitam até 60 caracteres.")
        else:
            vozes.append(voz)

    # Alternativas que já foram escolhidas por jogadores não podem sumir
    if cenario is not None:
        letras_novas = {o["letra"] for o in opcoes}
        for existente in cenario.opcoes.exclude(letra__in=letras_novas):
            if Decisao.objects.filter(opcao=existente).exists():
                erros.append(
                    f"A alternativa {existente.letra.upper()} já foi escolhida por jogadores e não pode "
                    "ser removida. Altere o texto dela em vez de apagar."
                )

    if erros:
        return erros, None
    return erros, {
        "trilha": trilha, "ordem": ordem, "perda_atual": perda_atual,
        "opcoes": opcoes, "vozes": vozes,
    }


# ------------------------------------------------------------ gravação

@transaction.atomic
def _gravar(valores, dados, cenario=None):
    """Cria ou atualiza o Cenario, as Opcao (por letra) e substitui as Voz."""
    if cenario is None:
        proximo = (Cenario.objects.aggregate(m=Max("numero"))["m"] or 0) + 1
        cenario = Cenario(numero=proximo)
        trilha_travada = False
    else:
        # Cenário que já foi jogado continua na mesma trilha (não mexe em partidas existentes).
        trilha_travada = Decisao.objects.filter(cenario=cenario).exists()

    if not trilha_travada:
        cenario.trilha = dados["trilha"]
    if dados["ordem"] is not None:
        cenario.ordem = dados["ordem"]
    elif cenario.pk is None:
        ultimo = Cenario.objects.filter(trilha=cenario.trilha).aggregate(m=Max("ordem"))["m"] or 0
        cenario.ordem = ultimo + 1

    cenario.titulo = valores["titulo"]
    cenario.setor = valores["setor"]
    cenario.problema = valores["problema"]
    cenario.perda_atual = dados["perda_atual"]
    cenario.conceito_titulo = valores["conceito_titulo"]
    cenario.conceito_resumo = valores["conceito_resumo"]
    cenario.conceito_passos = valores["conceito_passos"]
    cenario.conceito_economia = valores["conceito_economia"]
    cenario.ativo = valores["ativo"]
    cenario.save()

    # Opções são atualizadas pela letra (não apagadas e recriadas) para não perder
    # as Decisões de quem já jogou, que apontam para elas.
    letras = []
    for o in dados["opcoes"]:
        letras.append(o["letra"])
        Opcao.objects.update_or_create(
            cenario=cenario, letra=o["letra"],
            defaults={
                "texto": o["texto"], "custo": o["custo"], "perda_restante": o["perda_restante"],
                "horas_perdidas": o["horas_perdidas"], "explicacao": o["explicacao"],
                "usa_iot": o["usa_iot"],
            },
        )
    cenario.opcoes.exclude(letra__in=letras).delete()  # já validado: nenhuma delas tem decisões

    # Vozes não são referenciadas por nada: pode regravar a lista inteira.
    cenario.vozes.all().delete()
    for ordem, voz in enumerate(dados["vozes"], start=1):
        Voz.objects.create(cenario=cenario, nome=voz["nome"], papel=voz["papel"], fala=voz["fala"], ordem=ordem)
    return cenario


def _problemas_para_ativar(cenario):
    """Motivos pelos quais o cenário ainda não pode aparecer para os jogadores."""
    problemas = []
    total = cenario.opcoes.count()
    if not MIN_OPCOES <= total <= MAX_OPCOES:
        problemas.append(f"precisa ter de {MIN_OPCOES} a {MAX_OPCOES} alternativas (tem {total})")
    if cenario.opcoes.filter(usa_iot=True).count() != 1:
        problemas.append("precisa ter exatamente uma alternativa marcada como solução IoT")
    if cenario.trilha_id is None:
        problemas.append("precisa estar em uma trilha")
    return problemas


# ------------------------------------------------------------ telas

@facilitador_required
def lista(request):
    """Lista de todos os cenários (ativos e desativados) com as ações de gestão."""
    cenarios = (
        Cenario.objects.select_related("trilha")
        .annotate(n_opcoes=Count("opcoes", distinct=True), n_decisoes=Count("decisao", distinct=True))
        .order_by("trilha__numero", "ordem", "numero")
    )
    return render(request, "simulador/gestao_lista.html", {
        "cenarios": cenarios,
        "total_ativos": sum(1 for c in cenarios if c.ativo),
    })


def _tela_formulario(request, valores, erros, cenario=None):
    return render(request, "simulador/gestao_form.html", {
        "cenario": cenario,
        "valores": valores,
        "erros": erros,
        "trilhas": Trilha.objects.all(),
        "trilha_travada": cenario is not None and Decisao.objects.filter(cenario=cenario).exists(),
        "total_vozes": len(valores["vozes"]),
        "min_opcoes": MIN_OPCOES,
        "max_opcoes": MAX_OPCOES,
    })


def _processar_formulario(request, cenario=None):
    if request.method == "POST":
        try:
            total_vozes = max(0, min(MAX_VOZES, int(request.POST.get("total_vozes", "0"))))
        except ValueError:
            total_vozes = 0
        valores = _valores_do_post(request.POST, total_vozes)
        if cenario is not None and Decisao.objects.filter(cenario=cenario).exists():
            valores["trilha"] = cenario.trilha.slug if cenario.trilha_id else valores["trilha"]
        erros, dados = _validar(valores, cenario)
        if erros:
            if len(valores["vozes"]) < 1:
                valores["vozes"] = [{"nome": "", "papel": "", "fala": ""}]
            return _tela_formulario(request, valores, erros, cenario)
        gravado = _gravar(valores, dados, cenario)
        messages.success(request, f"Cenário “{gravado.titulo}” salvo.")
        return redirect("simulador:gestao_lista")

    valores = _valores_do_cenario(cenario) if cenario is not None else _valores_novos()
    return _tela_formulario(request, valores, [], cenario)


@facilitador_required
def novo(request):
    """Cadastrar um novo cenário (Cenário 4.1)."""
    return _processar_formulario(request)


@facilitador_required
def editar(request, numero):
    """Editar um cenário existente (Cenário 4.4)."""
    cenario = get_object_or_404(Cenario, numero=numero)
    return _processar_formulario(request, cenario)


@facilitador_required
@require_POST
def alternar(request, numero):
    """Ativa ou desativa o cenário (Cenário 4.5). Nunca apaga decisões."""
    cenario = get_object_or_404(Cenario, numero=numero)
    if cenario.ativo:
        cenario.ativo = False
        cenario.save(update_fields=["ativo"])
        messages.success(request, f"“{cenario.titulo}” foi desativado e não aparece mais para novos jogadores.")
    else:
        problemas = _problemas_para_ativar(cenario)
        if problemas:
            messages.error(request, f"Não dá para ativar “{cenario.titulo}”: {'; '.join(problemas)}.")
        else:
            cenario.ativo = True
            cenario.save(update_fields=["ativo"])
            messages.success(request, f"“{cenario.titulo}” está ativo e já aparece para os jogadores.")
    return redirect("simulador:gestao_lista")


@facilitador_required
@require_POST
def excluir(request, numero):
    """Exclui um cenário que ninguém jogou. Se já foi jogado, só dá para desativar."""
    cenario = get_object_or_404(Cenario, numero=numero)
    if Decisao.objects.filter(cenario=cenario).exists():
        messages.error(
            request,
            f"“{cenario.titulo}” já foi jogado e não pode ser excluído, para não apagar o histórico. Desative-o.",
        )
    else:
        titulo = cenario.titulo
        cenario.delete()
        messages.success(request, f"Cenário “{titulo}” excluído.")
    return redirect("simulador:gestao_lista")
