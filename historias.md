# Histórias de Usuário — Bzu Tech · Simulador de Decisões IoT

> **Formato:** Como [persona], eu quero [funcionalidade], para que [benefício].
> **Validação:** cenários BDD (Dado / Quando / Então).
> **Base:** pesquisa e workshop da equipe (Figma: insights, perguntas norteadoras, ideia e funcionamento do simulador).

## Contexto do produto

A pesquisa mostrou que **as empresas reconhecem o valor dos dados, mas não sabem traduzir IoT em problemas reais de operação**. A barreira é a falta de conhecimento, não a rejeição da tecnologia. Por isso o produto é um **simulador de decisões**: o usuário assume o papel de gestor, enfrenta situações operacionais e vê a diferença entre decidir **sem dados** e decidir **com dados coletados via IoT**, em reais (R$) e sem jargão técnico.

**Perguntas norteadoras:**
- Como poderíamos tornar o "primeiro contato com IoT" tão simples quanto descrever uma dor do dia a dia?
- Como poderíamos mostrar valor do IoT sem exigir conhecimento técnico prévio?

## Visão geral

| # | História | Entrega |
|---|---|---|
| 1 | Simulador de decisões com IoT (inclui identificação do jogador e ranking da equipe) | ✅ Entrega 03 |
| 2 | Trajetória comparada: sem IoT × com IoT | ✅ Entrega 03 |
| 3 | Trilhas de cenários por setor | ✅ Entrega 03 |
| 4 | Gestão de cenários pelo facilitador | ✅ Entrega 04 |
| 5 | Dados do sensor antes da decisão | ✅ Entrega 04 |
| 6 | Painel de resultados do facilitador | ✅ Entrega 04 |

**Regra para todas as histórias:** cada uma lê e/ou grava dados no banco de dados.

---

## História 1 — Simulador de decisões com IoT ✅

**Como** empresário (João, dono de uma empresa que tem tomado decisões pouco benéficas para o crescimento do negócio),
**eu quero** um simulador de decisões que apresente situações hipotéticas com alternativas para resolver o problema e, depois da escolha, mostre como a IoT seria aplicada no mesmo cenário,
**para que** eu e minha equipe aprendamos a usar dados e automação para tomar decisões mais seguras, previsíveis e corretas, eliminando achismos e evitando desperdícios e custos desnecessários.

> O jogo ensina João a ouvir perfis diversos e analíticos (como a persona do Alex). Mudando a forma de se comunicar com o time, João desbloqueia a inteligência coletiva da empresa.
> Insight da pesquisa: o primeiro contato com IoT precisa parecer a "dor do dia a dia" da própria empresa.
> Do Figma: "cada rodada de decisão gera uma consequência e gera uma pontuação".

**Critérios de aceitação**
1. **Simulação de cenários reais:** o sistema apresenta problemas práticos de empresas que podem ser resolvidos com sensores ou automação IoT.
2. **Interface intuitiva:** a escolha das alternativas exige menos de 3 cliques (são 2: selecionar a alternativa e "Confirmar decisão").
3. **Feedback de custo/benefício:** o impacto financeiro aparece logo após cada escolha.
4. **Autonomia de funcionamento:** roda localmente ou na nuvem sem atualizações ou manutenções semanais.
5. **Relatório de aprendizado:** ao final da rodada, um resumo explica de forma didática o conceito de IoT aplicado em cada decisão.
6. **Identificação do jogador:** antes de começar, a pessoa informa nome e empresa (obrigatórios, até 80 caracteres cada). Em caso de erro, a mensagem explica o problema e o que já foi digitado continua no campo.
7. **Rodadas registradas:** ao começar, uma nova rodada é gravada no banco, sem apagar as anteriores. Sem se identificar, não é possível acessar os cenários.
8. **Relatório personalizado:** o relatório final mostra o nome da empresa e de quem jogou.
9. **Pontuação:** vai de 0 a 100 e mede quanto do resultado possível com IoT a pessoa alcançou.
10. **Ranking da equipe:** lista apenas rodadas finalizadas, da maior para a menor pontuação; cada linha mostra jogador, empresa, decisões com IoT, resultado mensal e pontuação; a rodada de quem está vendo aparece destacada.
11. **Comparar decisões:** clicar em uma pessoa do ranking abre o relatório completo das decisões dela; rodadas não finalizadas não podem ser abertas.

