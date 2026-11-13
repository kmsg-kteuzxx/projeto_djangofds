# Como contribuir com o Smart Solve

Obrigado por querer ajudar! Este guia mostra, do zero, como rodar o projeto, fazer uma mudança e enviá-la para revisão.

## 1. Preparar o ambiente

Você precisa de **Python 3.12** (ou mais novo) e **Git**. Para os testes de sistema, também do **Google Chrome**.

```bash
git clone https://github.com/kmsg-kteuzxx/projeto_djangofds.git
cd projeto_djangofds

python -m venv venv
# Windows: venv\Scripts\activate    |    Linux/macOS: source venv/bin/activate

pip install -r requirements-dev.txt   # dependências do projeto + Selenium
```

Crie um arquivo `.env` na raiz (ele não vai para o Git):

```
ENVIRONMENT=development
```

Prepare o banco e rode:

```bash
python manage.py migrate
python manage.py createsuperuser      # para entrar em /admin/ e na área do facilitador
python manage.py runserver
```

Acesse http://127.0.0.1:8000/simulador/. A área do facilitador fica em `/simulador/facilitador/`.

## 2. Entender o código

| Onde | O quê |
|---|---|
| `simulador/models.py` | Models: `Trilha`, `Cenario`, `Opcao`, `Voz`, `Rodada`, `Decisao` |
| `simulador/views.py` | Telas do jogo (Histórias 1, 2, 3 e 5) |
| `simulador/gestao.py` | Área do facilitador: login e cadastro de cenários (História 4) |
| `simulador/painel.py` | Painel de resultados do facilitador (História 6) |
| `simulador/urls.py` | Todas as URLs do app |
| `simulador/templates/simulador/` | Templates HTML |
| `simulador/migrations/` | Estrutura do banco e dados iniciais (cenários, trilhas, dados do sensor) |
| `simulador/tests.py` | Testes de unidade, um por cenário BDD |
| `simulador/tests_e2e.py` | Testes de sistema (E2E) com Selenium |
| `historias.md` | Histórias de usuário com critérios e cenários BDD |

Regras do projeto:
- Views **em função** (sem generic views).
- **Sem Django Forms**: os dados vêm de `request.POST` e são validados à mão, com mensagem de erro clara.
- Toda regra nova precisa de um **cenário BDD** em `historias.md` e de um **teste** que o verifique.
- Mudou um model? Gere a migração com `python manage.py makemigrations` e envie junto.

## 3. Rodar os testes

```bash
python manage.py test simulador --exclude-tag=e2e   # testes de unidade (rápidos)
python manage.py test simulador --tag=e2e           # testes E2E com Selenium (abrem o Chrome sem janela)
python manage.py test simulador                     # todos
```

Para ver o navegador abrindo nos testes E2E: `E2E_JANELA=1 python manage.py test simulador --tag=e2e`.
Sem Selenium ou sem Chrome, os testes E2E são pulados localmente. No CI eles são obrigatórios.

## 4. Enviar sua mudança

1. Crie uma branch a partir da `main`: `git checkout -b historia-7-nome-curto`
2. Faça commits pequenos, com mensagens no imperativo e em português. Ex.: `Adiciona filtro por setor no ranking`.
   Se o commit resolve uma issue, cite no texto: `(fixes #12)`.
3. Rode os testes antes de enviar.
4. Envie a branch (`git push -u origin historia-7-nome-curto`) e abra um **Pull Request** para a `main`, explicando:
   - o que mudou e por quê (qual história ou issue);
   - como testar;
   - prints, se mudou alguma tela.
5. O **CI** (GitHub Actions) roda os testes de unidade e os E2E automaticamente no PR. Só faça merge com o CI verde e a revisão de alguém da equipe.

## 5. Como o deploy acontece

Quando um PR entra na `main`, o pipeline `.github/workflows/ci-cd.yml` roda de novo o build e todos os testes. Se tudo passar, ele pede o deploy ao Render pelo Deploy Hook. Se algum teste falhar, **nada vai para o ar**.

Site em produção: https://projeto-djangofds.onrender.com/simulador/

## 6. Reportar problemas

Abra uma **issue** no GitHub com: o que você fez, o que esperava, o que aconteceu, e um print ou a URL. Para ideias de funcionalidade, descreva no formato de história de usuário (**Como** … **eu quero** … **para que** …).
