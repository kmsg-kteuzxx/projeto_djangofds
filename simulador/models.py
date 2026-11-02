from django.db import models
from django.db.models import Q


class Trilha(models.Model):
    """Segmento escolhido pelo jogador na tela T3 (ex.: Agronegócio). Tem 5 rodadas."""

    numero = models.PositiveIntegerField(unique=True)
    slug = models.SlugField(unique=True)
    nome = models.CharField(max_length=60)
    icone = models.CharField(max_length=30, default="sensor")
    descricao = models.TextField()
    exemplos = models.CharField(max_length=200)
    diagnostico = models.TextField(help_text="1º parágrafo do diagnóstico no resultado final")

    class Meta:
        ordering = ["numero"]

    def __str__(self):
        return self.nome

    def primeiro_cenario(self):
        """Primeiro cenário ATIVO da trilha (cenário desativado não aparece para jogadores)."""
        return self.cenarios.filter(ativo=True).first()


class Cenario(models.Model):
    """Um problema real de empresa que o jogador precisa resolver."""

    numero = models.PositiveIntegerField(unique=True)
    trilha = models.ForeignKey(
        Trilha, on_delete=models.CASCADE, related_name="cenarios", null=True, blank=True
    )
    ordem = models.PositiveIntegerField(default=0, help_text="Posição da rodada dentro da trilha (1 a 5)")
    setor = models.CharField(max_length=60)
    titulo = models.CharField(max_length=120)
    problema = models.TextField()
    perda_atual = models.PositiveIntegerField(help_text="Prejuízo atual em R$ por mês")
    ativo = models.BooleanField(
        default=True,
        help_text="Só cenários ativos aparecem para os jogadores. Desativar não apaga as decisões já tomadas.",
    )

    # Conceito de IoT explicado no relatório de aprendizado
    conceito_titulo = models.CharField(max_length=120)
    conceito_resumo = models.TextField()
    conceito_passos = models.TextField(help_text="Um passo por linha")
    conceito_economia = models.TextField()

    class Meta:
        ordering = ["trilha__numero", "ordem", "numero"]
        verbose_name = "cenário"
        verbose_name_plural = "cenários"

    def __str__(self):
        return f"{self.numero}. {self.titulo}"

    # Ícone do card de situação de acordo com o setor (desenhos em simulador/_icone.html)
    ICONES_POR_SETOR = {
        "Cadeia fria": "frio",
        "Indústria 4.0": "industria",
        "Utilities (água)": "agua",
        "Edifícios inteligentes": "predio",
        "Agronegócio": "agro",
    }

    @property
    def icone(self):
        if self.setor in self.ICONES_POR_SETOR:
            return self.ICONES_POR_SETOR[self.setor]
        return self.trilha.icone if self.trilha_id else "sensor"

    @property
    def lista_passos(self):
        return [p.strip() for p in self.conceito_passos.splitlines() if p.strip()]

    def opcao_iot(self):
        return self.opcoes.filter(usa_iot=True).first()

    def proximo(self):
        """Próxima rodada ATIVA da mesma trilha (ou None se esta é a última)."""
        return Cenario.objects.filter(trilha=self.trilha, ordem__gt=self.ordem, ativo=True).first()


class Voz(models.Model):
    """Opinião de uma pessoa da equipe sobre o cenário (ex.: Alex)."""

    cenario = models.ForeignKey(Cenario, on_delete=models.CASCADE, related_name="vozes")
    nome = models.CharField(max_length=60)
    papel = models.CharField(max_length=60)
    fala = models.TextField()
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem"]
        verbose_name = "voz da equipe"
        verbose_name_plural = "vozes da equipe"

    def __str__(self):
        return f"{self.nome} ({self.cenario.numero})"


class Opcao(models.Model):
    """Alternativa que o jogador pode escolher em um cenário."""

    cenario = models.ForeignKey(Cenario, on_delete=models.CASCADE, related_name="opcoes")
    letra = models.CharField(max_length=1)
    texto = models.CharField(max_length=200)
    custo = models.PositiveIntegerField(help_text="Custo da solução em R$ por mês")
    perda_restante = models.PositiveIntegerField(help_text="Prejuízo que continua em R$ por mês")
    horas_perdidas = models.PositiveIntegerField(
        default=0, help_text="Horas de operação que continuam sendo perdidas por mês"
    )
    usa_iot = models.BooleanField(default=False)
    explicacao = models.TextField()

    class Meta:
        ordering = ["letra"]
        unique_together = [("cenario", "letra")]
        verbose_name = "opção"
        verbose_name_plural = "opções"

    def __str__(self):
        return f"{self.cenario.numero}{self.letra}: {self.texto}"

    @property
    def economia(self):
        """Quanto a empresa deixa de perder por mês."""
        return self.cenario.perda_atual - self.perda_restante

    @property
    def resultado(self):
        """Economia menos o custo da solução (pode ser negativo)."""
        return self.economia - self.custo


class Rodada(models.Model):
    """Uma partida do simulador, jogada por uma pessoa."""

    jogador = models.CharField(max_length=80)
    empresa = models.CharField(max_length=80)
    trilha = models.ForeignKey(
        Trilha, on_delete=models.SET_NULL, null=True, blank=True, related_name="rodadas"
    )
    iniciada_em = models.DateTimeField(auto_now_add=True)
    finalizada_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-iniciada_em"]

    def __str__(self):
        return f"{self.jogador} ({self.empresa})"

    @property
    def finalizada(self):
        return self.finalizada_em is not None

    def cenarios(self):
        """
        Cenários desta partida.
        - Partida finalizada (ou antiga, sem trilha): só os que o jogador respondeu. Assim,
          cadastrar, editar a ordem ou desativar cenários depois não muda uma partida antiga.
        - Partida em andamento: os cenários ATIVOS da trilha escolhida, mais os que o jogador
          já respondeu (mesmo que o facilitador tenha desativado no meio do caminho).
        """
        respondidos = self.decisoes.values_list("cenario_id", flat=True)
        if self.trilha_id and not self.finalizada:
            return Cenario.objects.filter(
                Q(trilha_id=self.trilha_id, ativo=True) | Q(id__in=respondidos)
            )
        return Cenario.objects.filter(id__in=respondidos)

    def resultado_total(self):
        return sum(d.opcao.resultado for d in self.decisoes.select_related("opcao__cenario"))

    def decisoes_iot(self):
        return self.decisoes.filter(opcao__usa_iot=True).count()

    def pontuacao(self):
        """
        Pontuação de 0 a 100: quanto do resultado possível com IoT o jogador alcançou
        nas rodadas da trilha escolhida.
        """
        ideal = 0
        for cenario in self.cenarios():
            iot = cenario.opcao_iot()
            if iot:
                ideal += iot.resultado
        if ideal <= 0:
            return 0
        return max(0, min(100, round(self.resultado_total() * 100 / ideal)))


class Decisao(models.Model):
    """A alternativa escolhida pelo jogador em um cenário de uma rodada."""

    rodada = models.ForeignKey(Rodada, on_delete=models.CASCADE, related_name="decisoes")
    cenario = models.ForeignKey(Cenario, on_delete=models.CASCADE)
    opcao = models.ForeignKey(Opcao, on_delete=models.CASCADE)
    decidida_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["cenario__ordem", "cenario__numero"]
        unique_together = [("rodada", "cenario")]
        verbose_name = "decisão"
        verbose_name_plural = "decisões"

    def __str__(self):
        return f"{self.rodada} → {self.opcao}"
