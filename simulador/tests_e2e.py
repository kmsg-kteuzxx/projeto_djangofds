"""
Testes de sistema (E2E) com Selenium - Entrega 04.

Abrem um Chrome de verdade (sem janela, modo headless), navegam pelo site
rodando num servidor de teste e conferem o que a pessoa vê na tela.

Cobrem as histórias desta entrega (4, 5 e 6) e o fluxo principal do jogo (1).

Como rodar:
    pip install -r requirements-dev.txt
    python manage.py test simulador.tests_e2e

Sem Selenium ou sem Chrome, os testes são PULADOS (para não atrapalhar quem só
quer rodar os testes de unidade). No CI, a variável E2E_OBRIGATORIO=1 faz eles
FALHAREM nesse caso, para nunca passar sem ter rodado de verdade.
Para ver o navegador abrindo (fora do CI): E2E_JANELA=1.
"""
import os
import unittest

from django.contrib.auth.models import Group, User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings, tag

from .models import Cenario, Decisao, Rodada

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import Select, WebDriverWait
except ImportError:  # selenium não instalado
    webdriver = None

TRILHA = "saude"
SENHA = "senha-forte-123"


def criar_navegador():
    opcoes = webdriver.ChromeOptions()
    if os.getenv("E2E_JANELA") != "1":
        opcoes.add_argument("--headless=new")
    for argumento in ("--no-sandbox", "--disable-dev-shm-usage", "--window-size=1280,1000"):
        opcoes.add_argument(argumento)
    if os.getenv("CHROME_BIN"):
        opcoes.binary_location = os.environ["CHROME_BIN"]
    servico = webdriver.ChromeService(executable_path=os.getenv("CHROMEDRIVER") or None)
    return webdriver.Chrome(options=opcoes, service=servico)