**Banco de dados:** lê `Cenario`, `Voz` e `Opcao`; grava `Rodada` (jogador, empresa, data de início) e `Decisao`; atualiza `Rodada.finalizada_em`; o ranking lê `Rodada`, `Decisao`, `Opcao` e `Cenario`.

### Identificação

**Cenário 1.1: Começar uma rodada**
- **Dado** que cliquei em "Começar" e estou na tela "Como funciona"
- **Quando** preencho "Maria" e "Frigorífico Boa Vista" e clico em "Iniciar"
- **Então** uma rodada é gravada com esses dados e vou para a rodada 1

**Cenário 1.2: Nome em branco**
- **Dado** que deixei o nome vazio
- **Quando** clico em "Iniciar"
- **Então** vejo "Informe o seu nome." e nenhuma rodada é criada

**Cenário 1.3: Empresa em branco**
- **Dado** que preenchi só o nome
- **Quando** clico em "Iniciar"
- **Então** vejo "Informe o nome da empresa.", o nome continua preenchido e nenhuma rodada é criada

**Cenário 1.4: Texto muito longo**
- **Dado** que digitei mais de 80 caracteres
- **Quando** clico em "Iniciar"
- **Então** vejo que o limite é de 80 caracteres e nenhuma rodada é criada

**Cenário 1.5: Acesso sem identificação**
- **Dado** que não me identifiquei
- **Quando** tento abrir um cenário pelo endereço
- **Então** sou levado à página inicial do simulador

### Decisões

**Cenário 1.6: Ver um problema real com alternativas**
- **Dado** que me identifiquei e comecei uma rodada
- **Quando** o primeiro cenário abre
- **Então** vejo o problema, o prejuízo mensal estimado, a opinião de pessoas da equipe (incluindo o Alex) e as alternativas, sendo pelo menos uma baseada em IoT

**Cenário 1.7: Decidir em 2 cliques**
- **Dado** que estou vendo a rodada 1 de 5
- **Quando** seleciono uma alternativa e clico em "Confirmar decisão"
- **Então** a decisão é gravada no banco e vejo a consequência

**Cenário 1.8: Alternativa inválida**
- **Dado** que estou vendo um cenário
- **Quando** o sistema recebe uma alternativa que não existe
- **Então** vejo "Escolha uma das alternativas para continuar" e nada é gravado

**Cenário 1.9: Mudar de ideia**
- **Dado** que já respondi um cenário
- **Quando** volto e escolho outra alternativa
- **Então** a decisão é atualizada, sem criar uma segunda decisão para o mesmo cenário

**Cenário 1.10: Ver o impacto financeiro na hora**
- **Dado** que acabei de escolher uma alternativa
- **Quando** a página de resultado abre
- **Então** vejo "Veja o que aconteceu" com o custo da solução, o prejuízo que continua e o resultado mensal da minha decisão

**Cenário 1.11: Comparar com a solução IoT**
- **Dado** que escolhi uma alternativa sem IoT
- **Quando** vejo o resultado
- **Então** vejo lado a lado o card "Sem IoT · Sua decisão" e o card "Com IoT · O que mudaria", com custo, prejuízo e resultado, e um bloco explicando como dados em tempo real mudariam o cenário

**Cenário 1.12: Escolher a solução IoT**
- **Dado** que escolhi a alternativa com IoT
- **Quando** vejo o resultado
- **Então** a minha decisão aparece como "Com IoT · Sua decisão", comparada com "Sem dados · Como estava"

### Relatório

**Cenário 1.13: Relatório de aprendizado**
- **Dado** que respondi todos os cenários
- **Quando** clico em "Ver resultado final"
- **Então** vejo "Veja o que a Bzu teria feito diferente", minha jornada comparada com a jornada com Bzu IoT, a pontuação, quantas decisões usaram IoT, o resultado em 1 ano e, para cada rodada, o conceito de IoT explicado passo a passo
- **E** vejo os botões "Quero saber mais sobre a Bzu Tech" e "Refazer simulação"

