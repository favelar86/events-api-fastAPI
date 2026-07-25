class TestCreateEventEndpoint:
    """Testa o endpoint POST /events/."""

    def test_post_creates_event_and_returns_201(self, test_client):
        """Criação bem-sucedida retorna 201 com o evento."""
        response = test_client.post(
            "/api/v1/events/",
            json={"numero_evento": 2400, "valor": "10.00"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["numero_evento"] == 2400
        assert data["id"] is not None
        assert "data_hora_atualizacao" in data

    def test_post_duplicate_numero_returns_409(self, test_client):
        """Número duplicado retorna 409 Conflict."""
        test_client.post(
            "/api/v1/events/", json={"numero_evento": 2400, "valor": "10.00"}
        )
        response = test_client.post(
            "/api/v1/events/", json={"numero_evento": 2400, "valor": "5.00"}
        )
        assert response.status_code == 409

    def test_post_invalid_numero_returns_422(self, test_client):
        """Número inválido retorna 422 Unprocessable Entity."""
        response = test_client.post(
            "/api/v1/events/", json={"numero_evento": -1, "valor": "10.00"}
        )
        assert response.status_code == 422

    def test_post_negative_valor_returns_422(self, test_client):
        """Valor negativo retorna 422."""
        response = test_client.post(
            "/api/v1/events/", json={"numero_evento": 1, "valor": "-5.00"}
        )
        assert response.status_code == 422


class TestUpdateEventEndpoint:
    """Testa o endpoint PUT /events/{id}."""

    def test_put_updates_valor_and_returns_200(self, test_client):
        """Atualização de valor retorna 200 com o evento atualizado."""
        create = test_client.post(
            "/api/v1/events/", json={"numero_evento": 2400, "valor": "10.00"}
        )
        event_id = create.json()["id"]

        response = test_client.put(
            f"/api/v1/events/{event_id}", json={"valor": "20.00"}
        )

        assert response.status_code == 200
        assert float(response.json()["valor"]) == 20.00

    def test_put_updates_numero_evento(self, test_client):
        """Atualização de número retorna 200."""
        create = test_client.post(
            "/api/v1/events/", json={"numero_evento": 2400, "valor": "10.00"}
        )
        event_id = create.json()["id"]

        response = test_client.put(
            f"/api/v1/events/{event_id}", json={"numero_evento": 9999}
        )

        assert response.status_code == 200
        assert response.json()["numero_evento"] == 9999

    def test_put_nonexistent_returns_404(self, test_client):
        """Evento inexistente retorna 404."""
        response = test_client.put("/api/v1/events/9999", json={"valor": "20.00"})
        assert response.status_code == 404


class TestDeleteEventEndpoint:
    """Testa o endpoint DELETE /events/{id}."""

    def test_delete_returns_204(self, test_client):
        """Deleção bem-sucedida retorna 204 sem body."""
        create = test_client.post(
            "/api/v1/events/", json={"numero_evento": 2400, "valor": "10.00"}
        )
        event_id = create.json()["id"]

        assert test_client.delete(f"/api/v1/events/{event_id}").status_code == 204

    def test_delete_nonexistent_returns_404(self, test_client):
        """Evento inexistente retorna 404."""
        assert test_client.delete("/api/v1/events/9999").status_code == 404

    def test_get_after_delete_returns_404(self, test_client):
        """Buscar evento deletado retorna 404."""
        create = test_client.post(
            "/api/v1/events/", json={"numero_evento": 2400, "valor": "10.00"}
        )
        event_id = create.json()["id"]
        test_client.delete(f"/api/v1/events/{event_id}")

        assert test_client.get(f"/api/v1/events/{event_id}").status_code == 404


class TestSearchEventsEndpoint:
    """Testa o endpoint GET /events/."""

    def test_get_all_returns_empty_initially(self, test_client):
        """Lista vazia quando não há eventos."""
        assert test_client.get("/api/v1/events/").json() == []

    def test_get_all_returns_created_events(self, test_client):
        """Lista retorna todos os eventos criados."""
        test_client.post(
            "/api/v1/events/", json={"numero_evento": 2400, "valor": "10.00"}
        )
        test_client.post(
            "/api/v1/events/", json={"numero_evento": 2401, "valor": "20.00"}
        )

        assert len(test_client.get("/api/v1/events/").json()) == 2

    def test_search_by_numero_returns_matching(self, test_client):
        """Filtro por número retorna só o evento correspondente."""
        test_client.post(
            "/api/v1/events/", json={"numero_evento": 2400, "valor": "10.00"}
        )
        test_client.post(
            "/api/v1/events/", json={"numero_evento": 2401, "valor": "20.00"}
        )

        results = test_client.get("/api/v1/events/?numero_evento=2400").json()
        assert len(results) == 1
        assert results[0]["numero_evento"] == 2400

    def test_search_nonexistent_numero_returns_empty(self, test_client):
        """Número inexistente retorna lista vazia."""
        assert test_client.get("/api/v1/events/?numero_evento=9999").json() == []
