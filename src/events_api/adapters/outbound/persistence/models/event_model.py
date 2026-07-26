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