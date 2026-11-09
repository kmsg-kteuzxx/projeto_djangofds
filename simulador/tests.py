"""
Testes das histórias implementadas nas Entregas 03 e 04 (ver historias.md).
Cada classe corresponde a uma história e cada teste a um cenário BDD.

Para rodar:  python manage.py test simulador
O banco de teste é criado com as migrações, então os cenários iniciais
(migração 0002) já estão disponíveis.
"""
from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .models import Cenario, Decisao, Opcao, Rodada, Trilha, Voz
from .views import CHAVE_RODADA, reais


class Base(TestCase):
    TRILHA = "saude"  # a trilha "Saúde e Cadeia Fria" começa pelo cenário 1

    def comecar(self, jogador="João", empresa="Distribuidora Recife", trilha=TRILHA):
        resposta = self.client.post(reverse("simulador:comecar"), {"jogador": jogador, "empresa": empresa})
        if trilha and Rodada.objects.filter(jogador=jogador, empresa=empresa).exists():
            self.escolher_trilha(trilha)
        return resposta

    def escolher_trilha(self, slug):
        return self.client.post(reverse("simulador:trilhas"), {"trilha": slug})

    def responder(self, numero, letra):
        return self.client.post(reverse("simulador:cenario", args=[numero]), {"opcao": letra})

    def cenarios_da_trilha(self, slug=TRILHA):
        return Cenario.objects.filter(trilha__slug=slug)

    def jogar_rodada(self, usar_iot=False, trilha=TRILHA, **dados):
        self.comecar(trilha=trilha, **dados)
        for cenario in self.cenarios_da_trilha(trilha):
            opcao = cenario.opcoes.filter(usa_iot=usar_iot).first()
            self.responder(cenario.numero, opcao.letra)
        return self.client.get(reverse("simulador:relatorio"))


# ---------------------------------------------------------------- História 1

