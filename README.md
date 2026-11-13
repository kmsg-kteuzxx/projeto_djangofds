# Smart Solve – Simulador de Decisões IoT

**Grupo FDS:** 10 · **Grupo Projetos:** 1

**Status do Projeto:** 🛠️ Em desenvolvimento (Entrega 04 – Testes Automatizados e CI/CD)

---

## 📌 Sobre o Projeto

Aplicação web em Django feita para a **Bzu Tech**, empresa de soluções IoT de Recife. Nossa pesquisa mostrou que as empresas reconhecem o valor dos dados, mas não sabem traduzir IoT em problemas reais de operação. Por isso o produto é um **simulador de decisões**: o usuário assume o papel de gestor, enfrenta situações operacionais (câmara fria, máquinas, água, energia, agronegócio) e vê, em reais, a diferença entre decidir sem dados e decidir com dados coletados via IoT.

---

## 🛠️ Tecnologias Que Usamos

| Categoria | Tecnologia |
| --- | --- |
| **Linguagem e Framework** | Python / Django |
| **Front-end** | HTML5 / CSS3 |
| **Banco de Dados** | SQLite (Local) / PostgreSQL (Produção - Render) |
| **Hospedagem & Deploy** | Render (Web Service & Database) |
| **Servidor WSGI & Estáticos** | Gunicorn / WhiteNoise |

---

## 🚀 Entregas e Sprints

### Sprint 1 – Análise de Concorrentes

Na primeira sprint, nos concentramos na pesquisa de mercado para estruturar o nosso *Documento de Análise de Concorrentes*. Mapeamos as soluções existentes e dividimos o trabalho nas seguintes etapas:

* **Estrutura inicial** e organização do documento de benchmark.
* **Análise detalhada** das ferramentas mapeadas (como NOVUS e Data IoT).
* **Estudo de Benchmark** cruzando recursos e funcionalidades.
* **Revisão final** e consolidação da documentação.

#### 📊 Produtos Analisados
* **NOVUS Automation / NOVUS Cloud**
* **TagoIO**
* **Ubidots**
* **Solinftec**
* **SyOS**

---

### Sprint 2 – Colocando o Projeto no Ar (Deploy & Produção)

Na segunda sprint, focamos em colocar a aplicação no ar usando a plataforma **Render**, garantindo uma infraestrutura segura, automatizada e pronta para produção:

* **Configuração do ambiente:** Adicionamos as dependências necessárias para produção (`gunicorn`, `whitenoise`, `dj-database-url` e `psycopg2-binary`).
* **Automação no Deploy (`build.sh`):** Criamos o script responsável por instalar dependências, organizar arquivos estáticos e rodar as migrações automaticamente no servidor.
* **Banco de dados dinâmico:** Ajustamos o projeto para rodar com SQLite localmente e se conectar automaticamente ao PostgreSQL em produção.
* **Entrega de arquivos estáticos:** Usamos o `WhiteNoise` para servir CSS e JS sem depender de serviços externos.
* **Infraestrutura no Render:** Subimos o serviço web e a instância do PostgreSQL (região Oregon), configurando workers em paralelo para lidar com múltiplas requisições.

