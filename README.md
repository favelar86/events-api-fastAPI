# Events API

API de gerenciamento de eventos financeiros construída com FastAPI, PostgreSQL e Arquitetura Hexagonal.

> Este guia é construído em partes — cada parte começa criando uma branch, termina com um commit, push e merge na `develop`. Ao final você tem um histórico limpo e rastreável, exatamente como se faz no mercado.

---

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando
- [VS Code](https://code.visualstudio.com/) com a extensão **Dev Containers** instalada

---

## Conceitos rápidos antes de começar

**Arquitetura Hexagonal** — o núcleo da aplicação (regras de negócio) fica isolado. Banco de dados, HTTP e qualquer tecnologia externa ficam nas bordas, conectados por adaptadores. Trocar PostgreSQL por outro banco? Só muda o adaptador.

**SOLID** — cinco princípios de design que tornam o código mais fácil de manter e testar. O mais visível aqui é o **D** (Dependency Inversion): o serviço depende de uma interface, não do PostgreSQL diretamente.

**Repository Pattern** — isola todo o acesso ao banco em uma classe dedicada.

**Dependency Injection** — as dependências são passadas de fora, não criadas dentro da classe. Isso é o que permite trocar o repositório real por um mock nos testes.

---

## Configuração inicial do repositório

Após criar o repositório no GitHub com licença e descrição, clone e configure as branches base:

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/events-api.git
cd events-api

# Crie a branch develop a partir da main
git checkout -b develop
git push -u origin develop
```

> **Por que develop?** É o padrão do mercado para projetos com múltiplos desenvolvedores.
> `main` recebe apenas código estável e revisado. `develop` é onde as features se acumulam antes de ir para produção.
> Cada parte deste tutorial cria uma branch a partir da `develop`, faz o trabalho e volta para ela via merge.

O fluxo de cada parte será sempre:

```
develop
   └── feature/parte-X-descricao   ← você trabalha aqui
         └── merge de volta para develop
```

---

## Parte 1 — Estrutura base do projeto

### Início: criar a branch

```bash
git checkout develop
git checkout -b feature/parte-1-estrutura-base
```

### 1.1 Criar a estrutura de pastas

```bash
# Pacotes da aplicação
mkdir -p src/events_api/domain/entities
mkdir -p src/events_api/domain/ports
mkdir -p src/events_api/application/services
mkdir -p src/events_api/adapters/inbound/http/routers
mkdir -p src/events_api/adapters/inbound/http/schemas
mkdir -p src/events_api/adapters/outbound/persistence/models
mkdir -p src/events_api/adapters/outbound/persistence/repositories
mkdir -p src/events_api/infrastructure
mkdir -p migrations/versions
mkdir -p tests/unit/domain
mkdir -p tests/unit/application
mkdir -p tests/integration
mkdir -p .devcontainer
mkdir -p .vscode

# __init__.py em todos os pacotes Python
touch src/__init__.py
touch src/events_api/__init__.py
touch src/events_api/domain/__init__.py
touch src/events_api/domain/entities/__init__.py
touch src/events_api/domain/ports/__init__.py
touch src/events_api/application/__init__.py
touch src/events_api/application/services/__init__.py
touch src/events_api/adapters/__init__.py
touch src/events_api/adapters/inbound/__init__.py
touch src/events_api/adapters/inbound/http/__init__.py
touch src/events_api/adapters/inbound/http/routers/__init__.py
touch src/events_api/adapters/inbound/http/schemas/__init__.py
touch src/events_api/adapters/outbound/__init__.py
touch src/events_api/adapters/outbound/persistence/__init__.py
touch src/events_api/adapters/outbound/persistence/models/__init__.py
touch src/events_api/adapters/outbound/persistence/repositories/__init__.py
touch src/events_api/infrastructure/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/unit/domain/__init__.py
touch tests/unit/application/__init__.py
touch tests/integration/__init__.py

# conftest.py em cada nível de testes
touch conftest.py
touch tests/conftest.py
touch tests/unit/domain/conftest.py
touch tests/unit/application/conftest.py
touch tests/integration/conftest.py
```

Estrutura resultante:

```
events-api/
├── conftest.py                          # raiz — necessário para o pytest encontrar src/
├── src/
│   └── events_api/
│       ├── domain/
│       │   ├── entities/
│       │   └── ports/
│       ├── application/
│       │   └── services/
│       ├── adapters/
│       │   ├── inbound/http/
│       │   └── outbound/persistence/
│       └── infrastructure/
├── migrations/
│   └── versions/
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── domain/
│   │   └── application/
│   └── integration/
└── .devcontainer/
```

### 1.2 Criar `.gitignore`

```
.env
__pycache__/
*.pyc
*.pyo
.pytest_cache/
htmlcov/
.coverage
```

### Fim: commit, push e merge

```bash
git add .
git commit -m "chore: estrutura base do projeto"
git push -u origin feature/parte-1-estrutura-base

# Merge na develop
git checkout develop
git merge feature/parte-1-estrutura-base
git push origin develop
```

---

## Parte 2 — DevContainer e Docker

### Início: criar a branch

```bash
git checkout develop
git checkout -b feature/parte-2-devcontainer
```

### 2.1 `.devcontainer/devcontainer.json`

> **O que é:** arquivo que diz ao VS Code como montar o ambiente de desenvolvimento dentro do container. Define extensões instaladas automaticamente, configurações do editor, portas expostas e o comando executado ao criar o container.

```json
{
  "name": "Events API",
  "dockerComposeFile": "docker-compose.yml",
  "service": "app",
  "workspaceFolder": "/workspace",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.black-formatter",
        "ms-python.isort",
        "ms-python.pylint",
        "mtxr.sqltools",
        "mtxr.sqltools-driver-pg"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "editor.formatOnSave": true,
        "[python]": {
          "editor.defaultFormatter": "ms-python.black-formatter"
        },
        "python.testing.pytestEnabled": true,
        "python.testing.unittestEnabled": false,
        "python.testing.pytestArgs": ["tests", "-v"]
      }
    }
  },
  "postCreateCommand": "pip install -e '.[dev]'",
  "forwardPorts": [8000, 5432],
  "remoteEnv": {
    "DATABASE_URL": "postgresql://postgres:postgres@db:5432/events_db",
    "ENVIRONMENT": "development"
  }
}
```

Campos principais:

| Campo | O que faz |
|-------|-----------|
| `dockerComposeFile` | Qual arquivo Docker Compose usar para subir os serviços |
| `service` | Qual serviço do Compose é o container principal do VS Code |
| `extensions` | Extensões instaladas automaticamente para todos no time |
| `postCreateCommand` | Comando executado uma vez ao criar o container — instala as dependências |
| `forwardPorts` | Portas do container expostas na sua máquina: 8000 (API) e 5432 (banco) |
| `remoteEnv` | Variáveis de ambiente disponíveis dentro do container |

> As migrations são aplicadas separadamente na Parte 9 para que você veja cada etapa.

### 2.2 `.devcontainer/docker-compose.yml`

> **O que é:** define os serviços que sobem junto com o DevContainer. Aqui temos dois: `app` (onde o VS Code abre) e `db` (PostgreSQL). O `app` só inicia depois que o banco estiver pronto — garantido pelo `healthcheck`.

```yaml
version: '3.8'