class H1SimuladorDeDecisoesTest(Base):
    """História 1: simulador de decisões com IoT."""

    def test_cenarios_iniciais_estao_no_banco_e_todos_tem_opcao_iot(self):
        self.assertGreaterEqual(Cenario.objects.count(), 3)
        for cenario in Cenario.objects.all():
            self.assertGreaterEqual(cenario.opcoes.count(), 2)
            self.assertIsNotNone(cenario.opcao_iot(), f"Cenário {cenario.numero} sem opção IoT")

    def test_dado_que_comecei_entao_vejo_problema_vozes_e_alternativas(self):
        self.comecar()
        cenario = Cenario.objects.first()
        resposta = self.client.get(reverse("simulador:cenario", args=[cenario.numero]))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, cenario.titulo)
        self.assertContains(resposta, "Alex")
        for opcao in cenario.opcoes.all():
            self.assertContains(resposta, opcao.texto)

    def test_quando_clico_em_uma_alternativa_a_decisao_e_gravada_com_1_clique(self):
        self.comecar()
        resposta = self.responder(1, "b")
        self.assertRedirects(resposta, reverse("simulador:resultado", args=[1]))
        decisao = Decisao.objects.get()
        self.assertEqual(decisao.opcao.letra, "b")
        self.assertEqual(decisao.cenario.numero, 1)

    def test_decidir_leva_2_cliques_escolher_e_confirmar(self):
        # 1º clique: seleciona a alternativa (radio). 2º clique: "Confirmar decisão".
        self.comecar()
        resposta = self.client.get(reverse("simulador:cenario", args=[1]))
        total_opcoes = Cenario.objects.get(numero=1).opcoes.count()
        self.assertContains(resposta, 'type="radio" name="opcao"', count=total_opcoes)
        self.assertContains(resposta, "Confirmar decisão")
        self.assertContains(resposta, "Rodada 1 de 5")

    def test_alternativa_invalida_mostra_mensagem_e_nao_grava(self):
        self.comecar()
        resposta = self.responder(1, "z")
        self.assertContains(resposta, "Escolha uma das alternativas")
        self.assertEqual(Decisao.objects.count(), 0)

    def test_mudar_de_ideia_atualiza_a_decisao_em_vez_de_duplicar(self):
        self.comecar()
        self.responder(1, "a")
        self.responder(1, "b")
        self.assertEqual(Decisao.objects.count(), 1)
        self.assertEqual(Decisao.objects.get().opcao.letra, "b")

    def test_quando_escolho_entao_vejo_o_impacto_financeiro_na_hora(self):
        self.comecar()
        resposta = self.client.post(reverse("simulador:cenario", args=[1]), {"opcao": "a"}, follow=True)
        opcao = Cenario.objects.get(numero=1).opcoes.get(letra="a")
        self.assertContains(resposta, "Veja o que aconteceu")
        self.assertContains(resposta, "Sem IoT · Sua decisão")
        self.assertContains(resposta, reais(opcao.custo))
        self.assertContains(resposta, reais(opcao.perda_restante))
        self.assertContains(resposta, reais(opcao.resultado))

    def test_calculo_do_resultado_financeiro(self):
        opcao = Cenario.objects.get(numero=1).opcoes.get(letra="a")  # 18.000 - 9.000 - 4.500
        self.assertEqual(opcao.economia, 9000)
        self.assertEqual(opcao.resultado, 4500)

    def test_quando_nao_escolho_iot_entao_vejo_como_a_iot_resolveria(self):
        self.comecar()
        cenario = Cenario.objects.get(numero=1)
        sem_iot = cenario.opcoes.filter(usa_iot=False).first()
        resposta = self.client.post(
            reverse("simulador:cenario", args=[1]), {"opcao": sem_iot.letra}, follow=True
        )
        self.assertContains(resposta, "Com IoT · O que mudaria")
        self.assertContains(resposta, cenario.opcao_iot().texto)

    def test_quando_escolho_iot_entao_comparo_com_a_situacao_sem_dados(self):
        self.comecar()
        cenario = Cenario.objects.get(numero=1)
        resposta = self.client.post(
            reverse("simulador:cenario", args=[1]), {"opcao": cenario.opcao_iot().letra}, follow=True
        )
        self.assertContains(resposta, "Com IoT · Sua decisão")
        self.assertContains(resposta, "Sem dados · Como estava")
        self.assertContains(resposta, reais(cenario.perda_atual))

    def test_resultado_sem_escolha_volta_para_o_cenario(self):
        self.comecar()
        segundo = self.cenarios_da_trilha()[1]
        resposta = self.client.get(reverse("simulador:resultado", args=[segundo.numero]))
        self.assertRedirects(resposta, reverse("simulador:cenario", args=[segundo.numero]))

    def test_relatorio_explica_o_conceito_de_cada_cenario(self):
        resposta = self.jogar_rodada()
        self.assertContains(resposta, "Veja o que a Bzu teria feito diferente")
        self.assertContains(resposta, "Sem IoT · Sua jornada")
        self.assertContains(resposta, "Com Bzu IoT · O que mudaria")
        for cenario in self.cenarios_da_trilha():
            self.assertContains(resposta, cenario.conceito_titulo)
            self.assertContains(resposta, cenario.lista_passos[0])

    def test_relatorio_antes_de_terminar_leva_ao_cenario_que_falta(self):
        self.comecar()
        self.responder(1, "a")
        resposta = self.client.get(reverse("simulador:relatorio"))
        segundo = self.cenarios_da_trilha()[1]
        self.assertRedirects(resposta, reverse("simulador:cenario", args=[segundo.numero]))

    def test_relatorio_marca_a_rodada_como_finalizada(self):
        self.jogar_rodada()
        self.assertIsNotNone(Rodada.objects.get().finalizada_em)

    def test_cenario_inexistente_retorna_404(self):
        self.comecar()
        resposta = self.client.get(reverse("simulador:cenario", args=[999]))
        self.assertEqual(resposta.status_code, 404)

    def test_relatorio_tem_botoes_saber_mais_e_refazer(self):
        resposta = self.jogar_rodada()
        self.assertContains(resposta, "Quero saber mais sobre a Bzu Tech")
        self.assertContains(resposta, "https://www.bzutech.com.br")
        self.assertContains(resposta, "Refazer simulação")

    def test_paginas_abrem_logo_apos_o_deploy_sem_cadastro_manual(self):
        for url in ["/", reverse("simulador:inicio"), reverse("simulador:como_funciona"), reverse("simulador:ranking")]:
            self.assertEqual(self.client.get(url).status_code, 200, url)


# ---------------------------------------------------------------- História 2

class H2IdentificacaoDoJogadorTest(Base):
    """História 2: identificar jogador e empresa antes de jogar."""

    def test_dado_nome_e_empresa_quando_comeco_entao_a_rodada_e_gravada(self):
        resposta = self.comecar("Maria", "Frigorífico Boa Vista")
        rodada = Rodada.objects.get()
        self.assertEqual(rodada.jogador, "Maria")
        self.assertEqual(rodada.empresa, "Frigorífico Boa Vista")
        self.assertEqual(self.client.session[CHAVE_RODADA], rodada.id)
        self.assertRedirects(resposta, reverse("simulador:trilhas"))

    def test_tela_como_funciona_explica_e_pede_nome_e_empresa(self):
        resposta = self.client.get(reverse("simulador:como_funciona"))
        self.assertContains(resposta, "Como seu desempenho é calculado")
        self.assertContains(resposta, 'name="jogador"')
        self.assertContains(resposta, 'name="empresa"')

    def test_inicio_leva_para_como_funciona(self):
        resposta = self.client.get(reverse("simulador:inicio"))
        self.assertContains(resposta, reverse("simulador:como_funciona"))
        self.assertContains(resposta, "Tempo estimado")

    def test_sem_nome_nao_comeca_e_mostra_erro(self):
        resposta = self.comecar("", "Empresa X")
        self.assertContains(resposta, "Informe o seu nome.")
        self.assertEqual(Rodada.objects.count(), 0)

    def test_sem_empresa_nao_comeca_e_mantem_o_nome_digitado(self):
        resposta = self.comecar("Maria", "   ")
        self.assertContains(resposta, "Informe o nome da empresa.")
        self.assertContains(resposta, 'value="Maria"')
        self.assertEqual(Rodada.objects.count(), 0)

    def test_nome_muito_longo_e_recusado(self):
        resposta = self.comecar("A" * 81, "Empresa X")
        self.assertContains(resposta, "no máximo 80 caracteres")
        self.assertEqual(Rodada.objects.count(), 0)

    def test_sem_se_identificar_nao_acessa_os_cenarios(self):
        resposta = self.client.get(reverse("simulador:cenario", args=[1]))
        self.assertRedirects(resposta, reverse("simulador:inicio"))

    def test_relatorio_mostra_o_nome_da_empresa(self):
        resposta = self.jogar_rodada(jogador="Maria", empresa="Frigorífico Boa Vista")
        self.assertContains(resposta, "Relatório de aprendizado da <strong>Frigorífico Boa Vista</strong>", html=False)
        self.assertContains(resposta, "<strong>Maria</strong>", html=False)

    def test_nova_rodada_nao_apaga_a_anterior(self):
        self.jogar_rodada(jogador="Maria")
        self.comecar("Maria", "Outra empresa")
        self.assertEqual(Rodada.objects.count(), 2)


