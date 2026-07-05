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