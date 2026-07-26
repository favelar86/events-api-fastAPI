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
        """Modelo SQLAlchemy → entidade de domínio.
        O timestamp vem do banco — sobrescrevemos o gerado automaticamente pela entidade.
        """
        event = Event(
            id=model.id,
            numero_evento=model.numero_evento,
            valor=model.valor,
        )
        event.data_hora_atualizacao = model.data_hora_atualizacao
        return event

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