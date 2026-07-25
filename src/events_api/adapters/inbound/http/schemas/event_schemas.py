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