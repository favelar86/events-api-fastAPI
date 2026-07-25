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