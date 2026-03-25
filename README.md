# Personal Finance — Prova de Conceito

Este repositório contém uma Prova de Conceito de uma pequena aplicação de Gerenciamento de Finanças Pessoais, criada como base para o hackathon interno "Ctrl+Alt+AI: Hackeando a Rotina de Programação".

## Como executar (desenvolvimento)

### Requisitos

- UV da Astral, [Instalação](https://docs.astral.sh/uv/getting-started/installation/)

Este projeto utiliza o helper `uv` para gerenciamento do ambiente virtual, instalação do Python, além da execução de comandos. O fluxo local recomendado é:

1. clonar o repositório

por ssh
```bash
$ git clone git@github.com:JoonMarion/hackathon-intgest.git
```
ou por http
```bash
$ git clone https://github.com/JoonMarion/hackathon-intgest.git
```

2. executar o comando para criar o ambiente virtual e instalar as dependências:

```bash
$ uv sync
```

3. Criar arquivo `.env` copiando o template `.env.example` e ajustando as variáveis de ambiente conforme necessário.


4. Aplicar migrações:

```bash
$ uv run manage.py migrate
```

3. Iniciar o servidor:

```bash
$ uv run manage.py runserver
```

4. Abra `http://localhost:8000/` para acessar a aplicação.

Notas de instalação:

- Use `uv sync` para criar o ambiente virtual e instalar dependências.
- Use `uv run ...` para comandos do Django e scripts do projeto.

## Testes (rápido)

- Execute os testes do Django com:

```bash
$ uv run manage.py test
```

- Execute um teste direcionado de bootstrap com:

```bash
$ uv run manage.py test apps.transactions.tests.unit.test_bootstrap
```

## Sobre os Testes

Os testes usam o runner padrão do Django (baseado em unittest). Execute os testes usando o helper `uv` para rodá-los dentro do ambiente virtual do projeto:

```bash
# rodar todos os testes
$ uv run manage.py test

# rodar teste direcionado de bootstrap
$ uv run manage.py test apps.transactions.tests.unit.test_bootstrap
```

Observações:

- Para estratégias de testes adicionais, consulte `docs/testing-guide.md`.


## Seed de Geração de dados

O projeto inclui um comando customizado para gerar dados de teste (seed) para desenvolvimento e testes. Para executar o comando de seed, use:

```bash
$ uv run manage.py seed_demo_data
``` 