@tag("e2e")
# Os testes não rodam collectstatic: serve os estáticos direto das pastas dos apps.
@override_settings(STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage")
class E2EBase(StaticLiveServerTestCase):
    # O servidor de teste esvazia o banco depois de cada teste, inclusive os
    # cenários, trilhas e o grupo Facilitadores criados pelas migrações.
    # Isto restaura esses dados antes de cada teste.
    serialized_rollback = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        try:
            if webdriver is None:
                raise RuntimeError("selenium não está instalado")
            cls.navegador = criar_navegador()
        except Exception as erro:
            super().tearDownClass()
            if os.getenv("E2E_OBRIGATORIO") == "1":
                raise
            raise unittest.SkipTest(f"Navegador indisponível para os testes E2E: {erro}")
        cls.navegador.implicitly_wait(3)

    @classmethod
    def tearDownClass(cls):
        cls.navegador.quit()
        super().tearDownClass()

    # ---------------------------------------------------------------- ajudantes
    def abrir(self, caminho):
        self.navegador.get(self.live_server_url + caminho)

    def esperar(self, condicao, tempo=5):
        return WebDriverWait(self.navegador, tempo).until(condicao)

    def css(self, seletor):
        return self.navegador.find_element(By.CSS_SELECTOR, seletor)

    def texto_da_pagina(self):
        return self.css("body").text

    def comecar(self, jogador="Maria", empresa="Clínica Boa Vista"):
        """T2 (nome e empresa) → T3 (trilha) → 1º cenário."""
        self.abrir("/simulador/como-funciona/")
        self.css("#jogador").send_keys(jogador)
        self.css("#empresa").send_keys(empresa)
        self.css("form button[type=submit]").click()
        self.esperar(EC.url_contains("/trilhas/"))
        self.css(f"form:has(input[value='{TRILHA}']) button").click()
        self.esperar(EC.url_contains("/cenario/"))

    def decidir(self, letra, ver_dados=False):
        """Na tela do cenário: (opcional) abre os dados do sensor, escolhe e confirma."""
        if ver_dados:
            self.css("#abrir-dados").click()
        self.css(f"label:has(input[name=opcao][value='{letra}'])").click()
        self.css("form button[type=submit]").click()
        self.esperar(EC.url_contains("/resultado/"))

    def entrar_como_facilitador(self):
        usuario = User.objects.create_user("facilitador", password=SENHA)
        usuario.groups.add(Group.objects.get(name="Facilitadores"))
        self.abrir("/simulador/facilitador/entrar/")
        self.css("input[name=usuario]").send_keys("facilitador")
        self.css("input[name=senha]").send_keys(SENHA)
        self.css("form button[type=submit]").click()
        self.esperar(EC.url_contains("/facilitador/"))


class E2EJogoTest(E2EBase):
    """História 1: jogar uma trilha inteira pelo navegador e ver o relatório."""

    def test_jogar_a_trilha_inteira_e_ver_o_relatorio(self):
        self.comecar()
        cenarios = list(Cenario.objects.filter(trilha__slug=TRILHA, ativo=True))
        for cenario in cenarios:
            self.abrir(f"/simulador/cenario/{cenario.numero}/")
            self.decidir(cenario.opcao_iot().letra)
        self.abrir("/simulador/relatorio/")
        texto = self.texto_da_pagina()
        self.assertIn("Maria", texto)
        self.assertIn(f"{len(cenarios)} de {len(cenarios)}", texto)  # todas baseadas em dados
        self.assertEqual(Rodada.objects.get().pontuacao(), 100)


class E2EDadosDoSensorTest(E2EBase):
    """História 5: dados do sensor abrem na hora, sem recarregar a página."""

    def test_ver_os_dados_do_sensor_sem_recarregar(self):
        self.comecar()
        cenario = Cenario.objects.filter(trilha__slug=TRILHA, ativo=True).first()
        bloco = self.css("#dados-sensor")
        self.assertFalse(bloco.is_displayed())

        url_antes = self.navegador.current_url
        self.navegador.execute_script("window.marcaSemRecarregar = true;")
        self.css("#abrir-dados").click()

        self.esperar(EC.visibility_of(bloco))
        self.assertIn(cenario.dados_sensor[:40], bloco.text)
        self.assertFalse(self.css("#abrir-dados").is_displayed())
        self.assertEqual(self.navegador.current_url, url_antes)
        # Se a página tivesse recarregado, a variável teria sumido.
        self.assertTrue(self.navegador.execute_script("return window.marcaSemRecarregar === true;"))

    def test_relatorio_conta_as_decisoes_em_que_viu_os_dados(self):
        self.comecar()
        cenarios = list(Cenario.objects.filter(trilha__slug=TRILHA, ativo=True))
        for i, cenario in enumerate(cenarios):
            self.abrir(f"/simulador/cenario/{cenario.numero}/")
            self.decidir("a", ver_dados=(i < 2))
        self.assertEqual(Decisao.objects.filter(viu_dados_sensor=True).count(), 2)
        self.abrir("/simulador/relatorio/")
        self.assertIn("Consultou os dados do sensor", self.texto_da_pagina())
        self.assertIn(f"2 de {len(cenarios)}", self.texto_da_pagina())


class E2EGestaoDeCenariosTest(E2EBase):
    """História 4: o facilitador desativa um cenário e ele some do jogo."""

    def test_sem_login_a_area_do_facilitador_pede_login(self):
        self.abrir("/simulador/facilitador/")
        self.esperar(EC.url_contains("/facilitador/entrar/"))
        self.assertTrue(self.css("input[name=senha]").is_displayed())

    def test_desativar_cenario_pelo_painel(self):
        self.entrar_como_facilitador()
        cenario = Cenario.objects.filter(trilha__slug=TRILHA, ativo=True).last()
        linha = self.navegador.find_element(By.XPATH, f"//tr[td[1][normalize-space()='{cenario.numero}']]")
        linha.find_element(By.XPATH, ".//button[normalize-space()='Desativar']").click()
        self.esperar(lambda _: not Cenario.objects.get(pk=cenario.pk).ativo)
        self.assertIn("Desativado", self.navegador.find_element(
            By.XPATH, f"//tr[td[1][normalize-space()='{cenario.numero}']]").text)


class E2EPainelDeResultadosTest(E2EBase):
    """História 6: painel de resultados dentro da área do facilitador."""

    def test_painel_pelo_menu_com_filtro_e_csv(self):
        # Uma partida jogada pelo navegador, parada no 2º cenário.
        self.comecar()
        primeiro = Cenario.objects.filter(trilha__slug=TRILHA, ativo=True).first()
        self.decidir(primeiro.opcao_iot().letra)
        self.navegador.delete_all_cookies()

        self.entrar_como_facilitador()
        self.navegador.find_element(By.LINK_TEXT, "Resultados").click()
        self.esperar(EC.url_contains("/facilitador/resultados/"))
        texto = self.texto_da_pagina()
        self.assertIn("Resultados das partidas", texto)
        self.assertIn("Saúde e Cadeia Fria", texto)
        self.assertIn("0%", texto)  # 0 de 1 partida concluída

        Select(self.css("#trilha")).select_by_value("industria")
        self.navegador.find_element(By.XPATH, "//button[normalize-space()='Filtrar']").click()
        self.esperar(EC.url_contains("trilha=industria"))
        self.assertIn("Nenhuma rodada foi iniciada com esses filtros", self.texto_da_pagina())

        link_csv = self.navegador.find_element(By.LINK_TEXT, "Exportar CSV") \
            if self.navegador.find_elements(By.LINK_TEXT, "Exportar CSV") else None
        self.assertIsNone(link_csv)  # sem dados, não há tabela para exportar

        self.abrir("/simulador/facilitador/resultados/?trilha=saude")
        csv_href = self.navegador.find_element(By.LINK_TEXT, "Exportar CSV").get_attribute("href")
        self.assertIn("formato=csv", csv_href)
        self.assertIn("trilha=saude", csv_href)
