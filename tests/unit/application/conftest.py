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
    )