services:
  app:
    build:
      context: ..
      dockerfile: Dockerfile
    volumes:
      - ..:/workspace:cached
    command: sleep infinity
    depends_on:
      db:
        condition: service_healthy
    networks:
      - events-network

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: events_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - events-network

volumes:
  postgres_data:

networks:
  events-network:
    driver: bridge
```

Pontos importantes:

| Campo | O que faz |
|-------|-----------|
| `context: ..` | O Docker busca o `Dockerfile` na raiz do projeto (um nível acima de `.devcontainer/`) |
| `volumes: ..:/workspace:cached` | Monta a pasta do projeto dentro do container — suas edições aparecem lá instantaneamente |
| `command: sleep infinity` | Mantém o container `app` rodando sem fazer nada, para o VS Code poder entrar nele |
| `depends_on: condition: service_healthy` | O container `app` só sobe depois que o banco passar no healthcheck |
| `postgres_data` | Volume nomeado — os dados do banco persistem entre restarts do container |

### 2.3 `Dockerfile`

> **O que é:** receita para construir a imagem do container `app`. Parte de uma imagem oficial do Python, instala dependências do sistema, copia o projeto e instala os pacotes Python. Fica na **raiz do projeto**.

```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    curl git libpq-dev gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY pyproject.toml .
RUN pip install --upgrade pip && pip install -e ".[dev]"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.events_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

Por que copiar o `pyproject.toml` antes do resto do código? O Docker cacheia cada instrução em camadas. Se você copiar tudo de uma vez, qualquer alteração no código força a reinstalação de todas as dependências. Separando, o `pip install` só roda novamente quando o `pyproject.toml` mudar.

### 2.4 `.vscode/settings.json`

> **O que é:** configurações do VS Code específicas do projeto, versionadas no repositório. Garante que todos no time usem as mesmas configurações de testes — independente do que cada um tem no VS Code instalado na máquina.

```json
{
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": ["tests", "-v"]
}
```

Com isso, o ícone de tubinho de ensaio (⚗️ Testing) na barra lateral do VS Code já mostra todos os testes organizados em árvore, prontos para rodar com um clique.

### 2.5 `pyproject.toml`

> **O que é:** arquivo central de configuração do projeto Python. Define as dependências, versão do Python, configurações do formatador, do linter e do pytest. Substitui o antigo `setup.py` e vários arquivos de configuração separados.

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "events-api"
version = "0.1.0"
description = "API de Eventos com FastAPI e Arquitetura Hexagonal"
requires-python = ">=3.12"

dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.29.0",
    "sqlalchemy>=2.0.0",
    "alembic>=1.13.0",
    "psycopg2-binary>=2.9.9",
    "pydantic>=2.6.0",
    "pydantic-settings>=2.2.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=5.0.0",
    "httpx>=0.27.0",
    "black>=24.0.0",
    "isort>=5.13.0",
    "pylint>=3.1.0",
]

[tool.hatch.build.targets.wheel]
packages = ["src/events_api"]

[tool.black]
line-length = 88
target-version = ["py312"]

[tool.isort]
profile = "black"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
pythonpath = ["."]

[tool.pylint.messages_control]
disable = ["missing-class-docstring"]
```

Seções principais:

| Seção | O que configura |
|-------|----------------|
| `[project] dependencies` | Pacotes necessários para rodar a aplicação em produção |
| `[project.optional-dependencies] dev` | Pacotes extras só para desenvolvimento e testes |
| `[tool.black]` | Formatador de código — linha máxima de 88 caracteres |
| `[tool.pytest.ini_options]` | Onde o pytest procura os testes e como o Python encontra o `src/` |
| `[tool.pylint]` | Desabilita avisos de docstring em classes de teste |

### 2.6 `.env.example`

> **O que é:** modelo do arquivo de variáveis de ambiente. É commitado no repositório para que todos saibam quais variáveis são necessárias, mas **sem valores reais**. Cada desenvolvedor copia para `.env` (que fica no `.gitignore`) e preenche com seus próprios valores.

```bash
DATABASE_URL=postgresql://postgres:postgres@db:5432/events_db
ENVIRONMENT=development
DEBUG=false
```

### 2.7 Subir o DevContainer

> ⚠️ **Antes de continuar:** certifique-se de que o **Docker Desktop está aberto e rodando**. O ícone na bandeja do sistema deve estar verde. Sem o Docker rodando, o VS Code não consegue construir o container e o DevContainer não vai abrir.

Passos:

1. Abra a pasta do projeto no VS Code (`File → Open Folder`)
2. O VS Code vai detectar a pasta `.devcontainer/` e exibir uma notificação no canto inferior direito: **"Reopen in Container"** — clique nela
3. Se a notificação não aparecer: pressione `Ctrl+Shift+P` → digite `Dev Containers: Reopen in Container` → Enter
4. Aguarde o build — na **primeira vez** leva 2-5 minutos (baixa a imagem Python e instala os pacotes). Nas próximas vezes é muito mais rápido pois usa o cache do Docker
5. Quando terminar, o terminal do VS Code já estará **dentro do container**

### 2.8 Verificar o ambiente

Com o terminal aberto dentro do container, execute:

```bash
# Python enxerga o projeto?
python -c "import src.events_api; print('ok')"

# Dependências instaladas?
pip show fastapi sqlalchemy alembic

# Banco acessível?
psql $DATABASE_URL -c "SELECT version();"
```

### Fim: commit, push e merge

```bash
git add .
git commit -m "chore: devcontainer, docker e dependências"
git push -u origin feature/parte-2-devcontainer

# Merge na develop
git checkout develop
git merge feature/parte-2-devcontainer
git push origin develop
```

---

## Parte 3 — Domain: exceções

### Início: criar a branch

```bash
git checkout develop
git checkout -b feature/parte-3-domain-excecoes
```

As exceções de domínio traduzem erros de negócio em tipos específicos. Isso permite que a camada HTTP converta cada uma no status HTTP correto sem conhecer os detalhes da regra de negócio.

### 3.1 `src/events_api/domain/exceptions.py`

```python
"""Exceções do Domínio."""


class DomainException(Exception):
    """Exceção base — todas as outras herdam desta."""


class EventNotFoundException(DomainException):
    """Lançada quando um evento não é encontrado."""

    def __init__(self, identifier: int | str) -> None:
        self.identifier = identifier
        super().__init__(f"Evento não encontrado: {identifier}")


class EventAlreadyExistsException(DomainException):
    """Lançada ao tentar criar um evento com número já existente."""

    def __init__(self, numero_evento: int) -> None:
        self.numero_evento = numero_evento
        super().__init__(f"Evento com número {numero_evento} já existe")
```

### Fim: commit, push e merge

```bash
git add .
git commit -m "feat(domain): exceções de domínio"
git push -u origin feature/parte-3-domain-excecoes

# Merge na develop
git checkout develop
git merge feature/parte-3-domain-excecoes
git push origin develop
```

---

## Parte 4 — Domain: entidade Event + testes

### Início: criar a branch

```bash
git checkout develop
git checkout -b feature/parte-4-domain-entity
```

A entidade é o objeto mais importante da aplicação. Ela carrega as regras de negócio e não depende de nada externo — sem banco, sem HTTP. Por isso é a primeira coisa a ser implementada e testada.

### 4.1 `src/events_api/domain/entities/event.py`

```python
"""Entidade de Domínio: Evento."""
from dataclasses import dataclass, field
from datetime import datetime, UTC
from decimal import Decimal


