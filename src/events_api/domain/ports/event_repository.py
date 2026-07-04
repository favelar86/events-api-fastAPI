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