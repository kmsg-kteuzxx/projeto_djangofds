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

📄 **Todas as histórias (6) com cenários BDD (as Histórias 5 e 6 foram revisadas na Entrega 04):** [historias.md](historias.md)

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

**Identidade visual (moodboard do time de design):** paleta *Dark Tech* (fundo `#180E29`, cards `#23173B`, CTA `#7C3AED`, com IoT `#10B981`, sem IoT `#EF4444`, texto `#F5F3FF`). As fontes escolhidas no Figma são pagas, por isso usamos alternativas gratuitas (licença OFL) incluídas no projeto: **Michroma** no lugar de Bank Gothic (títulos de abertura), **Inter** no lugar de Aktiv Grotesk (textos) e **JetBrains Mono** no lugar de Input Mono (valores e métricas).

**Como funciona por dentro:**
* App Django `simulador` com os models `Cenario`, `Voz`, `Opcao`, `Rodada` e `Decisao`.
* Os 5 cenários iniciais são gravados no banco pela migração `0002_cenarios_iniciais` (roda sozinha no `migrate` do deploy). Também podem ser editados pelo `/admin/`.
* Views em função, sem generic views e sem Django Forms (dados lidos direto de `request.POST`).
* Testes automáticos ligados aos cenários BDD (78 no total, incluindo as Histórias 4 e 5): `python manage.py test simulador`.

---

### Entrega 04 – Gestão de cenários pelo facilitador (História 4)

O facilitador cadastra, edita, ativa/desativa e exclui cenários (com alternativas e opiniões da equipe) pelo próprio sistema, em `/simulador/facilitador/`.

* **Acesso:** só superusuário ou usuário do grupo **Facilitadores** (criado pela migração `0006`; vincule o usuário em `/admin/`). Sem login, vai para a tela de login; logado sem permissão, recebe 403.
* **Regras:** 2 a 4 alternativas, exatamente uma marcada como solução IoT, custo, prejuízo que continua e horas perdidas/mês por alternativa.
* **Ativo/desativado:** só cenários ativos aparecem para jogadores; desativar não apaga decisões nem altera partidas antigas. Cenário já jogado não pode ser excluído, só desativado.
* Código em `simulador/gestao.py` (views em função, sem Django Forms) e templates `gestao_*.html`.

🔗 **Área do facilitador:** https://projeto-djangofds.onrender.com/simulador/facilitador/
user: testefacilitador senha: testefacilitador

### Entrega 04 – Dados do sensor antes da decisão (História 5)

O jogador pode ver, antes de escolher uma alternativa, o que o sensor estaria mostrando sobre aquele problema (botão "Ver o que o sensor mostraria" na tela do cenário). É opcional e não muda a pontuação. O facilitador cadastra o texto no formulário de cenário, e o relatório final mostra em quantas decisões a pessoa consultou os dados.

* **Banco:** campos `Cenario.dados_sensor` e `Decisao.viu_dados_sensor` (migração `0007_dados_sensor`, que já preenche os dados dos 30 cenários iniciais).
* **Como funciona:** o botão abre os dados na hora, sem recarregar a página (se o JavaScript estiver desligado, cai no plano B com `?dados=1`); ao confirmar, a decisão grava que os dados foram vistos. Mudar de ideia não apaga esse registro.

### Entrega 04 – Painel de resultados do facilitador (História 6)

🛠️ Em desenvolvimento. Ver [historias.md](historias.md#história-6--painel-de-resultados-do-facilitador-entrega-04).
---

## ▶️ Como rodar o projeto

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate        # cria as tabelas e grava os cenários do simulador
python manage.py runserver
```

Acesse http://127.0.0.1:8000. Para rodar os testes: `python manage.py test simulador`.

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