🔗 **Acesse a aplicação no ar:** [https://projeto-djangofds.onrender.com](https://projeto-djangofds.onrender.com)

---

### Entrega 03 – Histórias de Usuário

📄 **Todas as histórias (6) com cenários BDD (as Histórias 5 e 6 foram revisadas e implementadas na Entrega 04):** [historias.md](historias.md)

#### ✅ Histórias implementadas

> **📝 POST-IT 1 — Simulador de decisões com IoT**
>
> **Como** empresário,
> **eu quero** um simulador de decisões,
> **para que** eu melhore as decisões da minha empresa usando dados e IoT.
>
> - Cenários reais resolvidos com sensores/automação IoT
> - Decisão em 2 cliques: escolher + confirmar (menos de 3)
> - Impacto financeiro logo após cada escolha
> - Funciona local ou na nuvem sem manutenção
> - Relatório final explicando o conceito de IoT de cada decisão
> - Identificação com nome e empresa (obrigatórios, até 80 caracteres); sem isso, não acessa os cenários
> - Ranking da equipe com pontuação de 0 a 100; clicar em uma pessoa abre o relatório dela

> **📝 POST-IT 2 — Trajetória comparada: sem IoT × com IoT**
>
> **Como** gestor que terminou uma rodada,
> **eu quero** ver o prejuízo acumulado das minhas decisões lado a lado com a mesma trajetória usando IoT,
> **para que** eu sinta a diferença entre decidir tarde e decidir em tempo real.
>
> - Prejuízo acumulado em horas de produção perdidas e em R$ (por mês e em 12 meses)
> - Trajetória recalculada como se a solução IoT tivesse sido escolhida em tudo
> - As duas colunas lado a lado, com a diferença destacada
> - Só abre depois de terminar todos os cenários

> **📝 POST-IT 3 — Trilhas de cenários por setor**
>
> **Como** gestor de uma empresa de um setor específico,
> **eu quero** escolher o setor da minha empresa e jogar cenários do meu dia a dia,
> **para que** os problemas e a linguagem façam sentido para a minha realidade.
>
> - Setor escolhido na identificação, a partir de uma lista do banco
> - Cada setor com seus próprios cenários (inclui trilha de saúde); "Geral" mantém os atuais
> - Setor gravado na rodada e ranking filtrável por setor
> - Setor inválido mostra erro e não cria rodada

**Como acessar:** página inicial → **Começar** → **Iniciar** · ranking em `/simulador/ranking/`.

**Telas (seguindo o planejamento do time de design):** T1 abertura → T2 como funciona → T3 escolha de trilha (setor) → T4 rodada X de 5 → T5 consequência (sem IoT × com IoT) → T6 progresso com prejuízo acumulado → (repete T4 a T6 a cada rodada) → T7 simulação concluída.

**Identidade visual IoTSim (manual da marca e protótipo de média fidelidade do time de design):** logo IoTSim, cores da marca `#180E29` (fundo), `#FFFFFF` (texto), `#6D28D9` e `#9333EA` (roxos), vermelho e verde só nos cards "sem IoT" e "com IoT". Botões e cards lisos, cantos arredondados, sem sombras nem efeitos, seguindo a regra do manual da marca. A fonte escolhida no Figma (Aktiv Grotesk) é paga, por isso usamos a **Inter**, alternativa gratuita (licença OFL) incluída no projeto, em todo o site.

**Como funciona por dentro:**
* App Django `simulador` com os models `Cenario`, `Voz`, `Opcao`, `Rodada` e `Decisao`.
* Os 5 cenários iniciais são gravados no banco pela migração `0002_cenarios_iniciais` (roda sozinha no `migrate` do deploy). Também podem ser editados pelo `/admin/`.
* Views em função, sem generic views e sem Django Forms (dados lidos direto de `request.POST`).
* Testes automáticos ligados aos cenários BDD: `python manage.py test simulador`.

---

### Entrega 04 – Gestão, dados do sensor e painel de resultados

#### ✅ Histórias implementadas

> **📝 POST-IT 4 — Gestão de cenários pelo facilitador**
>
> **Como** facilitador da Bzu Tech,
> **eu quero** cadastrar, editar, ativar/desativar e excluir cenários pelo próprio sistema,
> **para que** eu transforme a dor relatada pelo cliente em um cenário jogável sem mexer no código.
>
> - Acesso só para facilitadores (login próprio); sem permissão, acesso negado
> - Cenário com 2 a 4 alternativas, exatamente uma marcada como solução IoT
> - Opiniões da equipe, custo, prejuízo que continua e horas perdidas por alternativa
> - Só cenários ativos aparecem para os jogadores; desativar não altera partidas antigas
> - Cenário já jogado não pode ser excluído, só desativado

> **📝 POST-IT 5 — Dados do sensor antes da decisão**
>
> **Como** gestor diante de um problema da minha operação,
> **eu quero** ver o que o sensor estaria mostrando antes de escolher uma alternativa,
> **para que** eu perceba a diferença entre decidir por palpite e decidir com dados.
>
> - Botão "Ver o que o sensor mostraria" na tela do cenário, que abre os dados sem recarregar a página
> - Opcional: não muda a pontuação nem a decisão em 2 cliques
> - O facilitador cadastra o texto no formulário de cenário (em branco, o botão não aparece)
> - O relatório final mostra em quantas decisões a pessoa consultou os dados

> **📝 POST-IT 6 — Painel de resultados do facilitador**
>
> **Como** facilitador da Bzu Tech,
> **eu quero** acompanhar, dentro da minha área, como as pessoas estão jogando,
> **para que** eu saiba quais cenários funcionam, quais precisam de ajuste e mostre resultados aos clientes.
>
> - Link "Resultados" no menu do facilitador, com o mesmo login e permissão da História 4
> - Taxa de conclusão e pontuação média por trilha
> - Ponto de desistência: em qual cenário as partidas não finalizadas pararam
> - Adoção de IoT por cenário, com o de menor adoção destacado como "ponto de atenção"
> - Filtros por trilha e período, exportação em CSV e mensagem quando não há dados

🔗 **Área do facilitador:** https://projeto-djangofds.onrender.com/simulador/facilitador/
🔗 **Painel de resultados:** https://projeto-djangofds.onrender.com/simulador/facilitador/resultados/
user: testefacilitador senha: testefacilitador

**Como funciona por dentro:**
* **História 4:** `simulador/gestao.py` (views em função, sem Django Forms) e templates `gestao_*.html`. Facilitador = superusuário ou usuário do grupo **Facilitadores** (criado pela migração `0006`; vincule o usuário em `/admin/`). Sem login, vai para a tela de login; logado sem permissão, recebe 403.
* **História 5:** campos `Cenario.dados_sensor` e `Decisao.viu_dados_sensor` (migração `0007_dados_sensor`, que já preenche os dados dos 30 cenários iniciais). O botão abre os dados na hora com JavaScript (sem JavaScript, cai no plano B com `?dados=1`); ao confirmar, a decisão grava que os dados foram vistos.
* **História 6:** `simulador/painel.py` (view `resultados`, protegida pelo mesmo `facilitador_required`) e template `gestao_resultados.html`. Só lê o banco: contagens e médias com `Count` e filtros por trilha e data de início da partida; o CSV usa a mesma consulta, com `?formato=csv`.
* Testes automáticos ligados aos cenários BDD (90 de unidade): `python manage.py test simulador --exclude-tag=e2e`.

#### 🧪 Testes de sistema (E2E) com Selenium

Em `simulador/tests_e2e.py`, os testes abrem um Chrome de verdade (sem janela) e usam o site como uma pessoa usaria:
* **História 1:** joga a trilha inteira pelo navegador e confere o relatório.
* **História 4:** a área do facilitador pede login; o facilitador desativa um cenário pela tela.
* **História 5:** os dados do sensor abrem na hora, sem recarregar a página, e o relatório conta em quantas decisões a pessoa viu os dados.
* **História 6:** o painel abre pelo menu "Resultados", o filtro por trilha funciona e o link do CSV leva os filtros.

Como rodar: `pip install -r requirements-dev.txt` e depois `python manage.py test simulador --tag=e2e`.

🎥 **Screencast da execução dos testes E2E:** _(link do YouTube)_

#### ⚙️ CI/CD (integração e deploy contínuos)

O pipeline fica em [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml) e roda no GitHub Actions a cada push e pull request:
1. **Build:** instala as dependências, confere as migrações e roda `collectstatic`.
2. **Testes:** roda os testes de unidade e depois os testes E2E com Selenium (Chrome e ChromeDriver instalados no próprio pipeline).
3. **Deploy:** só se todos os testes passarem e o push for na `main`, o pipeline pede o deploy ao Render pelo Deploy Hook. Teste falhando = nada vai para o ar.

🎥 **Screencast do CI/CD (build, testes e deploy):** _(link do YouTube)_

🎥 **Screencast do deploy das novas histórias:** _(link do YouTube)_

📋 **Quadro da Sprint 04 (JIRA):** _(print do quadro)_

---

## ▶️ Como rodar o projeto

🤝 Quer contribuir? Veja o guia completo em [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate        # cria as tabelas e grava os cenários do simulador
python manage.py runserver
```

Acesse http://127.0.0.1:8000. Para rodar os testes: `python manage.py test simulador` (os E2E precisam de `pip install -r requirements-dev.txt`).

---

## 👥 Equipe do Projeto

| Nome Completo | E-mail Institucional | Papel / Responsabilidade |
| --- | --- | --- |
| **André Augusto de Araújo** | aaapn@cesar.school | Desenvolvedor |
| **Arthur Casanova de Azevedo** | aca5@cesar.school | Desenvolvedor |
| **Caio Ribeiro Lima Pinheiro** | crlp@cesar.school | Desenvolvedor |
| **Daniel Pereira Gomes de Faria** | dpgf@cesar.school | Desenvolvedor |
| **Eduardo Augusto Cordeiro dos Santos** | gfva@cesar.school | Desenvolvedor |
| **Gabriel Feitosa Vieira Aragão** | gabriel.email@school.com | Desenvolvedor |
| **Kauan Matheus da Silva Gomes** | kmsg@cesar.school | Desenvolvedor |
| **Alice Siqueira** | asci@cesar.school | Designer |
| **Bernardo Martins** | bmll@cesar.school | Designer |
| **Carolina Borba** | cbb3@cesar.school | Designer |
| **Mateus Coutinho** | mmc6@cesar.school | Designer |
| **Pedro Feitosa** | pamf@cesar.school | Designer |

---

## 🎥 Explicação do código do projeto Django - Bzu Tech

[https://youtu.be/AJv6ibi3YPE]

---

## 🤖 Uso de Inteligência Artificial

Usamos o Claude (Anthropic) como ferramenta de apoio durante o projeto: para revisar e sugerir histórias de usuário, ajudar a implementar partes do código (como as Histórias 5 e 6) e escrever testes e documentação. Todo o código foi revisado, testado e aplicado no repositório pela equipe, e as decisões sobre o produto foram nossas.