# ---------------------------------------------------------------- História 3

class H3RankingDaEquipeTest(Base):
    """História 3: ranking das rodadas da equipe."""

    def test_ranking_vazio_mostra_convite(self):
        resposta = self.client.get(reverse("simulador:ranking"))
        self.assertContains(resposta, "Ninguém concluiu uma simulação ainda")

    def test_rodada_finalizada_aparece_no_ranking(self):
        self.jogar_rodada(jogador="Maria", empresa="Empresa M")
        resposta = self.client.get(reverse("simulador:ranking"))
        self.assertContains(resposta, "Maria")
        self.assertContains(resposta, "Empresa M")

    def test_rodada_em_andamento_nao_aparece_no_ranking(self):
        self.comecar("Pedro", "Empresa P")
        self.responder(1, "a")
        resposta = self.client.get(reverse("simulador:ranking"))
        self.assertNotContains(resposta, "Pedro")

    def test_ranking_ordena_pela_maior_pontuacao(self):
        self.jogar_rodada(usar_iot=False, jogador="Sem Dados")
        self.jogar_rodada(usar_iot=True, jogador="Com Dados")
        html = self.client.get(reverse("simulador:ranking")).content.decode()
        self.assertLess(html.index("Com Dados"), html.index("Sem Dados"))

    def test_ranking_mostra_a_trilha_e_filtra_por_ela(self):
        self.jogar_rodada(jogador="Ana Saúde", trilha="saude")
        self.client = self.client_class()
        self.jogar_rodada(jogador="Beto Agro", trilha="agro")
        resposta = self.client.get(reverse("simulador:ranking"))
        self.assertContains(resposta, "Saúde e Cadeia Fria")
        self.assertContains(resposta, "Agronegócio")
        filtrado = self.client.get(reverse("simulador:ranking") + "?trilha=agro")
        self.assertContains(filtrado, "Beto Agro")
        self.assertNotContains(filtrado, "Ana Saúde")

    def test_pontuacao_maxima_quando_usa_iot_em_tudo(self):
        self.jogar_rodada(usar_iot=True)
        self.assertEqual(Rodada.objects.get().pontuacao(), 100)

    def test_clicar_numa_rodada_mostra_as_decisoes_dela(self):
        self.jogar_rodada(jogador="Maria", empresa="Empresa M")
        rodada = Rodada.objects.get()
        resposta = self.client.get(reverse("simulador:rodada", args=[rodada.id]))
        self.assertContains(resposta, "Relatório de aprendizado da <strong>Empresa M</strong>", html=False)
        primeira = rodada.decisoes.first()
        self.assertContains(resposta, primeira.opcao.texto)

    def test_rodada_nao_finalizada_nao_pode_ser_vista_pelo_ranking(self):
        self.comecar()
        rodada = Rodada.objects.get()
        resposta = self.client.get(reverse("simulador:rodada", args=[rodada.id]))
        self.assertEqual(resposta.status_code, 404)


# ---------------------------------------------------------------- Entrega 04: trilhas

class TrilhasConteudoTest(TestCase):
    """As 6 trilhas do mapa do simulador, com 5 rodadas cada."""

    def test_seis_trilhas_com_cinco_rodadas_cada(self):
        nomes = list(Trilha.objects.values_list("nome", flat=True))
        self.assertEqual(nomes, [
            "Saúde e Cadeia Fria", "Indústria e Manufatura", "Logística e Varejo",
            "Infraestrutura Predial", "Educação e Gestão Pública", "Agronegócio",
        ])
        for trilha in Trilha.objects.all():
            ordens = list(trilha.cenarios.values_list("ordem", flat=True))
            self.assertEqual(ordens, [1, 2, 3, 4, 5], trilha.nome)

    def test_em_todo_cenario_a_opcao_iot_e_a_melhor(self):
        for cenario in Cenario.objects.all():
            melhor = max(cenario.opcoes.all(), key=lambda o: o.resultado)
            self.assertTrue(melhor.usa_iot, f"Cenário {cenario.numero}: a melhor opção deveria ser a de IoT")
            self.assertEqual(cenario.opcoes.count(), 3)
            self.assertTrue(cenario.vozes.filter(nome="Alex").exists())