@dataclass
class Event:
    """
    Representa um Evento no domínio da aplicação.

    @dataclass gera automaticamente __init__, __repr__ e __eq__,
    evitando código repetitivo.
    """

    numero_evento: int
    valor: Decimal
    data_hora_atualizacao: datetime
    id: int | None = field(default=None)

    def __post_init__(self) -> None:
        """Validações executadas automaticamente ao criar o objeto."""
        self._validate()

    def _validate(self) -> None:
        """
        Ponto único de validação — tanto na criação quanto após updates.
        Princípio DRY: a regra existe em um único lugar.
        """
        if self.numero_evento <= 0:
            raise ValueError(
                f"Número do evento deve ser positivo, recebido: {self.numero_evento}"
            )
        if self.valor < Decimal("0"):
            raise ValueError(
                f"Valor do evento não pode ser negativo, recebido: {self.valor}"
            )

    def update_valor(self, novo_valor: Decimal) -> None:
        """Atualiza o valor e o timestamp, revalidando o estado completo."""
        self.valor = novo_valor
        self.data_hora_atualizacao = datetime.now(UTC)
        self._validate()

    def update_numero_evento(self, novo_numero: int) -> None:
        """Atualiza o número do evento e o timestamp, revalidando o estado completo."""
        self.numero_evento = novo_numero
        self.data_hora_atualizacao = datetime.now(UTC)
        self._validate()

    def to_dict(self) -> dict:
        """Converte a entidade para dicionário."""
        return {
            "id": self.id,
            "numero_evento": self.numero_evento,
            "valor": float(self.valor),
            "data_hora_atualizacao": self.data_hora_atualizacao.isoformat(),
        }
```

### 4.2 `tests/unit/domain/conftest.py`

```python
"""Fixtures dos testes de domínio."""
from datetime import datetime, UTC
from decimal import Decimal

import pytest

from src.events_api.domain.entities.event import Event


@pytest.fixture
def valid_event() -> Event:
    """Nova instância criada para cada teste — sem compartilhamento de estado."""
    return Event(
        numero_evento=2400,
        valor=Decimal("10.00"),
        data_hora_atualizacao=datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC),
    )


@pytest.fixture
def persisted_event() -> Event:
    """Evento que simula já ter sido salvo no banco (tem ID)."""
    return Event(
        id=1,
        numero_evento=2400,
        valor=Decimal("10.00"),
        data_hora_atualizacao=datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC),
    )
```

### 4.3 `tests/unit/domain/test_event_entity.py`

```python
"""Testes da Entidade de Domínio: Event."""
from datetime import datetime, UTC
from decimal import Decimal
import time

import pytest

from src.events_api.domain.entities.event import Event


class TestEventCreation:
    """Testa a criação de eventos com dados válidos e inválidos."""

    def test_create_valid_event(self):
        """Criação com dados válidos deve funcionar sem erros."""
        event = Event(
            numero_evento=2400,
            valor=Decimal("10.00"),
            data_hora_atualizacao=datetime.now(UTC),
        )
        assert event.numero_evento == 2400
        assert event.valor == Decimal("10.00")
        assert event.id is None

    def test_create_event_with_id(self, persisted_event):
        """Evento com ID representa um registro já existente no banco."""
        assert persisted_event.id == 1

    def test_create_event_with_zero_valor_is_allowed(self):
        """Valor zero é permitido."""
        event = Event(
            numero_evento=1,
            valor=Decimal("0.00"),
            data_hora_atualizacao=datetime.now(UTC),
        )
        assert event.valor == Decimal("0.00")

    def test_create_event_with_large_valor(self):
        """Valores grandes devem ser aceitos."""
        event = Event(
            numero_evento=1,
            valor=Decimal("999999.99"),
            data_hora_atualizacao=datetime.now(UTC),
        )
        assert event.valor == Decimal("999999.99")


class TestEventValidation:
    """Testa o _validate como ponto único de validação de regras de negócio."""

    def test_negative_numero_raises_on_creation(self):
        """Número negativo deve falhar na criação via __post_init__."""
        with pytest.raises(ValueError, match="Número do evento deve ser positivo"):
            Event(numero_evento=-1, valor=Decimal("10.00"), data_hora_atualizacao=datetime.now(UTC))

    def test_zero_numero_raises_on_creation(self):
        """Número zero não é permitido."""
        with pytest.raises(ValueError, match="Número do evento deve ser positivo"):
            Event(numero_evento=0, valor=Decimal("10.00"), data_hora_atualizacao=datetime.now(UTC))

    def test_negative_valor_raises_on_creation(self):
        """Valor negativo deve falhar na criação."""
        with pytest.raises(ValueError, match="Valor do evento não pode ser negativo"):
            Event(numero_evento=2400, valor=Decimal("-0.01"), data_hora_atualizacao=datetime.now(UTC))


class TestUpdateValor:
    """Testa o método update_valor e seus efeitos colaterais."""

    def test_update_valor_changes_value(self, valid_event):
        """Novo valor deve ser persistido na entidade."""
        valid_event.update_valor(Decimal("20.00"))
        assert valid_event.valor == Decimal("20.00")

    def test_update_valor_refreshes_timestamp(self, valid_event):
        """Timestamp deve ser posterior ao original após update."""
        original_timestamp = valid_event.data_hora_atualizacao
        time.sleep(0.01)
        valid_event.update_valor(Decimal("20.00"))
        assert valid_event.data_hora_atualizacao > original_timestamp
        assert valid_event.data_hora_atualizacao.tzinfo is not None

    def test_update_valor_to_zero_is_allowed(self, valid_event):
        """Zerar o valor de um evento deve ser permitido."""
        valid_event.update_valor(Decimal("0.00"))
        assert valid_event.valor == Decimal("0.00")

    def test_update_valor_negative_raises_via_validate(self, valid_event):
        """Valor negativo deve lançar ValueError via _validate centralizado."""
        with pytest.raises(ValueError, match="Valor do evento não pode ser negativo"):
            valid_event.update_valor(Decimal("-1.00"))

    def test_update_valor_does_not_change_numero_evento(self, valid_event):
        """update_valor não deve alterar outros campos além de valor e timestamp."""
        original_numero = valid_event.numero_evento
        valid_event.update_valor(Decimal("50.00"))
        assert valid_event.numero_evento == original_numero


