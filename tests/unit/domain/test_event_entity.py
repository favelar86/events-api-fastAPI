from datetime import datetime, UTC
from decimal import Decimal
import time

import pytest

from src.events_api.domain.entities.event import Event


class TestEventCreation:
    """Testa a criação de eventos com dados válidos e inválidos."""

    def test_create_valid_event(self):
        """Criação com dados válidos deve funcionar sem erros."""
        event = Event(
            numero_evento=2400,
            valor=Decimal("10.00"),
        )
        assert event.numero_evento == 2400
        assert event.valor == Decimal("10.00")
        assert event.id is None

    def test_create_event_timestamp_is_set_automatically(self):
        """Timestamp deve ser gerado automaticamente pela entidade."""
        before = datetime.now(UTC)
        event = Event(numero_evento=2400, valor=Decimal("10.00"))
        after = datetime.now(UTC)
        assert before <= event.data_hora_atualizacao <= after

    def test_create_event_with_id(self, persisted_event):
        """Evento com ID representa um registro já existente no banco."""
        assert persisted_event.id == 1

    def test_create_event_with_zero_valor_is_allowed(self):
        """Valor zero é permitido."""
        event = Event(
            numero_evento=1,
            valor=Decimal("0.00"),
        )
        assert event.valor == Decimal("0.00")

    def test_create_event_with_large_valor(self):
        """Valores grandes devem ser aceitos."""
        event = Event(
            numero_evento=1,
            valor=Decimal("999999.99"),
        )
        assert event.valor == Decimal("999999.99")


class TestEventValidation:
    """Testa o _validate como ponto único de validação de regras de negócio."""

    def test_negative_numero_raises_on_creation(self):
        """Número negativo deve falhar na criação via __post_init__."""
        with pytest.raises(ValueError, match="Número do evento deve ser positivo"):
            Event(numero_evento=-1, valor=Decimal("10.00"))

    def test_zero_numero_raises_on_creation(self):
        """Número zero não é permitido."""
        with pytest.raises(ValueError, match="Número do evento deve ser positivo"):
            Event(numero_evento=0, valor=Decimal("10.00"))

    def test_negative_valor_raises_on_creation(self):
        """Valor negativo deve falhar na criação."""
        with pytest.raises(ValueError, match="Valor do evento não pode ser negativo"):
            Event(numero_evento=2400, valor=Decimal("-0.01"))


class TestUpdateValor:
    """Testa o método update_valor e seus efeitos colaterais."""

    def test_update_valor_changes_value(self, valid_event):
        """Novo valor deve ser persistido na entidade."""
        valid_event.update_valor(Decimal("20.00"))
        assert valid_event.valor == Decimal("20.00")

    def test_update_valor_refreshes_timestamp(self, valid_event):
        """Timestamp deve ser posterior ao original após update."""
        original_timestamp = valid_event.data_hora_atualizacao
        time.sleep(0.01)
        valid_event.update_valor(Decimal("20.00"))
        assert valid_event.data_hora_atualizacao > original_timestamp
        assert valid_event.data_hora_atualizacao.tzinfo is not None

    def test_update_valor_to_zero_is_allowed(self, valid_event):
        """Zerar o valor de um evento deve ser permitido."""
        valid_event.update_valor(Decimal("0.00"))
        assert valid_event.valor == Decimal("0.00")

    def test_update_valor_negative_raises_via_validate(self, valid_event):
        """Valor negativo deve lançar ValueError via _validate centralizado."""
        with pytest.raises(ValueError, match="Valor do evento não pode ser negativo"):
            valid_event.update_valor(Decimal("-1.00"))

    def test_update_valor_does_not_change_numero_evento(self, valid_event):
        """update_valor não deve alterar outros campos além de valor e timestamp."""
        original_numero = valid_event.numero_evento
        valid_event.update_valor(Decimal("50.00"))
        assert valid_event.numero_evento == original_numero


class TestUpdateNumeroEvento:
    """Testa o método update_numero_evento e seus efeitos colaterais."""

    def test_update_numero_evento_changes_numero(self, valid_event):
        """Novo número deve ser persistido na entidade."""
        valid_event.update_numero_evento(9999)
        assert valid_event.numero_evento == 9999

    def test_update_numero_evento_refreshes_timestamp(self, valid_event):
        """Timestamp deve ser posterior ao original após update."""
        original_timestamp = valid_event.data_hora_atualizacao
        time.sleep(0.01)
        valid_event.update_numero_evento(9999)
        assert valid_event.data_hora_atualizacao > original_timestamp
        assert valid_event.data_hora_atualizacao.tzinfo is not None

    def test_update_numero_evento_negative_raises_via_validate(self, valid_event):
        """Número negativo deve lançar ValueError via _validate centralizado."""
        with pytest.raises(ValueError, match="Número do evento deve ser positivo"):
            valid_event.update_numero_evento(-1)

    def test_update_numero_evento_zero_raises_via_validate(self, valid_event):
        """Número zero deve lançar ValueError via _validate centralizado."""
        with pytest.raises(ValueError, match="Número do evento deve ser positivo"):
            valid_event.update_numero_evento(0)

    def test_update_numero_evento_does_not_change_valor(self, valid_event):
        """update_numero_evento não deve alterar outros campos além de numero e timestamp."""
        original_valor = valid_event.valor
        valid_event.update_numero_evento(9999)
        assert valid_event.valor == original_valor


class TestToDict:
    """Testa a serialização da entidade para dicionário."""

    def test_to_dict_contains_all_fields(self, persisted_event):
        """Dicionário deve conter todos os campos esperados."""
        result = persisted_event.to_dict()
        assert set(result.keys()) == {"id", "numero_evento", "valor", "data_hora_atualizacao"}

    def test_to_dict_id_is_none_for_new_event(self, valid_event):
        """Evento novo deve serializar id como None."""
        assert valid_event.to_dict()["id"] is None

    def test_to_dict_valor_is_float(self, valid_event):
        """Valor deve ser serializado como float."""
        result = valid_event.to_dict()
        assert isinstance(result["valor"], float)
        assert result["valor"] == 10.0

    def test_to_dict_timestamp_is_iso_string(self, valid_event):
        """Timestamp deve ser serializado como string ISO 8601."""
        result = valid_event.to_dict()
        assert isinstance(result["data_hora_atualizacao"], str)
        parsed = datetime.fromisoformat(result["data_hora_atualizacao"])
        assert parsed == valid_event.data_hora_atualizacao

    def test_to_dict_reflects_updated_valor(self, valid_event):
        """to_dict deve refletir o estado atual após update_valor."""
        valid_event.update_valor(Decimal("99.99"))
        assert valid_event.to_dict()["valor"] == 99.99

    def test_to_dict_reflects_updated_numero_evento(self, valid_event):
        """to_dict deve refletir o número atualizado."""
        valid_event.update_numero_evento(7777)
        assert valid_event.to_dict()["numero_evento"] == 7777