class T3EscolhaDaTrilhaTest(Base):
    def test_depois_de_se_identificar_vejo_os_seis_segmentos(self):
        self.comecar(trilha=None)
        resposta = self.client.get(reverse("simulador:trilhas"))
        self.assertContains(resposta, "Qual é o seu segmento?")
        self.assertContains(resposta, "Jogar essa trilha", count=6)
        for trilha in Trilha.objects.all():
            self.assertContains(resposta, trilha.nome)

    def test_escolher_trilha_grava_e_leva_a_primeira_rodada_dela(self):
        self.comecar(trilha=None)
        resposta = self.escolher_trilha("agro")
        agro = Trilha.objects.get(slug="agro")
        self.assertEqual(Rodada.objects.get().trilha, agro)
        self.assertRedirects(resposta, reverse("simulador:cenario", args=[agro.primeiro_cenario().numero]))

    def test_trilha_invalida_mostra_erro(self):
        self.comecar(trilha=None)
        resposta = self.escolher_trilha("nao-existe")
        self.assertContains(resposta, "Escolha uma das trilhas")
        self.assertIsNone(Rodada.objects.get().trilha)

    def test_sem_trilha_nao_acessa_os_cenarios(self):
        self.comecar(trilha=None)
        resposta = self.client.get(reverse("simulador:cenario", args=[1]))
        self.assertRedirects(resposta, reverse("simulador:trilhas"))

    def test_cenario_de_outra_trilha_volta_para_a_rodada_que_falta(self):
        self.comecar(trilha="saude")
        outro = Cenario.objects.filter(trilha__slug="agro").first()
        resposta = self.client.get(reverse("simulador:cenario", args=[outro.numero]))
        self.assertRedirects(resposta, reverse("simulador:cenario", args=[1]))

    def test_trocar_de_trilha_apaga_as_respostas_da_anterior(self):
        self.comecar(trilha="saude")
        self.responder(1, "a")
        self.escolher_trilha("industria")
        self.assertEqual(Decisao.objects.count(), 0)


class T5T6ProgressoERevisaoTest(Base):
    def test_consequencia_explica_todas_as_opcoes(self):
        self.comecar()
        cenario = Cenario.objects.get(numero=1)
        resposta = self.client.post(reverse("simulador:cenario", args=[1]), {"opcao": "a"}, follow=True)
        self.assertContains(resposta, "Entenda todas as opções")
        self.assertContains(resposta, "Sua escolha")
        self.assertContains(resposta, "Melhor opção")
        for opcao in cenario.opcoes.all():
            self.assertContains(resposta, opcao.explicacao)

    def test_proxima_rodada_passa_pela_tela_de_progresso(self):
        self.comecar()
        resposta = self.client.post(reverse("simulador:cenario", args=[1]), {"opcao": "a"}, follow=True)
        self.assertContains(resposta, reverse("simulador:progresso"))
        progresso = self.client.get(reverse("simulador:progresso"))
        self.assertContains(progresso, "1 de 5 rodadas")
        self.assertContains(progresso, "Prejuízo acumulado")
        perda = Cenario.objects.get(numero=1).opcoes.get(letra="a").perda_restante
        self.assertContains(progresso, reais(perda))
        segundo = self.cenarios_da_trilha()[1]
        self.assertContains(progresso, reverse("simulador:cenario", args=[segundo.numero]))

    def test_ultima_rodada_leva_ao_resultado_final(self):
        self.comecar()
        cenarios = list(self.cenarios_da_trilha())
        for cenario in cenarios:
            resposta = self.client.post(
                reverse("simulador:cenario", args=[cenario.numero]), {"opcao": "a"}, follow=True
            )
        self.assertContains(resposta, "Ver resultado final")
        self.assertRedirects(self.client.get(reverse("simulador:progresso")), reverse("simulador:relatorio"))

    def test_resultado_final_tem_diagnostico_do_segmento_e_revisao(self):
        resposta = self.jogar_rodada(usar_iot=False)
        self.assertContains(resposta, "Diagnóstico para Saúde e Cadeia Fria")
        self.assertContains(resposta, "Revise suas decisões")
        self.assertContains(resposta, "Havia uma opção melhor", count=5)
        for cenario in self.cenarios_da_trilha():
            self.assertContains(resposta, cenario.opcao_iot().explicacao)

    def test_resultado_final_quando_acerta_tudo(self):
        resposta = self.jogar_rodada(usar_iot=True, trilha="publica")
        self.assertContains(resposta, "Você escolheu a melhor opção", count=5)
        self.assertContains(resposta, "nas 5 rodadas")


# ---------------------------------------------------------------- História 4