class TestUpdateNumeroEvento:
    """Testa o método update_numero_evento e seus efeitos colaterais."""

    def test_update_numero_evento_changes_numero(self, valid_event):
        """Novo número deve ser persistido na entidade."""
        valid_event.update_numero_evento(9999)
        assert valid_event.numero_evento == 9999

    def test_update_numero_evento_refreshes_timestamp(self, valid_event):
        """Timestamp deve ser posterior ao original após update."""
        original_timestamp = valid_event.data_hora_atualizacao
        time.sleep(0.01)
        valid_event.update_numero_evento(9999)
        assert valid_event.data_hora_atualizacao > original_timestamp
        assert valid_event.data_hora_atualizacao.tzinfo is not None

    def test_update_numero_evento_negative_raises_via_validate(self, valid_event):
        """Número negativo deve lançar ValueError via _validate centralizado."""
        with pytest.raises(ValueError, match="Número do evento deve ser positivo"):
            valid_event.update_numero_evento(-1)

    def test_update_numero_evento_zero_raises_via_validate(self, valid_event):
        """Número zero deve lançar ValueError via _validate centralizado."""
        with pytest.raises(ValueError, match="Número do evento deve ser positivo"):
            valid_event.update_numero_evento(0)

    def test_update_numero_evento_does_not_change_valor(self, valid_event):
        """update_numero_evento não deve alterar outros campos além de numero e timestamp."""
        original_valor = valid_event.valor
        valid_event.update_numero_evento(9999)
        assert valid_event.valor == original_valor


class TestToDict:
    """Testa a serialização da entidade para dicionário."""

    def test_to_dict_contains_all_fields(self, persisted_event):
        """Dicionário deve conter todos os campos esperados."""
        result = persisted_event.to_dict()
        assert set(result.keys()) == {"id", "numero_evento", "valor", "data_hora_atualizacao"}

    def test_to_dict_id_is_none_for_new_event(self, valid_event):
        """Evento novo deve serializar id como None."""
        assert valid_event.to_dict()["id"] is None

    def test_to_dict_valor_is_float(self, valid_event):
        """Valor deve ser serializado como float."""
        result = valid_event.to_dict()
        assert isinstance(result["valor"], float)
        assert result["valor"] == 10.0

    def test_to_dict_timestamp_is_iso_string(self, valid_event):
        """Timestamp deve ser serializado como string ISO 8601."""
        result = valid_event.to_dict()
        assert isinstance(result["data_hora_atualizacao"], str)
        parsed = datetime.fromisoformat(result["data_hora_atualizacao"])
        assert parsed == valid_event.data_hora_atualizacao

    def test_to_dict_reflects_updated_valor(self, valid_event):
        """to_dict deve refletir o estado atual após update_valor."""
        valid_event.update_valor(Decimal("99.99"))
        assert valid_event.to_dict()["valor"] == 99.99

    def test_to_dict_reflects_updated_numero_evento(self, valid_event):
        """to_dict deve refletir o número atualizado."""
        valid_event.update_numero_evento(7777)
        assert valid_event.to_dict()["numero_evento"] == 7777
```

### Fim: verificar, commit, push e merge

```bash
pytest tests/unit/domain/ -v
# 23 passed ✅
```

```bash
git add .
git commit -m "feat(domain): entidade Event com validações e testes"
git push -u origin feature/parte-4-domain-entity

# Merge na develop
git checkout develop
git merge feature/parte-4-domain-entity
git push origin develop
```

---

## Parte 5 — Domain: porta do repositório

### Início: criar a branch

```bash
git checkout develop
git checkout -b feature/parte-5-domain-port
```

A porta é o contrato que qualquer repositório deve seguir. O domínio depende desta interface — não do PostgreSQL diretamente. Isso é o **D** do SOLID (Dependency Inversion).

### 5.1 `src/events_api/domain/ports/event_repository.py`

```python
"""Porta do Repositório de Eventos."""
from abc import ABC, abstractmethod
from typing import Optional

from src.events_api.domain.entities.event import Event


class EventRepositoryPort(ABC):
    """
    Contrato que qualquer implementação de repositório deve seguir.

    ABC = Abstract Base Class. Python garante que toda classe que herde
    desta implemente todos os métodos marcados com @abstractmethod.
    """

    @abstractmethod
    def save(self, event: Event) -> Event:
        """Persiste um novo evento e retorna com o ID gerado."""
        ...

    @abstractmethod
    def find_by_id(self, event_id: int) -> Optional[Event]:
        """Retorna o evento ou None se não existir."""
        ...

    @abstractmethod
    def find_by_numero_evento(self, numero_evento: int) -> Optional[Event]:
        """Retorna o evento pelo número ou None se não existir."""
        ...

    @abstractmethod
    def update(self, event: Event) -> Event:
        """Atualiza um evento existente."""
        ...

    @abstractmethod
    def delete(self, event_id: int) -> bool:
        """Remove um evento. Retorna True se deletado, False se não encontrado."""
        ...

    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> list[Event]:
        """Lista eventos com paginação."""
        ...
```

### Fim: commit, push e merge

```bash
git add .
git commit -m "feat(domain): porta EventRepositoryPort"
git push -u origin feature/parte-5-domain-port

# Merge na develop
git checkout develop
git merge feature/parte-5-domain-port
git push origin develop
```

---

## Parte 6 — Application: EventService + testes

### Início: criar a branch

```bash
git checkout develop
git checkout -b feature/parte-6-application-service
```

O serviço orquestra os casos de uso. Ele recebe o repositório via injeção de dependência e não sabe se é PostgreSQL ou um mock — só sabe que implementa `EventRepositoryPort`.

### 6.1 `src/events_api/application/services/event_service.py`

```python
"""Serviço de Eventos: Casos de Uso da Aplicação."""
from datetime import datetime, UTC
from decimal import Decimal

from src.events_api.domain.entities.event import Event
from src.events_api.domain.exceptions import (
    EventAlreadyExistsException,
    EventNotFoundException,
)
from src.events_api.domain.ports.event_repository import EventRepositoryPort


class EventService:
    """
    Casos de uso do sistema de eventos.

    Princípios SOLID aplicados:
      S — responsabilidade única: orquestra casos de uso de eventos
      D — depende da abstração EventRepositoryPort, não do PostgreSQL
    """

    def __init__(self, repository: EventRepositoryPort) -> None:
        """
        Repositório injetado — não criado aqui.
        Em produção: repositório real (PostgreSQL).
        Nos testes: repositório mock (sem banco).
        """
        self._repository = repository

    def create_event(self, numero_evento: int, valor: Decimal) -> Event:
        """Cria um novo evento. Falha se o número já existir."""
        if self._repository.find_by_numero_evento(numero_evento) is not None:
            raise EventAlreadyExistsException(numero_evento)

        event = Event(
            numero_evento=numero_evento,
            valor=valor,
            data_hora_atualizacao=datetime.now(UTC),
        )
        return self._repository.save(event)

    def update_event(
        self,
        event_id: int,
        novo_valor: Decimal | None = None,
        novo_numero_evento: int | None = None,
    ) -> Event:
        """Atualiza valor e/ou número do evento."""
        event = self._repository.find_by_id(event_id)
        if event is None:
            raise EventNotFoundException(event_id)

        if novo_valor is not None:
            event.update_valor(novo_valor)

        if novo_numero_evento is not None:
            event.update_numero_evento(novo_numero_evento)

        return self._repository.update(event)

    def delete_event(self, event_id: int) -> None:
        """Remove um evento. Falha se não existir."""
        if self._repository.find_by_id(event_id) is None:
            raise EventNotFoundException(event_id)
        self._repository.delete(event_id)

    def get_event_by_id(self, event_id: int) -> Event:
        """Busca evento por ID. Falha se não existir."""
        event = self._repository.find_by_id(event_id)
        if event is None:
            raise EventNotFoundException(event_id)
        return event

    def search_events(
        self,
        numero_evento: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Event]:
        """Lista eventos com filtro opcional por número."""
        if numero_evento is not None:
            event = self._repository.find_by_numero_evento(numero_evento)
            return [event] if event else []
        return self._repository.find_all(skip=skip, limit=limit)