**Cenário 1.14: Relatório personalizado**
- **Dado** que terminei uma rodada como "Maria" da "Frigorífico Boa Vista"
- **Quando** vejo o relatório
- **Então** o resultado final mostra "Relatório de aprendizado da Frigorífico Boa Vista" e que Maria jogou

**Cenário 1.15: Relatório antes da hora**
- **Dado** que ainda faltam cenários
- **Quando** tento abrir o relatório
- **Então** sou levado ao primeiro cenário que falta

**Cenário 1.16: Pontuação máxima**
- **Dado** que escolhi a solução IoT em todos os cenários
- **Quando** termino a rodada
- **Então** minha pontuação é 100

### Ranking da equipe

**Cenário 1.17: Ranking vazio**
- **Dado** que ninguém terminou uma rodada
- **Quando** abro o ranking
- **Então** vejo um convite para ser o primeiro a jogar

**Cenário 1.18: Rodada finalizada entra no ranking**
- **Dado** que Maria terminou uma rodada
- **Quando** abro o ranking
- **Então** vejo Maria, a empresa dela e a pontuação

**Cenário 1.19: Rodada em andamento fica de fora**
- **Dado** que Pedro respondeu só um cenário
- **Quando** abro o ranking
- **Então** Pedro não aparece

**Cenário 1.20: Ordem por pontuação**
- **Dado** que uma pessoa escolheu IoT em tudo e outra não escolheu nenhuma vez
- **Quando** abro o ranking
- **Então** quem usou IoT aparece primeiro

**Cenário 1.21: Comparar decisões**
- **Dado** que estou no ranking
- **Quando** clico no nome de uma pessoa
- **Então** vejo o relatório com cada decisão que ela tomou

**Cenário 1.22: Rodada incompleta**
- **Dado** que uma rodada ainda não terminou
- **Quando** alguém tenta abri-la pelo endereço
- **Então** recebe "página não encontrada"

### Funcionamento

**Cenário 1.23: Funcionar logo após o deploy**
- **Dado** que o sistema acabou de ser publicado e só rodou o `migrate`
- **Quando** acesso o simulador
- **Então** os cenários já estão no banco e todas as páginas abrem, sem cadastro manual

---

## História 2 — Trajetória comparada: sem IoT × com IoT ✅

**Como** gestor que terminou uma rodada,
**eu quero** ver o prejuízo acumulado das minhas decisões em horas de produção perdidas e em reais, lado a lado com a mesma trajetória usando monitoramento IoT,
**para que** eu sinta a diferença entre uma decisão tardia e uma decisão em tempo real e entenda por que dados operacionais importam, sem jargão técnico.

> Do Figma (Funcionamento): "Terminada a simulação, o prejuízo acumulado é revelado e traduzido em números reais (horas de produção e prejuízo financeiro estimado). Depois disso o jogo reconstrói a trajetória do usuário, mas com o monitoramento via IoT. Ao final, mostramos uma comparação lado a lado dos dois cenários."

**Critérios de aceitação**
1. Cada alternativa tem, no banco, as horas de produção perdidas por mês.
2. Ao final da rodada aparece o total acumulado em horas e em R$ (por mês e em 12 meses).
3. A mesma trajetória é recalculada como se a solução IoT tivesse sido escolhida em todos os cenários.
4. As duas trajetórias aparecem lado a lado, com a diferença destacada.
5. A linguagem fala de perdas, segurança e qualidade, sem termos técnicos sem explicação.

**Cenário 2.1: Prejuízo acumulado revelado**
- **Dado** que terminei a rodada
- **Quando** abro a trajetória
- **Então** vejo o total de horas de produção perdidas e o prejuízo em R$ das minhas decisões

**Cenário 2.2: Trajetória reconstruída com IoT**
- **Dado** que estou vendo minha trajetória
- **Quando** a comparação carrega
- **Então** vejo, ao lado, as mesmas situações resolvidas com monitoramento IoT e quanto seria economizado