class H4GestaoDeCenariosTest(Base):
    """História 4: gestão de cenários pelo facilitador."""

    def setUp(self):
        self.facilitador = User.objects.create_user("fac", password="senha-forte-123")
        self.facilitador.groups.add(Group.objects.get(name="Facilitadores"))
        self.client.login(username="fac", password="senha-forte-123")

    def dados(self, **extra):
        """POST de um cenário válido: 3 alternativas (a solução IoT é a B) e 1 opinião."""
        dados = {
            "titulo": "Câmara fria sem alarme", "setor": "Cadeia fria", "trilha": "saude", "ordem": "",
            "problema": "A temperatura sobe à noite e ninguém percebe.", "perda_atual": "18000",
            "conceito_titulo": "Alerta remoto", "conceito_resumo": "Sensor avisa no celular.",
            "conceito_passos": "Medir\nAvisar", "conceito_economia": "Evita perda de produto.",
            "ativo": "on", "iot": "b", "total_vozes": "1",
            "voz_0_nome": "Alex", "voz_0_papel": "Gerente", "voz_0_fala": "Perdemos estoque de novo.",
        }
        for letra, texto, custo, restante, horas in [
            ("a", "Não fazer nada", "0", "18000", "40"),
            ("b", "Sensor com alerta", "900", "1000", "2"),
            ("c", "Contratar vigia noturno", "4000", "9000", "10"),
        ]:
            dados.update({
                f"op_{letra}_texto": texto, f"op_{letra}_custo": custo,
                f"op_{letra}_perda_restante": restante, f"op_{letra}_horas_perdidas": horas,
                f"op_{letra}_explicacao": f"Explicação da {letra}.",
            })
        dados.update(extra)
        return dados

    def salvar(self, **extra):
        return self.client.post(reverse("simulador:gestao_novo"), self.dados(**extra))

    def cenario_novo(self):
        return Cenario.objects.get(titulo="Câmara fria sem alarme")

    # 4.1
    def test_cadastrar_cenario_grava_opcoes_voz_e_aparece_na_lista(self):
        resposta = self.salvar()
        self.assertRedirects(resposta, reverse("simulador:gestao_lista"))
        cenario = self.cenario_novo()
        self.assertTrue(cenario.ativo)
        self.assertEqual(cenario.trilha.slug, "saude")
        self.assertEqual(cenario.ordem, 6)  # vai para o fim da trilha (que já tinha 5)
        self.assertEqual(cenario.opcoes.count(), 3)
        self.assertEqual(cenario.opcao_iot().letra, "b")
        self.assertEqual(cenario.opcoes.get(letra="a").horas_perdidas, 40)
        self.assertEqual(cenario.vozes.get().nome, "Alex")
        self.assertContains(self.client.get(reverse("simulador:gestao_lista")), "Câmara fria sem alarme")

    def test_cenario_novo_aparece_para_o_jogador_na_trilha(self):
        self.salvar()
        self.client.logout()
        self.comecar()
        cenario = self.cenario_novo()
        for existente in Cenario.objects.filter(trilha__slug="saude").exclude(id=cenario.id):
            self.responder(existente.numero, "a")
        resposta = self.client.get(reverse("simulador:cenario", args=[cenario.numero]))
        self.assertContains(resposta, "Rodada 6 de 6")
        self.assertContains(resposta, "Sensor com alerta")

    # 4.2
    def test_sem_solucao_iot_mostra_erro_e_nao_grava(self):
        resposta = self.salvar(iot="")
        self.assertContains(resposta, "Marque uma alternativa como solução IoT.")
        self.assertFalse(Cenario.objects.filter(titulo="Câmara fria sem alarme").exists())

    def test_iot_marcada_em_linha_vazia_conta_como_sem_iot(self):
        resposta = self.salvar(iot="d")
        self.assertContains(resposta, "Marque uma alternativa como solução IoT.")

    # 4.3
    def test_so_uma_alternativa_mostra_erro_e_mantem_o_que_foi_digitado(self):
        dados = self.dados()
        for chave in [k for k in dados if k.startswith(("op_b_", "op_c_"))]:
            dados[chave] = ""
        dados["iot"] = "a"
        resposta = self.client.post(reverse("simulador:gestao_novo"), dados)
        self.assertContains(resposta, "Cadastre pelo menos 2 alternativas.")
        self.assertContains(resposta, "Câmara fria sem alarme")  # título continua no campo
        self.assertContains(resposta, 'value="18000"')
        self.assertContains(resposta, "Não fazer nada")
        self.assertFalse(Cenario.objects.filter(titulo="Câmara fria sem alarme").exists())

    def test_alternativas_puladas_sao_recusadas(self):
        dados = self.dados(op_b_texto="", op_b_custo="", op_b_perda_restante="",
                           op_b_horas_perdidas="", op_b_explicacao="", iot="c")
        resposta = self.client.post(reverse("simulador:gestao_novo"), dados)
        self.assertContains(resposta, "sem pular linhas")

    def test_campos_numericos_invalidos_e_obrigatorios(self):
        resposta = self.salvar(perda_atual="abc", titulo="", op_a_custo="-5")
        self.assertContains(resposta, "Prejuízo mensal estimado (R$): use um número inteiro")
        self.assertContains(resposta, "Título: preencha este campo.")
        self.assertContains(resposta, "Alternativa A, custo (R$/mês): use um número inteiro")
        self.assertEqual(Cenario.objects.count(), 30)

    def test_opiniao_meio_preenchida_e_erro_e_linha_vazia_e_ignorada(self):
        resposta = self.salvar(total_vozes="2", voz_1_nome="Bia", voz_1_papel="", voz_1_fala="")
        self.assertContains(resposta, "Opinião da equipe 2")
        self.assertEqual(Cenario.objects.count(), 30)
        self.salvar(total_vozes="2", voz_1_nome="", voz_1_papel="", voz_1_fala="")
        self.assertEqual(self.cenario_novo().vozes.count(), 1)

    # 4.4
    def test_editar_atualiza_o_valor_para_os_novos_jogadores(self):
        self.salvar()
        cenario = self.cenario_novo()
        resposta = self.client.post(
            reverse("simulador:gestao_editar", args=[cenario.numero]), self.dados(perda_atual="25000")
        )
        self.assertRedirects(resposta, reverse("simulador:gestao_lista"))
        cenario.refresh_from_db()
        self.assertEqual(cenario.perda_atual, 25000)
        self.assertEqual(cenario.opcoes.count(), 3)
        self.assertEqual(cenario.vozes.count(), 1)

    def test_tela_de_edicao_vem_preenchida(self):
        resposta = self.client.get(reverse("simulador:gestao_editar", args=[1]))
        cenario = Cenario.objects.get(numero=1)
        self.assertContains(resposta, cenario.titulo)
        self.assertContains(resposta, cenario.opcoes.first().texto)

    def test_editar_nao_apaga_decisoes_de_quem_ja_jogou(self):
        self.client.logout()
        self.comecar()
        self.responder(1, "b")
        self.client.login(username="fac", password="senha-forte-123")
        cenario = Cenario.objects.get(numero=1)
        dados = self.dados(titulo=cenario.titulo, trilha="saude", ordem="1", iot=cenario.opcao_iot().letra)
        for opcao in cenario.opcoes.all():  # reaproveita as alternativas existentes
            for campo, valor in [("texto", opcao.texto), ("custo", opcao.custo),
                                 ("perda_restante", opcao.perda_restante), ("explicacao", opcao.explicacao)]:
                dados[f"op_{opcao.letra}_{campo}"] = str(valor)
        resposta = self.client.post(reverse("simulador:gestao_editar", args=[1]), dados)
        self.assertRedirects(resposta, reverse("simulador:gestao_lista"))
        self.assertEqual(Decisao.objects.count(), 1)

    def test_nao_remove_alternativa_ja_escolhida_por_jogadores(self):
        self.client.logout()
        self.comecar()
        self.responder(1, "c")
        self.client.login(username="fac", password="senha-forte-123")
        cenario = Cenario.objects.get(numero=1)
        dados = self.dados(titulo=cenario.titulo, iot="a")
        for chave in [k for k in dados if k.startswith("op_c_")]:
            dados[chave] = ""
        resposta = self.client.post(reverse("simulador:gestao_editar", args=[1]), dados)
        self.assertContains(resposta, "já foi escolhida por jogadores")
        self.assertTrue(Opcao.objects.filter(cenario=cenario, letra="c").exists())
        self.assertEqual(Decisao.objects.count(), 1)

    # 4.5
    def test_desativar_some_para_novas_rodadas_mas_o_relatorio_antigo_continua(self):
        # Maria joga a trilha inteira
        maria = self.jogar_rodada(jogador="Maria", empresa="Mercado Boa Vista")
        self.assertContains(maria, "Maria")
        decisoes_antes = Decisao.objects.count()
        rodada_maria = Rodada.objects.get(jogador="Maria")
        pontos_antes = rodada_maria.pontuacao()
        self.client.logout()

        self.client.login(username="fac", password="senha-forte-123")
        resposta = self.client.post(reverse("simulador:gestao_alternar", args=[1]))
        self.assertRedirects(resposta, reverse("simulador:gestao_lista"))
        self.assertFalse(Cenario.objects.get(numero=1).ativo)
        self.client.logout()

        # decisões e partida antiga não mudam
        self.assertEqual(Decisao.objects.count(), decisoes_antes)
        rodada_maria.refresh_from_db()
        self.assertEqual(rodada_maria.pontuacao(), pontos_antes)
        self.assertEqual(rodada_maria.cenarios().count(), 5)
        relatorio = self.client.get(reverse("simulador:rodada", args=[rodada_maria.id]))
        self.assertEqual(relatorio.status_code, 200)
        self.assertEqual(relatorio.context["total"], 5)

        # nova rodada: o cenário 1 não aparece; a trilha passa a ter 4 rodadas
        segundo = self.cenarios_da_trilha().exclude(numero=1)[0]
        self.comecar(jogador="Joana", empresa="Clínica Sol")
        resposta = self.client.get(reverse("simulador:cenario", args=[1]))
        self.assertRedirects(resposta, reverse("simulador:cenario", args=[segundo.numero]))
        resposta = self.client.get(reverse("simulador:cenario", args=[segundo.numero]))
        self.assertContains(resposta, "Rodada 1 de 4")  # posição recalculada sem o desativado

    def test_jogador_no_meio_da_partida_continua_apos_cenario_ser_desativado(self):
        self.comecar()
        primeiro, segundo, terceiro = self.cenarios_da_trilha()[:3]
        self.responder(primeiro.numero, "a")
        Cenario.objects.filter(id=segundo.id).update(ativo=False)
        resposta = self.client.get(reverse("simulador:progresso"))
        self.assertContains(resposta, "1 de 4 rodadas")
        resposta = self.client.get(reverse("simulador:cenario", args=[segundo.numero]))
        self.assertRedirects(resposta, reverse("simulador:cenario", args=[terceiro.numero]))

    def test_ativar_de_volta_e_recusado_se_o_cenario_estiver_incompleto(self):
        cenario = Cenario.objects.get(numero=1)
        cenario.opcoes.update(usa_iot=False)
        cenario.ativo = False
        cenario.save()
        self.client.post(reverse("simulador:gestao_alternar", args=[1]))
        cenario.refresh_from_db()
        self.assertFalse(cenario.ativo)
        cenario.opcoes.filter(letra="a").update(usa_iot=True)
        self.client.post(reverse("simulador:gestao_alternar", args=[1]))
        cenario.refresh_from_db()
        self.assertTrue(cenario.ativo)

    def test_excluir_so_cenario_que_ninguem_jogou(self):
        self.salvar()
        novo = self.cenario_novo()
        self.client.post(reverse("simulador:gestao_excluir", args=[novo.numero]))
        self.assertFalse(Cenario.objects.filter(id=novo.id).exists())
        self.assertEqual(Voz.objects.filter(nome="Alex", cenario=novo).count(), 0)

        self.client.logout()
        self.comecar()
        self.responder(1, "a")
        self.client.login(username="fac", password="senha-forte-123")
        self.client.post(reverse("simulador:gestao_excluir", args=[1]))
        self.assertTrue(Cenario.objects.filter(numero=1).exists())
        self.assertEqual(Decisao.objects.count(), 1)

    # 4.6
    def test_sem_login_vai_para_a_tela_de_login(self):
        self.client.logout()
        for nome, args in [("gestao_lista", []), ("gestao_novo", []), ("gestao_editar", [1])]:
            url = reverse(f"simulador:{nome}", args=args)
            self.assertRedirects(
                self.client.get(url), f"{reverse('simulador:login_facilitador')}?next={url}",
            )

    def test_acoes_de_gestao_sem_login_nao_alteram_nada(self):
        self.client.logout()
        self.client.post(reverse("simulador:gestao_alternar", args=[1]))
        self.client.post(reverse("simulador:gestao_excluir", args=[1]))
        self.client.post(reverse("simulador:gestao_novo"), self.dados())
        self.assertTrue(Cenario.objects.get(numero=1).ativo)
        self.assertEqual(Cenario.objects.count(), 30)

    def test_usuario_logado_que_nao_e_facilitador_recebe_403(self):
        User.objects.create_user("jogador", password="senha-forte-123")
        self.client.login(username="jogador", password="senha-forte-123")
        self.assertEqual(self.client.get(reverse("simulador:gestao_lista")).status_code, 403)
        self.assertEqual(self.client.post(reverse("simulador:gestao_alternar", args=[1])).status_code, 403)

    def test_jogador_comum_nao_ve_link_para_a_gestao(self):
        self.client.logout()
        for nome in ("inicio", "ranking"):
            self.assertNotContains(self.client.get(reverse(f"simulador:{nome}")), "facilitador")

    def test_login_do_facilitador(self):
        self.client.logout()
        url = reverse("simulador:login_facilitador")
        self.assertContains(self.client.post(url, {"usuario": "fac", "senha": "errada"}), "Usuário ou senha incorretos.")
        User.objects.create_user("jogador", password="senha-forte-123")
        resposta = self.client.post(url, {"usuario": "jogador", "senha": "senha-forte-123"})
        self.assertContains(resposta, "não tem permissão de facilitador")
        resposta = self.client.post(url, {"usuario": "fac", "senha": "senha-forte-123"})
        self.assertRedirects(resposta, reverse("simulador:gestao_lista"))

    def test_login_nao_redireciona_para_site_externo(self):
        self.client.logout()
        resposta = self.client.post(
            reverse("simulador:login_facilitador"),
            {"usuario": "fac", "senha": "senha-forte-123", "next": "https://site-malicioso.com"},
        )
        self.assertRedirects(resposta, reverse("simulador:gestao_lista"))

    def test_sair_encerra_a_sessao(self):
        self.client.post(reverse("simulador:logout_facilitador"))
        self.assertEqual(self.client.get(reverse("simulador:gestao_lista")).status_code, 302)


