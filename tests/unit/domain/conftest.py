from decimal import Decimal

import pytest

from src.events_api.domain.entities.event import Event


@pytest.fixture
def valid_event() -> Event:
    """Nova instância criada para cada teste — sem compartilhamento de estado."""
    return Event(
        numero_evento=2400,
        valor=Decimal("10.00"),
    )


@pytest.fixture
def persisted_event() -> Event:
    """Evento que simula já ter sido salvo no banco (tem ID)."""
    return Event(
        id=1,
        numero_evento=2400,
        valor=Decimal("10.00"),
    )