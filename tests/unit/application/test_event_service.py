from decimal import Decimal

import pytest

from src.events_api.domain.entities.event import Event
from src.events_api.domain.exceptions import (
    EventAlreadyExistsException,
    EventNotFoundException,
)


class TestCreateEvent:
    """Testa o caso de uso de criação de eventos."""

    def test_create_event_successfully(self, event_service, mock_repository, sample_event):
        """Caminho feliz: número ainda não existe, evento é criado."""
        mock_repository.find_by_numero_evento.return_value = None
        mock_repository.save.return_value = sample_event

        result = event_service.create_event(numero_evento=2400, valor=Decimal("10.00"))

        assert result.numero_evento == 2400
        mock_repository.find_by_numero_evento.assert_called_once_with(2400)
        mock_repository.save.assert_called_once()

    def test_create_raises_when_numero_already_exists(
        self, event_service, mock_repository, sample_event
    ):
        """Número duplicado deve lançar EventAlreadyExistsException."""
        mock_repository.find_by_numero_evento.return_value = sample_event

        with pytest.raises(EventAlreadyExistsException) as exc_info:
            event_service.create_event(numero_evento=2400, valor=Decimal("10.00"))

        assert "2400" in str(exc_info.value)
        mock_repository.save.assert_not_called()

    def test_create_with_invalid_numero_raises_value_error(
        self, event_service, mock_repository
    ):
        """Número inválido lança ValueError antes de chegar no repositório."""
        mock_repository.find_by_numero_evento.return_value = None

        with pytest.raises(ValueError):
            event_service.create_event(numero_evento=-1, valor=Decimal("10.00"))


class TestUpdateEvent:
    """Testa o caso de uso de atualização de eventos."""

    def test_update_valor_successfully(self, event_service, mock_repository, sample_event):
        """Atualiza valor com sucesso."""
        updated = Event(
            id=1, numero_evento=2400,
            valor=Decimal("20.00"),
        )
        mock_repository.find_by_id.return_value = sample_event
        mock_repository.update.return_value = updated

        result = event_service.update_event(event_id=1, novo_valor=Decimal("20.00"))

        assert result.valor == Decimal("20.00")
        mock_repository.update.assert_called_once()

    def test_update_numero_evento_successfully(
        self, event_service, mock_repository, sample_event
    ):
        """Atualiza número do evento com sucesso."""
        updated = Event(
            id=1, numero_evento=9999,
            valor=Decimal("10.00"),
        )
        mock_repository.find_by_id.return_value = sample_event
        mock_repository.update.return_value = updated

        result = event_service.update_event(event_id=1, novo_numero_evento=9999)

        assert result.numero_evento == 9999
        mock_repository.update.assert_called_once()

    def test_update_nonexistent_raises_not_found(self, event_service, mock_repository):
        """Evento inexistente deve lançar EventNotFoundException."""
        mock_repository.find_by_id.return_value = None

        with pytest.raises(EventNotFoundException) as exc_info:
            event_service.update_event(event_id=999, novo_valor=Decimal("20.00"))

        assert "999" in str(exc_info.value)
        mock_repository.update.assert_not_called()


class TestDeleteEvent:
    """Testa o caso de uso de deleção de eventos."""

    def test_delete_successfully(self, event_service, mock_repository, sample_event):
        """Deleta evento existente sem lançar exceção."""
        mock_repository.find_by_id.return_value = sample_event

        event_service.delete_event(event_id=1)

        mock_repository.delete.assert_called_once_with(1)

    def test_delete_nonexistent_raises_not_found(self, event_service, mock_repository):
        """Deletar evento inexistente deve lançar EventNotFoundException."""
        mock_repository.find_by_id.return_value = None

        with pytest.raises(EventNotFoundException):
            event_service.delete_event(event_id=999)

        mock_repository.delete.assert_not_called()


class TestSearchEvents:
    """Testa o caso de uso de pesquisa de eventos."""

    def test_search_by_numero_found(self, event_service, mock_repository, sample_event):
        """Pesquisa por número retorna lista com um elemento."""
        mock_repository.find_by_numero_evento.return_value = sample_event

        results = event_service.search_events(numero_evento=2400)

        assert len(results) == 1
        assert results[0].numero_evento == 2400

    def test_search_by_numero_not_found_returns_empty(
        self, event_service, mock_repository
    ):
        """Número inexistente retorna lista vazia."""
        mock_repository.find_by_numero_evento.return_value = None

        assert event_service.search_events(numero_evento=9999) == []

    def test_search_all_returns_paginated_list(
        self, event_service, mock_repository, sample_event
    ):
        """Pesquisa sem filtro retorna lista paginada."""
        mock_repository.find_all.return_value = [sample_event, sample_event]

        results = event_service.search_events(skip=0, limit=10)

        assert len(results) == 2
        mock_repository.find_all.assert_called_once_with(skip=0, limit=10)

    def test_search_all_empty_returns_empty_list(self, event_service, mock_repository):
        """Banco vazio retorna lista vazia."""
        mock_repository.find_all.return_value = []

        assert event_service.search_events() == []