class H5DadosDoSensorTest(Base):
    """História 5: dados do sensor antes da decisão."""

    def primeiro(self):
        return self.cenarios_da_trilha().first()

    def url(self, cenario, dados=False):
        return reverse("simulador:cenario", args=[cenario.numero]) + ("?dados=1" if dados else "")

    # 5.1
    def test_ver_os_dados_do_sensor_mostra_o_texto_e_as_alternativas(self):
        self.comecar()
        cenario = self.primeiro()
        self.assertTrue(cenario.dados_sensor)  # preenchido pela migração 0007
        antes = self.client.get(self.url(cenario))
        self.assertContains(antes, "Ver o que o sensor mostraria")
        # O bloco já vem na página, mas escondido até o clique (abre sem recarregar).
        self.assertContains(antes, 'id="dados-sensor"')
        self.assertRegex(antes.content.decode(), r'id="dados-sensor"[^>]*\shidden>')
        self.assertContains(antes, 'id="viu-dados" value=""')
        # Sem JavaScript, o link ?dados=1 abre o bloco já visível (plano B).
        depois = self.client.get(self.url(cenario, dados=True))
        self.assertContains(depois, cenario.dados_sensor[:30])
        self.assertNotRegex(depois.content.decode(), r'id="dados-sensor"[^>]*\shidden>')
        self.assertContains(depois, "Confirmar decisão")
        self.assertContains(depois, 'id="viu-dados" value="1"')

    # 5.2
    def test_cenario_sem_dados_nao_mostra_o_botao(self):
        self.comecar()
        cenario = self.primeiro()
        Cenario.objects.filter(pk=cenario.pk).update(dados_sensor="")
        resposta = self.client.get(self.url(cenario, dados=True))
        self.assertNotContains(resposta, "Ver o que o sensor mostraria")
        self.assertNotContains(resposta, 'id="dados-sensor"')
        self.assertNotContains(resposta, 'name="viu_dados"')

    # 5.3
    def test_abrir_os_dados_nao_muda_a_pontuacao(self):
        self.comecar()
        for cenario in self.cenarios_da_trilha():
            self.client.post(self.url(cenario), {"opcao": cenario.opcao_iot().letra, "viu_dados": "1"})
        self.client.get(reverse("simulador:relatorio"))
        self.assertEqual(Rodada.objects.get().pontuacao(), 100)

    # 5.4
    def test_relatorio_mostra_em_quantas_decisoes_consultou_os_dados(self):
        self.comecar()
        cenarios = list(self.cenarios_da_trilha())
        for i, cenario in enumerate(cenarios):
            dados = {"opcao": cenario.opcoes.first().letra}
            if i == 0:
                dados["viu_dados"] = "1"
            self.client.post(self.url(cenario), dados)
        resposta = self.client.get(reverse("simulador:relatorio"))
        self.assertEqual(Rodada.objects.get().decisoes_com_dados(), 1)
        self.assertContains(resposta, "Consultou os dados do sensor")
        self.assertContains(resposta, f"1 de {len(cenarios)}")

    def test_mudar_de_ideia_nao_apaga_que_consultou_os_dados(self):
        self.comecar()
        cenario = self.primeiro()
        self.client.post(self.url(cenario), {"opcao": "a", "viu_dados": "1"})
        self.client.post(self.url(cenario), {"opcao": "b"})
        decisao = Decisao.objects.get()
        self.assertEqual(decisao.opcao.letra, "b")
        self.assertTrue(decisao.viu_dados_sensor)

    def test_cenario_sem_dados_ignora_viu_dados_enviado(self):
        self.comecar()
        cenario = self.primeiro()
        Cenario.objects.filter(pk=cenario.pk).update(dados_sensor="")
        self.client.post(self.url(cenario), {"opcao": "a", "viu_dados": "1"})
        self.assertFalse(Decisao.objects.get().viu_dados_sensor)


