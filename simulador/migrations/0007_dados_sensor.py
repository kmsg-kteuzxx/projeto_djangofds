# História 5 — Dados do sensor antes da decisão.

from django.db import migrations, models


# Dados do sensor para os 30 cenários iniciais. O facilitador pode editar ou apagar pelo
# formulário de cenários; cenários sem texto simplesmente não mostram o botão.
DADOS_SENSOR = {
    1: (
        "Temperatura da câmara fria nas últimas 24 horas: estável em 2 °C durante o dia, "
        "mas subiu para 9 °C entre 1h e 4h da madrugada, todas as noites desta semana. "
        "No mesmo horário, a porta registrou 6 aberturas."
    ),
    2: (
        "Vibração do motor da máquina: subiu 40% nos últimos 10 dias, sempre no fim do turno. "
        "A temperatura do rolamento chegou a 78 °C ontem; o normal é até 60 °C."
    ),
    3: (
        "Consumo de água por hora: mesmo com a empresa fechada, entre 23h e 5h, o medidor "
        "registra cerca de 120 litros por hora saindo, todos os dias."
    ),
    6: (
        "Temperatura da geladeira de vacinas: ficou acima de 8 °C por 3 horas no último "
        "domingo, depois de uma queda de energia. Ninguém estava na unidade."
    ),
    4: (
        'Sensor de presença e medidor de energia das salas de reunião: as 6 salas ficaram ocupadas, em média, 3 horas por dia, mas o ar-condicionado e as luzes ficaram ligados 11 horas. A sala 3 não teve ninguém na quarta-feira inteira e consumiu energia o dia todo.'
    ),
    5: (
        'Umidade do solo na última semana: o talhão norte ficou encharcado (acima de 45%) depois da rega das 6h, enquanto o talhão sul secou abaixo de 18% à tarde. Na terça choveu 22 mm e a irrigação ligou mesmo assim, no horário de sempre.'
    ),
    7: (
        'Localização dos equipamentos agora: há 14 bombas de infusão paradas no hospital, 9 delas no depósito do 3º andar e 3 no corredor da pediatria. Ontem, a enfermagem fez 27 buscas por bombas, com média de 18 minutos cada.'
    ),
    8: (
        'Temperatura e posição do baú nas últimas entregas: a temperatura sobe acima de 8 °C sempre que o caminhão fica parado mais de 40 minutos com a porta aberta. Na entrega recusada de ontem, o baú ficou 1h10 aberto numa parada fora da rota.'
    ),
    9: (
        'Pressão dos cilindros de oxigênio: o cilindro da sala de emergência está em 25% e, no ritmo de consumo desta semana, acaba em cerca de 2 dias. O pedido normal ao fornecedor leva 3 dias para chegar.'
    ),
    10: (
        'Medidor de energia e pressão do ar comprimido: entre 12h e 13h e de madrugada, com as máquinas paradas, o compressor continua ligando a cada 4 minutos. A pressão cai sozinha, o que indica vazamentos na tubulação, responsáveis por cerca de 30% do ar produzido.'
    ),
    11: (
        'Temperatura e pressão da injetora 4: às 10h40 a temperatura do molde caiu 12 °C abaixo do padrão e ficou assim por 2 horas. Todas as peças com defeito do lote de ontem foram feitas nesse intervalo.'
    ),
    12: (
        'Contador de peças e paradas das máquinas: ontem, a linha 2 teve 41 paradas curtas, de 1 a 4 minutos, que não foram anotadas no papel. Somadas, deram 1h50 de máquina parada, quase o tempo que faltou para bater a meta.'
    ),
    13: (
        'Medidor inteligente de potência: o limite contratado foi ultrapassado 9 vezes neste mês, sempre entre 7h e 7h20, quando o forno, o compressor e a prensa grande ligam ao mesmo tempo na troca de turno.'
    ),
    14: (
        'Telemetria da frota: os caminhões ficaram 2h10 por dia, em média, parados com o motor ligado. O caminhão 7 fez um desvio de 38 km fora da rota três vezes nesta semana.'
    ),
    15: (
        'Sensores de peso nas prateleiras: o café e o leite zeram na prateleira entre 17h30 e 19h, todos os dias, enquanto o depósito tem estoque para mais 5 dias. A reposição acontece só às 20h.'
    ),
    16: (
        'Leitores RFID do armazém: 12% dos paletes estão em uma posição diferente da registrada no sistema. Na semana passada, 37 pedidos atrasaram porque o separador não encontrou a mercadoria na primeira tentativa.'
    ),
    17: (
        'Rastreamento dos veículos: 82% das entregas de hoje estão no horário e 9 estão atrasadas por trânsito na mesma avenida. A central recebeu 140 ligações hoje, e a maioria era sobre entregas que estavam no horário.'
    ),
    18: (
        'Contador de pessoas na entrada: o maior movimento é entre 11h30 e 13h e entre 17h30 e 19h, com até 3 vezes mais clientes que no resto do dia. A escala atual coloca o mesmo número de caixas das 8h às 22h.'
    ),
    19: (
        'Sensores do elevador 2: o motor da porta está demorando 40% mais para fechar e a vibração aumentou nas últimas 2 semanas. As duas últimas quebras foram precedidas por esse mesmo sinal.'
    ),
    20: (
        "Sensor de nível da caixa d'água: a bomba continua ligada depois que a caixa enche, entre 2h e 4h, porque a boia está travando. Em outros dias, a bomba ligou com a cisterna vazia e trabalhou 25 minutos sem água."
    ),
    21: (
        'Sensores do quadro elétrico do 4º andar: o disjuntor 6 chega a 74 °C entre 14h e 16h, quando o normal é até 50 °C. Nesses horários a corrente passa do limite do circuito, por causa dos aparelhos ligados juntos.'
    ),
    22: (
        'Telegestão dos postes: 312 postes ficaram acesos de dia nesta semana, porque o sensor de luz está queimado. Outros 87 estão apagados à noite há mais de 10 dias, concentrados em 3 bairros.'
    ),
    23: (
        'Sensores de nível dos contêineres: 60% dos contêineres da rota de terça estavam com menos de 30% da capacidade quando o caminhão passou. Os do centro e da feira chegam a 100% já no domingo à noite.'
    ),
    24: (
        'Medidores das escolas durante as férias: 31 das 40 escolas consumiram mais da metade da energia de um mês de aula. Na Escola Rio Doce, 8 aparelhos de ar-condicionado ficaram ligados direto por 12 dias.'
    ),
    25: (
        'Contadores de passageiros e GPS: a linha 204 roda com 120% da lotação entre 6h30 e 8h. No mesmo horário, a linha 310 leva em média 9 passageiros por viagem e tem o dobro de horários.'
    ),
    26: (
        'Sensores do rio e pluviômetros: com mais de 40 mm de chuva em 1 hora, o nível do rio sobe 1,5 metro em 50 minutos e o bairro começa a alagar cerca de 1h20 depois. Na última chuva, esse sinal apareceu 1 hora antes dos primeiros pedidos de socorro.'
    ),
    27: (
        'Colares das vacas: a vaca 112 está ruminando 35% menos e se movimentando menos há 2 dias, mas a produção de leite dela ainda não caiu. Esse foi o mesmo padrão das 4 vacas que adoeceram no último mês.'
    ),
    28: (
        'Cabos de temperatura do silo: a 6 metros de profundidade, no lado leste, a temperatura subiu de 22 °C para 31 °C em 10 dias. No resto do silo, os grãos estão estáveis em 20 °C.'
    ),
    29: (
        'Sensores de clima da estufa: ontem a temperatura passou de 38 °C entre 11h e 14h, mas as cortinas só abrem às 14h, no horário fixo. À noite, a umidade ficou acima de 90% por 7 horas, condição ideal para fungos.'
    ),
    30: (
        'Armadilhas conectadas: 3 das 25 armadilhas contaram mais de 40 lagartas por noite, todas no talhão próximo à mata. Nas outras 22, a contagem está abaixo do nível que exige aplicação.'
    ),
}


def preencher(apps, schema_editor):
    Cenario = apps.get_model("simulador", "Cenario")
    for numero, texto in DADOS_SENSOR.items():
        Cenario.objects.filter(numero=numero, dados_sensor="").update(dados_sensor=texto)


class Migration(migrations.Migration):

    dependencies = [
        ("simulador", "0006_grupo_facilitadores"),
    ]

    operations = [
        migrations.AddField(
            model_name="cenario",
            name="dados_sensor",
            field=models.TextField(
                blank=True,
                default="",
                help_text="O que o sensor mostraria sobre este problema, em linguagem simples. "
                "Se ficar em branco, o botão não aparece para o jogador.",
            ),
        ),
        migrations.AddField(
            model_name="decisao",
            name="viu_dados_sensor",
            field=models.BooleanField(
                default=False,
                help_text="O jogador abriu os dados do sensor antes de decidir (História 5)",
            ),
        ),
        migrations.RunPython(preencher, migrations.RunPython.noop),
    ]
