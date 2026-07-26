from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.events_api.adapters.inbound.http.schemas.event_schemas import (
    ErrorResponse,
    EventCreateRequest,
    EventResponse,
    EventUpdateRequest,
)
from src.events_api.application.services.event_service import EventService
from src.events_api.domain.exceptions import (
    EventAlreadyExistsException,
    EventNotFoundException,
)
from src.events_api.infrastructure.dependencies import get_event_service

router = APIRouter(
    prefix="/events",
    tags=["Eventos"],
    responses={404: {"model": ErrorResponse}},
)


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED,
             summary="Inserir um evento")
def create_event(
    request: EventCreateRequest,
    service: EventService = Depends(get_event_service),
) -> EventResponse:
    """Cria um novo evento. O timestamp é gerado automaticamente."""
    try:
        event = service.create_event(numero_evento=request.numero_evento, valor=request.valor)
        return EventResponse.model_validate(event.to_dict())
    except EventAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.put("/{event_id}", response_model=EventResponse, summary="Atualizar um evento")
def update_event(
    event_id: int,
    request: EventUpdateRequest,
    service: EventService = Depends(get_event_service),
) -> EventResponse:
    """Atualiza valor e/ou número. O timestamp é atualizado automaticamente."""
    try:
        event = service.update_event(
            event_id=event_id,
            novo_valor=request.valor,
            novo_numero_evento=request.numero_evento,
        )
        return EventResponse.model_validate(event.to_dict())
    except EventNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Deletar um evento")
def delete_event(
    event_id: int,
    service: EventService = Depends(get_event_service),
) -> None:
    """Remove permanentemente um evento pelo ID."""
    try:
        service.delete_event(event_id)
    except EventNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=list[EventResponse], summary="Pesquisar eventos")
def search_events(
    numero_evento: int | None = Query(default=None, gt=0, description="Filtrar por número"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    service: EventService = Depends(get_event_service),
) -> list[EventResponse]:
    """Lista eventos com filtro opcional por número e paginação."""
    events = service.search_events(numero_evento=numero_evento, skip=skip, limit=limit)
    return [EventResponse.model_validate(e.to_dict()) for e in events]


@router.get("/{event_id}", response_model=EventResponse, summary="Buscar evento por ID")
def get_event(
    event_id: int,
    service: EventService = Depends(get_event_service),
) -> EventResponse:
    """Busca um evento pelo ID."""
    try:
        event = service.get_event_by_id(event_id)
        return EventResponse.model_validate(event.to_dict())
    except EventNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))