```

### 6.2 `tests/unit/application/conftest.py`

```python
"""Fixtures dos testes de application."""
from datetime import datetime, UTC
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from src.events_api.application.services.event_service import EventService
from src.events_api.domain.entities.event import Event


@pytest.fixture
def mock_repository():
    """Repositório falso — aceita qualquer chamada sem conectar ao banco."""
    return MagicMock()


@pytest.fixture
def event_service(mock_repository):
    """EventService com repositório mockado injetado."""
    return EventService(repository=mock_repository)


@pytest.fixture
def sample_event() -> Event:
    """Evento de exemplo reutilizável nos testes."""
    return Event(
        id=1,
        numero_evento=2400,
        valor=Decimal("10.00"),
        data_hora_atualizacao=datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC),
    )
```

### 6.3 `tests/unit/application/test_event_service.py`

```python
"""Testes do EventService com Mock Repository."""
from decimal import Decimal
from datetime import datetime, UTC

import pytest

from src.events_api.domain.entities.event import Event
from src.events_api.domain.exceptions import (
    EventAlreadyExistsException,
    EventNotFoundException,
)


class TestCreateEvent:
    """Testa o caso de uso de criação de eventos."""

    def test_create_event_successfully(self, event_service, mock_repository, sample_event):
        """Caminho feliz: número ainda não existe, evento é criado."""
        mock_repository.find_by_numero_evento.return_value = None
        mock_repository.save.return_value = sample_event

        result = event_service.create_event(numero_evento=2400, valor=Decimal("10.00"))

        assert result.numero_evento == 2400
        mock_repository.find_by_numero_evento.assert_called_once_with(2400)
        mock_repository.save.assert_called_once()

    def test_create_raises_when_numero_already_exists(
        self, event_service, mock_repository, sample_event
    ):
        """Número duplicado deve lançar EventAlreadyExistsException."""
        mock_repository.find_by_numero_evento.return_value = sample_event

        with pytest.raises(EventAlreadyExistsException) as exc_info:
            event_service.create_event(numero_evento=2400, valor=Decimal("10.00"))

        assert "2400" in str(exc_info.value)
        mock_repository.save.assert_not_called()

    def test_create_with_invalid_numero_raises_value_error(
        self, event_service, mock_repository
    ):
        """Número inválido lança ValueError antes de chegar no repositório."""
        mock_repository.find_by_numero_evento.return_value = None

        with pytest.raises(ValueError):
            event_service.create_event(numero_evento=-1, valor=Decimal("10.00"))


class TestUpdateEvent:
    """Testa o caso de uso de atualização de eventos."""

    def test_update_valor_successfully(self, event_service, mock_repository, sample_event):
        """Atualiza valor com sucesso."""
        updated = Event(
            id=1, numero_evento=2400,
            valor=Decimal("20.00"),
            data_hora_atualizacao=datetime.now(UTC),
        )
        mock_repository.find_by_id.return_value = sample_event
        mock_repository.update.return_value = updated

        result = event_service.update_event(event_id=1, novo_valor=Decimal("20.00"))

        assert result.valor == Decimal("20.00")
        mock_repository.update.assert_called_once()

    def test_update_numero_evento_successfully(
        self, event_service, mock_repository, sample_event
    ):
        """Atualiza número do evento com sucesso."""
        updated = Event(
            id=1, numero_evento=9999,
            valor=Decimal("10.00"),
            data_hora_atualizacao=datetime.now(UTC),
        )
        mock_repository.find_by_id.return_value = sample_event
        mock_repository.update.return_value = updated

        result = event_service.update_event(event_id=1, novo_numero_evento=9999)

        assert result.numero_evento == 9999
        mock_repository.update.assert_called_once()

    def test_update_nonexistent_raises_not_found(self, event_service, mock_repository):
        """Evento inexistente deve lançar EventNotFoundException."""
        mock_repository.find_by_id.return_value = None

        with pytest.raises(EventNotFoundException) as exc_info:
            event_service.update_event(event_id=999, novo_valor=Decimal("20.00"))

        assert "999" in str(exc_info.value)
        mock_repository.update.assert_not_called()


class TestDeleteEvent:
    """Testa o caso de uso de deleção de eventos."""

    def test_delete_successfully(self, event_service, mock_repository, sample_event):
        """Deleta evento existente sem lançar exceção."""
        mock_repository.find_by_id.return_value = sample_event

        event_service.delete_event(event_id=1)

        mock_repository.delete.assert_called_once_with(1)

    def test_delete_nonexistent_raises_not_found(self, event_service, mock_repository):
        """Deletar evento inexistente deve lançar EventNotFoundException."""
        mock_repository.find_by_id.return_value = None

        with pytest.raises(EventNotFoundException):
            event_service.delete_event(event_id=999)

        mock_repository.delete.assert_not_called()


class TestSearchEvents:
    """Testa o caso de uso de pesquisa de eventos."""

    def test_search_by_numero_found(self, event_service, mock_repository, sample_event):
        """Pesquisa por número retorna lista com um elemento."""
        mock_repository.find_by_numero_evento.return_value = sample_event

        results = event_service.search_events(numero_evento=2400)

        assert len(results) == 1
        assert results[0].numero_evento == 2400

    def test_search_by_numero_not_found_returns_empty(
        self, event_service, mock_repository
    ):
        """Número inexistente retorna lista vazia."""
        mock_repository.find_by_numero_evento.return_value = None

        assert event_service.search_events(numero_evento=9999) == []

    def test_search_all_returns_paginated_list(
        self, event_service, mock_repository, sample_event
    ):
        """Pesquisa sem filtro retorna lista paginada."""
        mock_repository.find_all.return_value = [sample_event, sample_event]

        results = event_service.search_events(skip=0, limit=10)

        assert len(results) == 2
        mock_repository.find_all.assert_called_once_with(skip=0, limit=10)

    def test_search_all_empty_returns_empty_list(self, event_service, mock_repository):
        """Banco vazio retorna lista vazia."""
        mock_repository.find_all.return_value = []

        assert event_service.search_events() == []
```

### Fim: verificar, commit, push e merge

```bash
pytest tests/unit/ -v
# 23 passed (domain) + 11 passed (application) = 34 passed ✅
```

```bash
git add .
git commit -m "feat(application): EventService com casos de uso e testes"
git push -u origin feature/parte-6-application-service

# Merge na develop
git checkout develop
git merge feature/parte-6-application-service
git push origin develop
```

---

## Parte 7 — Infrastructure: settings e database

### Início: criar a branch

```bash
git checkout develop
git checkout -b feature/parte-7-infrastructure
```

### 7.1 `src/events_api/infrastructure/settings.py`

```python
"""Configurações carregadas de variáveis de ambiente."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Pydantic Settings lê automaticamente do arquivo .env ou do ambiente.
    Nunca coloque senhas no código — use variáveis de ambiente.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    database_url: str = "postgresql://postgres:postgres@localhost:5432/events_db"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"


settings = Settings()
```

### 7.2 `src/events_api/infrastructure/database.py`

```python
"""Configuração do SQLAlchemy."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.events_api.infrastructure.settings import settings


