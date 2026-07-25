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