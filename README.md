# Personal Finance — Prova de Conceito

Este repositório contém uma Prova de Conceito de uma pequena aplicação de Gerenciamento de Finanças Pessoais, criada como base para o hackathon interno "Ctrl+Alt+AI: Hackeando a Rotina de Programação".

## Objetivo do Projeto

O projeto demonstra uma aplicação simples em Django para gerenciar lançamentos financeiros (receitas e despesas), com abordagem server-rendered e HTMX, além de exemplos de separação de responsabilidades (models e camadas HTTP).

> ⚠️ IMPORTANTE: APIs estão desautorizadas neste hackathon. Não criar nem consumir endpoints API.

## Estrutura Mínima Esperada

- `config/` — configuração do Django com split de settings em `config/settings/`
- `apps/transactions/` — app principal com layout package-first (`models/`, `http/`, `tests/`, `templates/transactions/...`)

## Como executar (desenvolvimento)

### Requisitos

- UV da Astral, [Instalação](https://docs.astral.sh/uv/getting-started/installation/)

Este projeto utiliza o helper `uv` para gerenciamento do ambiente virtual e execução de comandos. O fluxo local recomendado é:

1. Criar o ambiente virtual e instalar dependências do projeto (gerenciado por `uv`):

```bash
uv sync
```

1.1. Criar arquivo `.env` na raiz do projeto (mínimo para desenvolvimento local):

```env
SECRET_KEY=unsafe-dev-secret-key-change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

Notas rápidas de ambiente:

- Desenvolvimento (`config.settings.development`): usa defaults locais seguros para facilitar bootstrap.
- Produção (`config.settings.production`): requer `SECRET_KEY` e `ALLOWED_HOSTS` definidos no ambiente.
- Testes (`config.settings.test`): usa fallback de `SECRET_KEY` e hosts de teste, podendo ser sobrescrito por env vars.

2. Aplicar migrações:

```bash
uv run manage.py migrate
```

3. Iniciar o servidor:

```bash
uv run manage.py runserver
```

4. Abra `http://127.0.0.1:8000/` para acessar a aplicação.

Notas de instalação:

- Use `uv sync` para criar o ambiente virtual e instalar dependências.
- Use `uv run ...` para comandos do Django e scripts do projeto.

## Testes (rápido)

- Execute os testes do Django com:

```bash
uv run manage.py test
```

- Execute um teste direcionado de bootstrap com:

```bash
uv run manage.py test apps.transactions.tests.unit.test_bootstrap
```

## Sobre os Testes

Os testes usam o runner padrão do Django (baseado em unittest). Execute os testes usando o helper `uv` para rodá-los dentro do ambiente virtual do projeto:

```bash
# rodar todos os testes
uv run manage.py test

# rodar teste direcionado de bootstrap
uv run manage.py test apps.transactions.tests.unit.test_bootstrap
```

Observações:

- Este projeto usa intencionalmente o runner padrão do Django (sem pytest, por convenção do projeto).
- Para estratégias de testes adicionais, consulte `docs/testing-guide.md`.

## Observações sobre o uso do GitHub Copilot

Durante o hackathon, espera-se que a equipe documente brevemente como utilizou o `GitHub Copilot` (trechos gerados, prompts relevantes, como a IA acelerou o desenvolvimento e exemplos de auxílio em refatorações). Mantenha um registro curto no repositório (por exemplo, `COPILOT_USAGE.md`) para a apresentação.

## Documentação

- A documentação cobrindo vários aspectos do projeto — arquitetura, padrões de código, testes, etc. — está disponível na pasta `docs/` e deve ser consultada para entender decisões de design e implementação.

- [Arquitetura (architecture.md)](./docs/architecture.md)

---

## Aviso Oficial (Resumo do Hackathon)

Aviso Oficial*
*Ctrl+Alt+AI: Hackeando a Rotina de Programação*

A M2A e a IntGest promovem o hackathon interno Ctrl+Alt+AI: Hackeando a Rotina de Programação, com o objetivo de incentivar o uso prático de Inteligência Artificial no desenvolvimento de software.

O desafio é construir uma Prova de Conceito de uma mini aplicação de Gestão Financeira Pessoal, com ênfase na capacidade das equipes de usar automação no processo de desenvolvimento via VS Code com GitHub Copilot.

Todas as equipes devem usar a seguinte stack mínima:

1. Python
2. Django
3. SQLite
4. VS Code
5. GitHub Copilot

A aplicação deve incluir, no mínimo:

1. Registro de receitas
2. Registro de despesas
3. Criação ou seleção de categorias
4. Listagem de lançamentos
5. Cálculo de saldo atual
6. Edição e exclusão de registros
7. Dashboard ou resumo simples

O objetivo do hackathon não é apenas avaliar o software final, mas também como a equipe usa automação com GitHub Copilot para acelerar o desenvolvimento.

Durante a avaliação, o júri poderá solicitar a implementação de uma nova funcionalidade (a mesma para todas as equipes) para observar como a automação e a equipe respondem a mudanças de requisito.

Cada equipe deve apresentar ao final do evento:

1. A aplicação rodando localmente
2. O repositório do projeto
3. Um README curto com instruções de execução
4. Uma demonstração objetiva de como o `GitHub Copilot` foi usado durante o desenvolvimento

Critérios principais de avaliação:

1. Funcionalidade da Prova de Conceito
2. Qualidade da implementação
3. Uso efetivo de automação com GitHub Copilot
4. Capacidade de adaptação à nova funcionalidade
5. Clareza da apresentação

Regras gerais:

1. Todas as equipes partem da mesma base
2. A aplicação deve rodar localmente no momento da apresentação
3. É proibido o uso de dados sensíveis, credenciais reais ou recursos corporativos não autorizados
4. A equipe deve ser capaz de explicar claramente o que foi construído e como o Copilot foi utilizado
5. As decisões do júri são definitivas

Este hackathon foi projetado para avaliar produtividade, qualidade técnica e adaptabilidade no uso de desenvolvimento assistido por IA.

---

*README gerado/atualizado para acompanhar o resumo do hackathon.*