**Cenário 2.3: Tudo com IoT**
- **Dado** que escolhi IoT em todos os cenários
- **Quando** abro a trajetória
- **Então** as duas colunas são iguais e vejo uma mensagem de parabéns

**Cenário 2.4: Acesso antes de terminar**
- **Dado** que ainda faltam cenários
- **Quando** tento abrir a trajetória
- **Então** sou levado ao primeiro cenário que falta

---

## História 3 — Trilhas de cenários por setor ✅

**Como** gestor de uma empresa de um setor específico (ex.: saúde, alimentos, indústria),
**eu quero** escolher o setor da minha empresa e jogar cenários do meu dia a dia,
**para que** os problemas e a linguagem façam sentido para a minha realidade.

> Do Figma (Insights para o produto): "experiência específica voltada para perfis prioritários" e "linguagem focada nas necessidades do cliente, destacando redução de perdas, segurança, qualidade e conformidade com termos técnicos contextualizados ao setor de saúde".

**Critérios de aceitação**
1. Na identificação, a pessoa escolhe o setor da empresa a partir de uma lista vinda do banco.
2. Cada setor tem seus próprios cenários (pelo menos 3), incluindo uma trilha de saúde (ex.: armazenamento de vacinas e bolsas de sangue).
3. A opção "Geral" continua mostrando os cenários atuais.
4. O ranking pode ser filtrado por setor.
5. O setor escolhido fica gravado na rodada.

**Cenário 3.1: Escolher o setor de saúde**
- **Dado** que estou me identificando
- **Quando** escolho o setor "Saúde" e começo
- **Então** vejo apenas cenários de saúde, com termos como conformidade e rastreabilidade

**Cenário 3.2: Setor geral**
- **Dado** que escolhi "Geral"
- **Quando** começo
- **Então** jogo os cenários de vários setores

**Cenário 3.3: Ranking por setor**
- **Dado** que existem rodadas de setores diferentes
- **Quando** filtro o ranking por "Saúde"
- **Então** vejo apenas rodadas de saúde

**Cenário 3.4: Setor inválido**
- **Dado** que o sistema recebe um setor que não existe
- **Quando** tento começar
- **Então** vejo uma mensagem de erro e nenhuma rodada é criada

---

## História 4 — Gestão de cenários pelo facilitador (Entrega 04)

**Como** facilitador da Bzu Tech (consultor que aplica o simulador com empresas clientes),
**eu quero** cadastrar, editar e desativar cenários, com suas alternativas e as opiniões da equipe, por telas do próprio sistema,
**para que** eu adapte o simulador aos problemas reais de cada cliente sem depender de um programador para mexer no código ou no banco.

> Insight da pesquisa: as empresas não sabem traduzir IoT em problemas reais da operação. Quem conhece essas dores é o facilitador, que conversa com o cliente; por isso ele precisa conseguir transformar a dor relatada em um cenário jogável.

**Critérios de aceitação**
1. Só usuários com login de facilitador acessam as telas de gestão; jogadores comuns não veem essas telas.
2. Um cenário tem título, descrição do problema, prejuízo mensal estimado, setor e conceito de IoT explicado.
3. Cada cenário precisa ter de 2 a 4 alternativas, com custo, prejuízo que continua e horas perdidas por mês, e **exatamente uma** alternativa marcada como solução IoT.
4. É possível adicionar opiniões da equipe (`Voz`) com nome da pessoa, cargo e fala.
5. Um cenário só aparece para os jogadores quando está **ativo**; desativar não apaga as decisões já tomadas nem altera rodadas antigas.
6. Ao salvar com erro, a mensagem explica o problema e o que já foi digitado continua nos campos.

**Banco de dados:** grava e atualiza `Cenario`, `Opcao` e `Voz`; atualiza `Cenario.ativo`; lê `Decisao` para impedir exclusão de cenários já jogados.