engine = create_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe base para todos os modelos SQLAlchemy."""
```

### Fim: verificar, commit, push e merge

```bash
python -c "from src.events_api.infrastructure.settings import settings; print(settings.environment)"
# development ✅
```

```bash
git add .
git commit -m "feat(infrastructure): settings e configuração do banco"
git push -u origin feature/parte-7-infrastructure

# Merge na develop
git checkout develop
git merge feature/parte-7-infrastructure
git push origin develop
```

---

## Parte 8 — Adapter outbound: model e repositório PostgreSQL

### Início: criar a branch

```bash
git checkout develop
git checkout -b feature/parte-8-adapter-outbound
```

O adaptador de saída é o único lugar que conhece SQLAlchemy. Se você quiser trocar o banco de dados, só muda este arquivo.

### 8.1 `src/events_api/adapters/outbound/persistence/models/event_model.py`

```python
"""Modelo SQLAlchemy — define a tabela 'events' no banco."""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.events_api.infrastructure.database import Base


class EventModel(Base):
    """Mapeamento da tabela events. Cada mapped_column é uma coluna."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    numero_evento: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    valor: Mapped[Decimal] = mapped_column(DECIMAL(precision=10, scale=2), nullable=False)
    data_hora_atualizacao: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"<EventModel(id={self.id}, numero_evento={self.numero_evento})>"
```

### 8.2 `src/events_api/adapters/outbound/persistence/repositories/event_repository_impl.py`

```python
"""Implementação concreta do repositório usando SQLAlchemy + PostgreSQL."""
from typing import Optional

from sqlalchemy.orm import Session

from src.events_api.adapters.outbound.persistence.models.event_model import EventModel
from src.events_api.domain.entities.event import Event
from src.events_api.domain.ports.event_repository import EventRepositoryPort


class EventRepositoryImpl(EventRepositoryPort):
    """
    Repositório PostgreSQL.

    Princípio SOLID — Liskov Substitution (L):
    pode substituir EventRepositoryPort em qualquer contexto.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: EventModel) -> Event:
        """Modelo SQLAlchemy → entidade de domínio."""
        return Event(
            id=model.id,
            numero_evento=model.numero_evento,
            valor=model.valor,
            data_hora_atualizacao=model.data_hora_atualizacao,
        )

    @staticmethod
    def _to_model(entity: Event) -> EventModel:
        """Entidade de domínio → modelo SQLAlchemy."""
        return EventModel(
            id=entity.id,
            numero_evento=entity.numero_evento,
            valor=entity.valor,
            data_hora_atualizacao=entity.data_hora_atualizacao,
        )

    def save(self, event: Event) -> Event:
        model = self._to_model(event)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, event_id: int) -> Optional[Event]:
        model = self._session.get(EventModel, event_id)
        return self._to_entity(model) if model else None

    def find_by_numero_evento(self, numero_evento: int) -> Optional[Event]:
        model = (
            self._session.query(EventModel)
            .filter(EventModel.numero_evento == numero_evento)
            .first()
        )
        return self._to_entity(model) if model else None

    def update(self, event: Event) -> Event:
        model = self._session.get(EventModel, event.id)
        model.valor = event.valor
        model.numero_evento = event.numero_evento
        model.data_hora_atualizacao = event.data_hora_atualizacao
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def delete(self, event_id: int) -> bool:
        model = self._session.get(EventModel, event_id)
        if model is None:
            return False
        self._session.delete(model)
        self._session.commit()
        return True

    def find_all(self, skip: int = 0, limit: int = 100) -> list[Event]:
        models = self._session.query(EventModel).offset(skip).limit(limit).all()
        return [self._to_entity(m) for m in models]
```

### Fim: verificar, commit, push e merge

```bash
# Testes unitários continuam passando sem banco
pytest tests/unit/ -v
# 34 passed ✅
```

```bash
git add .
git commit -m "feat(adapter): model e repositório PostgreSQL"
git push -u origin feature/parte-8-adapter-outbound

# Merge na develop
git checkout develop
git merge feature/parte-8-adapter-outbound
git push origin develop
```

---

## Parte 9 — Migrations com Alembic

### Início: criar a branch

```bash
git checkout develop
git checkout -b feature/parte-9-migrations
```

Alembic é o controle de versão do banco. Em vez de executar SQL manualmente, você cria arquivos de migration que são aplicados automaticamente — inclusive em produção durante o deploy.

### 9.1 `alembic.ini`

```ini
[alembic]
script_location = migrations
prepend_sys_path = .
sqlalchemy.url = %(DATABASE_URL)s

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### 9.2 `migrations/env.py`

```python
"""Configuração do Alembic."""
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from src.events_api.adapters.outbound.persistence.models.event_model import Base

config = context.config
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Gera SQL sem conectar ao banco — útil para revisar antes de aplicar."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica migrations conectando ao banco."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 9.3 Gerar e aplicar a migration

```bash
# Gera o arquivo de migration comparando os modelos com o banco atual
alembic revision --autogenerate -m "create_events_table"

# Aplica no banco
alembic upgrade head

# Confirma que a tabela foi criada
psql $DATABASE_URL -c "\dt"
psql $DATABASE_URL -c "\d events"
```

Comandos úteis do Alembic:

```bash
alembic current        # em qual migration o banco está
alembic history        # histórico de migrations
alembic downgrade -1   # desfaz a última migration (rollback)
```

### Fim: verificar, commit, push e merge

```bash
psql $DATABASE_URL -c "\dt"
# events ✅

pytest tests/unit/ -v
# 34 passed ✅
```

```bash
git add .
git commit -m "feat(migrations): migration inicial da tabela events"
git push -u origin feature/parte-9-migrations

# Merge na develop
git checkout develop
git merge feature/parte-9-migrations
git push origin develop
```

---

## Parte 10 — Adapter inbound: schemas, router e dependencies

### Início: criar a branch

```bash
git checkout develop
git checkout -b feature/parte-10-adapter-inbound
```

O adaptador de entrada recebe requisições HTTP e as converte em chamadas para o `EventService`. É a única camada que conhece FastAPI e status codes HTTP.

### 10.1 `src/events_api/infrastructure/dependencies.py`

```python
"""Injeção de Dependências do FastAPI."""
from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from src.events_api.adapters.outbound.persistence.repositories.event_repository_impl import (
    EventRepositoryImpl,
)
from src.events_api.application.services.event_service import EventService
from src.events_api.infrastructure.database import SessionLocal


def get_db_session() -> Generator[Session, None, None]:
    """
    Abre uma sessão por request e garante que seja fechada ao final.
    O FastAPI executa até o yield, injeta a sessão no handler,
    e executa o finally após a resposta — mesmo em caso de erro.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_event_service(db: Session = Depends(get_db_session)) -> EventService:
    """Monta o EventService com o repositório PostgreSQL."""
    return EventService(repository=EventRepositoryImpl(session=db))
