"""Exceções do Domínio."""


class DomainException(Exception):
    """Exceção base — todas as outras herdam desta."""


class EventNotFoundException(DomainException):
    """Lançada quando um evento não é encontrado."""

    def __init__(self, identifier: int | str) -> None:
        self.identifier = identifier
        super().__init__(f"Evento não encontrado: {identifier}")


class EventAlreadyExistsException(DomainException):
    """Lançada ao tentar criar um evento com número já existente."""

    def __init__(self, numero_evento: int) -> None:
        self.numero_evento = numero_evento
        super().__init__(f"Evento com número {numero_evento} já existe")