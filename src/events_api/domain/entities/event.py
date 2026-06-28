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
    id: int | None = field(default=None)
    data_hora_atualizacao: datetime = field(default_factory=lambda: datetime.now(UTC))

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