```

### 10.2 `src/events_api/adapters/inbound/http/schemas/event_schemas.py`

```python
"""Schemas Pydantic para validação de entrada e saída da API."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class EventCreateRequest(BaseModel):
    """Schema de entrada para criação de evento."""

    numero_evento: int = Field(..., gt=0, description="Número único do evento", examples=[2400])
    valor: Decimal = Field(..., ge=0, decimal_places=2, description="Valor em reais", examples=["10.00"])

    @field_validator("valor")
    @classmethod
    def validate_valor(cls, v: Decimal) -> Decimal:
        return round(v, 2)


class EventUpdateRequest(BaseModel):
    """Schema de entrada para atualização — valor e/ou número são opcionais."""

    valor: Decimal | None = Field(default=None, ge=0, description="Novo valor")
    numero_evento: int | None = Field(default=None, gt=0, description="Novo número do evento")


class EventResponse(BaseModel):
    """Schema de saída do evento."""

    id: int
    numero_evento: int
    valor: Decimal
    data_hora_atualizacao: datetime

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    """Schema de resposta de erro padronizado."""

    detail: str
    error_type: str
```

### 10.3 `src/events_api/adapters/inbound/http/routers/event_router.py`

```python
"""Router HTTP de Eventos."""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.events_api.adapters.inbound.http.schemas.event_schemas import (
    ErrorResponse,
    EventCreateRequest,
    EventResponse,
    EventUpdateRequest,
)
from src.events_api.application.services.event_service import EventService
from src.events_api.domain.exceptions import (
    EventAlreadyExistsException,
    EventNotFoundException,
)
from src.events_api.infrastructure.dependencies import get_event_service

router = APIRouter(
    prefix="/events",
    tags=["Eventos"],
    responses={404: {"model": ErrorResponse}},
)


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED,
             summary="Inserir um evento")
def create_event(
    request: EventCreateRequest,
    service: EventService = Depends(get_event_service),
) -> EventResponse:
    """Cria um novo evento. O timestamp é gerado automaticamente."""
    try:
        event = service.create_event(numero_evento=request.numero_evento, valor=request.valor)
        return EventResponse.model_validate(event.to_dict())
    except EventAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.put("/{event_id}", response_model=EventResponse, summary="Atualizar um evento")
def update_event(
    event_id: int,
    request: EventUpdateRequest,
    service: EventService = Depends(get_event_service),
) -> EventResponse:
    """Atualiza valor e/ou número. O timestamp é atualizado automaticamente."""
    try:
        event = service.update_event(
            event_id=event_id,
            novo_valor=request.valor,
            novo_numero_evento=request.numero_evento,
        )
        return EventResponse.model_validate(event.to_dict())
    except EventNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Deletar um evento")
def delete_event(
    event_id: int,
    service: EventService = Depends(get_event_service),
) -> None:
    """Remove permanentemente um evento pelo ID."""
    try:
        service.delete_event(event_id)
    except EventNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=list[EventResponse], summary="Pesquisar eventos")
def search_events(
    numero_evento: int | None = Query(default=None, gt=0, description="Filtrar por número"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    service: EventService = Depends(get_event_service),
) -> list[EventResponse]:
    """Lista eventos com filtro opcional por número e paginação."""
    events = service.search_events(numero_evento=numero_evento, skip=skip, limit=limit)
    return [EventResponse.model_validate(e.to_dict()) for e in events]


@router.get("/{event_id}", response_model=EventResponse, summary="Buscar evento por ID")
def get_event(
    event_id: int,
    service: EventService = Depends(get_event_service),
) -> EventResponse:
    """Busca um evento pelo ID."""
    try:
        event = service.get_event_by_id(event_id)
        return EventResponse.model_validate(event.to_dict())
    except EventNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
```

### 10.4 `src/events_api/main.py`

```python
"""Ponto de entrada da aplicação FastAPI."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.events_api.adapters.inbound.http.routers.event_router import router as event_router
from src.events_api.domain.exceptions import DomainException
from src.events_api.infrastructure.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida: código antes do yield roda na inicialização."""
    print(f"🚀 Events API | ambiente: {settings.environment}")
    yield
    print("👋 Events API encerrando...")


app = FastAPI(
    title="Events API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """Converte exceções de domínio em respostas HTTP padronizadas."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "error_type": type(exc).__name__},
    )