**Cenário 4.1: Cadastrar um novo cenário**
- **Dado** que estou logado como facilitador
- **Quando** preencho o cenário "Câmara fria sem alarme", cadastro 3 alternativas (uma delas IoT) e clico em "Salvar"
- **Então** o cenário é gravado no banco e aparece na lista de cenários

**Cenário 4.2: Cenário sem solução IoT**
- **Dado** que estou cadastrando um cenário
- **Quando** salvo sem marcar nenhuma alternativa como IoT
- **Então** vejo "Marque uma alternativa como solução IoT." e nada é gravado

**Cenário 4.3: Alternativas insuficientes**
- **Dado** que cadastrei só uma alternativa
- **Quando** clico em "Salvar"
- **Então** vejo "Cadastre pelo menos 2 alternativas." e os dados digitados continuam na tela

**Cenário 4.4: Editar um cenário**
- **Dado** que existe o cenário "Câmara fria sem alarme"
- **Quando** altero o prejuízo mensal e salvo
- **Então** os novos jogadores veem o valor atualizado

**Cenário 4.5: Desativar um cenário**
- **Dado** que um cenário está ativo e já foi jogado por Maria
- **Quando** clico em "Desativar"
- **Então** ele deixa de aparecer para novas rodadas, mas o relatório de Maria continua mostrando a decisão dela

**Cenário 4.6: Acesso sem permissão**
- **Dado** que não estou logado como facilitador
- **Quando** tento abrir a tela de gestão pelo endereço
- **Então** sou levado à tela de login

---

## História 5 — Dados do sensor antes da decisão (Entrega 04) ✅

**Como** gestor diante de um problema da minha operação,
**eu quero** ver o que o sensor estaria mostrando sobre esse problema antes de escolher uma alternativa,
**para que** eu perceba, na prática, a diferença entre decidir por palpite e decidir com dados.

> Insight da pesquisa: as empresas reconhecem o valor dos dados, mas não sabem traduzir IoT em problemas reais. Hoje o jogador só vê "dados" depois de decidir (no resultado e no relatório). Esta história traz o dado para o momento da decisão, que é a promessa central do produto.

**Critérios de aceitação**
1. Cada cenário pode ter um texto "O que o sensor mostraria", escrito em linguagem simples (ex.: "A temperatura passou de 8 °C por 3 horas na madrugada, sem ninguém perceber"), gravado no banco.
2. Na tela do cenário, se houver esse texto, aparece o botão "Ver o que o sensor mostraria"; ao clicar, o texto é exibido sem sair da página e as alternativas continuam disponíveis.
3. Ver os dados é opcional e **não altera a pontuação** nem a regra de 2 cliques da História 1.
4. O facilitador cadastra e edita esse texto no formulário de cenário da História 4, sem mexer no código.
5. Cenário sem o texto não mostra o botão.
6. A rodada registra se o jogador abriu os dados do sensor antes de decidir, e o relatório final mostra em quantas decisões isso aconteceu.

**Banco de dados:** acrescenta `Cenario.dados_sensor` (texto, opcional); acrescenta `Decisao.viu_dados_sensor` (verdadeiro/falso); lê e grava em `Cenario` e `Decisao`.

**Cenário 5.1: Ver os dados do sensor**
- **Dado** que estou no cenário "Câmara fria sem alarme" e ele tem dados do sensor cadastrados
- **Quando** clico em "Ver o que o sensor mostraria"
- **Então** vejo o texto com as leituras e continuo vendo as alternativas

**Cenário 5.2: Cenário sem dados**
- **Dado** que o cenário não tem dados do sensor cadastrados
- **Quando** abro o cenário
- **Então** o botão não aparece

**Cenário 5.3: Pontuação não muda**
- **Dado** que abri os dados do sensor em todos os cenários e escolhi a solução IoT em todos
- **Quando** termino a rodada
- **Então** minha pontuação é 100, igual a quem não abriu os dados

**Cenário 5.4: Registro de quem consultou**
- **Dado** que abri os dados do sensor em 2 de 5 cenários antes de decidir
- **Quando** vejo o relatório final
- **Então** vejo que consultei os dados em 2 de 5 decisões