class H5FacilitadorCadastraDadosTest(Base):
    """História 5, cenário 5.5: o facilitador cadastra os dados do sensor."""

    # Reaproveita o login e o formulário válido dos testes da História 4.
    setUp = H4GestaoDeCenariosTest.setUp
    dados = H4GestaoDeCenariosTest.dados
    salvar = H4GestaoDeCenariosTest.salvar
    cenario_novo = H4GestaoDeCenariosTest.cenario_novo

    def test_facilitador_cadastra_e_edita_os_dados_do_sensor(self):
        self.salvar(dados_sensor="Temperatura passou de 8 °C às 3h.")
        cenario = self.cenario_novo()
        self.assertEqual(cenario.dados_sensor, "Temperatura passou de 8 °C às 3h.")
        tela = self.client.get(reverse("simulador:gestao_editar", args=[cenario.numero]))
        self.assertContains(tela, "Temperatura passou de 8 °C às 3h.")


class H5TodosOsCenariosTemDadosTest(Base):
    """História 5: todos os cenários iniciais vêm com dados do sensor (migração 0007)."""

    def test_todos_os_cenarios_iniciais_tem_dados_do_sensor(self):
        sem_dados = Cenario.objects.filter(dados_sensor="").values_list("numero", flat=True)
        self.assertEqual(list(sem_dados), [])