app.include_router(event_router, prefix=settings.api_prefix)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check para load balancers."""
    return {"status": "healthy", "environment": settings.environment}
```

### Fim: verificar, commit, push e merge

```bash
uvicorn src.events_api.main:app --reload --host 0.0.0.0 --port 8000

curl -s http://localhost:8000/health
# {"status":"healthy","environment":"development"} ✅
```

```bash
git add .
git commit -m "feat(adapter): schemas, router HTTP e dependencies"
git push -u origin feature/parte-10-adapter-inbound

# Merge na develop
git checkout develop
git merge feature/parte-10-adapter-inbound
git push origin develop
```

---

## Parte 11 — Testes de integração

### Início: criar a branch

```bash
git checkout develop
git checkout -b feature/parte-11-integration-tests
```

Testam os endpoints HTTP de ponta a ponta, mas sem banco de dados real — usando um repositório em memória. Isso é possível graças à arquitetura hexagonal: o `TestClient` recebe o mesmo serviço com um repositório diferente.

### 11.1 `tests/integration/conftest.py`

```python
"""Fixtures dos testes de integração."""
import pytest
from fastapi.testclient import TestClient

from src.events_api.application.services.event_service import EventService
from src.events_api.infrastructure.dependencies import get_event_service
from src.events_api.main import app


class InMemoryEventRepository:
    """
    Repositório em memória para testes de integração.
    Implementa o mesmo contrato (EventRepositoryPort) sem tocar no banco.
    """

    def __init__(self):
        self._events: dict = {}
        self._next_id = 1

    def save(self, event):
        event.id = self._next_id
        self._events[self._next_id] = event
        self._next_id += 1
        return event

    def find_by_id(self, event_id):
        return self._events.get(event_id)

    def find_by_numero_evento(self, numero_evento):
        return next(
            (e for e in self._events.values() if e.numero_evento == numero_evento), None
        )

    def update(self, event):
        self._events[event.id] = event
        return event

    def delete(self, event_id):
        if event_id in self._events:
            del self._events[event_id]
            return True
        return False

    def find_all(self, skip=0, limit=100):
        events = list(self._events.values())
        return events[skip: skip + limit]


@pytest.fixture
def test_client():
    """TestClient com repositório em memória — sem banco de dados."""
    repo = InMemoryEventRepository()
    service = EventService(repository=repo)
    app.dependency_overrides[get_event_service] = lambda: service
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
```

### 11.2 `tests/integration/test_event_api.py`

```python
"""Testes de integração dos endpoints HTTP."""


class TestCreateEventEndpoint:
    """Testa o endpoint POST /events/."""

    def test_post_creates_event_and_returns_201(self, test_client):
        """Criação bem-sucedida retorna 201 com o evento."""
        response = test_client.post(
            "/api/v1/events/",
            json={"numero_evento": 2400, "valor": "10.00"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["numero_evento"] == 2400
        assert data["id"] is not None
        assert "data_hora_atualizacao" in data

    def test_post_duplicate_numero_returns_409(self, test_client):
        """Número duplicado retorna 409 Conflict."""
        test_client.post("/api/v1/events/", json={"numero_evento": 2400, "valor": "10.00"})
        response = test_client.post("/api/v1/events/", json={"numero_evento": 2400, "valor": "5.00"})
        assert response.status_code == 409

    def test_post_invalid_numero_returns_422(self, test_client):
        """Número inválido retorna 422 Unprocessable Entity."""
        response = test_client.post("/api/v1/events/", json={"numero_evento": -1, "valor": "10.00"})
        assert response.status_code == 422

    def test_post_negative_valor_returns_422(self, test_client):
        """Valor negativo retorna 422."""
        response = test_client.post("/api/v1/events/", json={"numero_evento": 1, "valor": "-5.00"})
        assert response.status_code == 422


class TestUpdateEventEndpoint:
    """Testa o endpoint PUT /events/{id}."""

    def test_put_updates_valor_and_returns_200(self, test_client):
        """Atualização de valor retorna 200 com o evento atualizado."""
        create = test_client.post("/api/v1/events/", json={"numero_evento": 2400, "valor": "10.00"})
        event_id = create.json()["id"]

        response = test_client.put(f"/api/v1/events/{event_id}", json={"valor": "20.00"})

        assert response.status_code == 200
        assert response.json()["valor"] == "20.00"

    def test_put_updates_numero_evento(self, test_client):
        """Atualização de número retorna 200."""
        create = test_client.post("/api/v1/events/", json={"numero_evento": 2400, "valor": "10.00"})
        event_id = create.json()["id"]

        response = test_client.put(f"/api/v1/events/{event_id}", json={"numero_evento": 9999})

        assert response.status_code == 200
        assert response.json()["numero_evento"] == 9999

    def test_put_nonexistent_returns_404(self, test_client):
        """Evento inexistente retorna 404."""
        response = test_client.put("/api/v1/events/9999", json={"valor": "20.00"})
        assert response.status_code == 404


class TestDeleteEventEndpoint:
    """Testa o endpoint DELETE /events/{id}."""

    def test_delete_returns_204(self, test_client):
        """Deleção bem-sucedida retorna 204 sem body."""
        create = test_client.post("/api/v1/events/", json={"numero_evento": 2400, "valor": "10.00"})
        event_id = create.json()["id"]

        assert test_client.delete(f"/api/v1/events/{event_id}").status_code == 204

    def test_delete_nonexistent_returns_404(self, test_client):
        """Evento inexistente retorna 404."""
        assert test_client.delete("/api/v1/events/9999").status_code == 404

    def test_get_after_delete_returns_404(self, test_client):
        """Buscar evento deletado retorna 404."""
        create = test_client.post("/api/v1/events/", json={"numero_evento": 2400, "valor": "10.00"})
        event_id = create.json()["id"]
        test_client.delete(f"/api/v1/events/{event_id}")

        assert test_client.get(f"/api/v1/events/{event_id}").status_code == 404


class TestSearchEventsEndpoint:
    """Testa o endpoint GET /events/."""

    def test_get_all_returns_empty_initially(self, test_client):
        """Lista vazia quando não há eventos."""
        assert test_client.get("/api/v1/events/").json() == []

    def test_get_all_returns_created_events(self, test_client):
        """Lista retorna todos os eventos criados."""
        test_client.post("/api/v1/events/", json={"numero_evento": 2400, "valor": "10.00"})
        test_client.post("/api/v1/events/", json={"numero_evento": 2401, "valor": "20.00"})

        assert len(test_client.get("/api/v1/events/").json()) == 2

    def test_search_by_numero_returns_matching(self, test_client):
        """Filtro por número retorna só o evento correspondente."""
        test_client.post("/api/v1/events/", json={"numero_evento": 2400, "valor": "10.00"})
        test_client.post("/api/v1/events/", json={"numero_evento": 2401, "valor": "20.00"})

        results = test_client.get("/api/v1/events/?numero_evento=2400").json()
        assert len(results) == 1
        assert results[0]["numero_evento"] == 2400

    def test_search_nonexistent_numero_returns_empty(self, test_client):
        """Número inexistente retorna lista vazia."""
        assert test_client.get("/api/v1/events/?numero_evento=9999").json() == []
```

### Fim: verificar, commit, push e merge

```bash
pytest tests/ -v
# 34 passed (unit) + 13 passed (integration) = 47 passed ✅

pytest tests/ --cov=src --cov-report=term-missing
# TOTAL > 90% ✅
```

```bash
git add .
git commit -m "test(integration): testes dos endpoints HTTP com repositório em memória"
git push -u origin feature/parte-11-integration-tests

# Merge na develop
git checkout develop
git merge feature/parte-11-integration-tests
git push origin develop
```

---

## Verificação final

```bash
# Todos os testes
pytest tests/ -v --tb=short

# API rodando
uvicorn src.events_api.main:app --reload --host 0.0.0.0 --port 8000

# Testar manualmente
curl -s -X POST http://localhost:8000/api/v1/events/ \
  -H "Content-Type: application/json" \
  -d '{"numero_evento": 2400, "valor": "10.00"}' | python3 -m json.tool

curl -s -X PUT http://localhost:8000/api/v1/events/1 \
  -H "Content-Type: application/json" \
  -d '{"valor": "15.50"}' | python3 -m json.tool

curl -s "http://localhost:8000/api/v1/events/?numero_evento=2400" | python3 -m json.tool

curl -s -X DELETE http://localhost:8000/api/v1/events/1

# Confirmar no banco
psql $DATABASE_URL -c "SELECT * FROM events;"
```

Documentação interativa: **http://localhost:8000/api/v1/docs**

---

## Histórico de branches e commits

```
main
 └── develop
      ├── feature/parte-1-estrutura-base         → chore: estrutura base do projeto
      ├── feature/parte-2-devcontainer           → chore: devcontainer, docker e dependências
      ├── feature/parte-3-domain-excecoes        → feat(domain): exceções de domínio
      ├── feature/parte-4-domain-entity          → feat(domain): entidade Event com validações e testes
      ├── feature/parte-5-domain-port            → feat(domain): porta EventRepositoryPort
      ├── feature/parte-6-application-service    → feat(application): EventService com casos de uso e testes
      ├── feature/parte-7-infrastructure         → feat(infrastructure): settings e configuração do banco
      ├── feature/parte-8-adapter-outbound       → feat(adapter): model e repositório PostgreSQL
      ├── feature/parte-9-migrations             → feat(migrations): migration inicial da tabela events
      ├── feature/parte-10-adapter-inbound       → feat(adapter): schemas, router HTTP e dependencies
      └── feature/parte-11-integration-tests     → test(integration): testes dos endpoints HTTP
```

---

## Referência rápida

| Comando | O que faz |
|---------|-----------|
| `pytest tests/unit/domain/ -v` | Testa só o domínio |
| `pytest tests/unit/ -v` | Testa domínio + application |
| `pytest tests/ -v` | Testa tudo |
| `pytest tests/ --cov=src --cov-report=html` | Relatório de cobertura |
| `alembic revision --autogenerate -m "desc"` | Cria migration |
| `alembic upgrade head` | Aplica migrations pendentes |
| `alembic downgrade -1` | Desfaz a última migration |
| `uvicorn src.events_api.main:app --reload` | Inicia a API |
| `psql $DATABASE_URL` | Abre o banco no terminal |