**Cenário 5.5: Facilitador cadastra os dados**
- **Dado** que estou logado como facilitador e editando um cenário
- **Quando** preencho "O que o sensor mostraria" e salvo
- **Então** os novos jogadores veem o botão nesse cenário

---

## História 6 — Painel de resultados do facilitador (Entrega 04) ✅

**Como** facilitador da Bzu Tech,
**eu quero** acompanhar, dentro da minha área de gestão, como as pessoas estão jogando (quem termina, onde desiste e quanto usa IoT),
**para que** eu saiba quais cenários funcionam, quais precisam ser ajustados e consiga mostrar resultados concretos às empresas clientes.

> Continuação da História 4: o facilitador já cadastra cenários, mas ainda não tem como saber se eles funcionam. O painel fecha esse ciclo (cadastrar, jogar, medir, ajustar).

**Critérios de aceitação**
1. O painel fica dentro da área do facilitador, com o link "Resultados" no menu da tela de gestão, ao lado de "Cenários". Não existe endereço solto: o acesso usa o mesmo login e a mesma permissão da História 4 (grupo Facilitadores ou superusuário). Sem login, vai para a tela de login; logado sem permissão, recebe 403.
2. **Taxa de conclusão** por trilha = rodadas finalizadas ÷ rodadas iniciadas.
3. **Pontuação média** por trilha, considerando apenas rodadas finalizadas.
4. **Ponto de desistência:** para as rodadas não finalizadas, o painel mostra em qual cenário cada uma parou (o primeiro cenário da trilha sem decisão) e quantas pararam em cada cenário.
5. **Adoção de IoT por cenário:** porcentagem de jogadores que escolheram a solução IoT; o cenário com menor adoção aparece destacado como "ponto de atenção".
6. Filtros por trilha e por período (data inicial e final). Os números da tela respeitam os filtros.
7. Botão "Exportar CSV" com a tabela filtrada.
8. Sem dados no filtro escolhido, o painel mostra uma mensagem explicando e não quebra.

**Banco de dados:** só leitura. Lê `Rodada`, `Decisao`, `Opcao`, `Cenario` e `Trilha` com consultas agregadas (contagem, média e agrupamento).

**Cenário 6.1: Acesso pelo menu do facilitador**
- **Dado** que estou logado como facilitador na tela de gestão de cenários
- **Quando** clico em "Resultados"
- **Então** o painel abre sem eu precisar digitar outro endereço

**Cenário 6.2: Acesso sem permissão**
- **Dado** que não estou logado como facilitador
- **Quando** tento abrir o painel pelo endereço
- **Então** sou levado à tela de login

**Cenário 6.3: Taxa de conclusão**
- **Dado** que 10 rodadas foram iniciadas e 4 finalizadas na trilha Saúde
- **Quando** abro o painel
- **Então** vejo 40% de conclusão para essa trilha

**Cenário 6.4: Ponto de desistência**
- **Dado** que 3 rodadas pararam antes de responder o cenário 3
- **Quando** abro o painel
- **Então** o cenário 3 aparece com 3 desistências

**Cenário 6.5: Ponto de atenção**
- **Dado** que quase ninguém escolheu IoT no cenário de cadeia fria
- **Quando** abro o painel
- **Então** esse cenário aparece destacado como "ponto de atenção"

**Cenário 6.6: Filtrar por trilha e período**
- **Dado** que existem rodadas de trilhas e datas diferentes
- **Quando** filtro por "Saúde" e pelo mês atual
- **Então** os números mostram só as rodadas de saúde daquele mês

**Cenário 6.7: Exportar CSV**
- **Dado** que apliquei um filtro
- **Quando** clico em "Exportar CSV"
- **Então** baixo um arquivo com as linhas da tabela filtrada

**Cenário 6.8: Sem dados**
- **Dado** que nenhuma rodada foi iniciada no período escolhido
- **Quando** abro o painel
- **Então** vejo uma mensagem informando que não há rodadas no período, sem erro

---

> Os cenários das histórias 1 a 6 são verificados pelos testes automáticos em `simulador/tests.py` (`python manage.py test simulador`).
