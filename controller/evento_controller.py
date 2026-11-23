from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schema.evento_schema import EventoCreate, EventoUpdate, EventoResponse
from security.security import get_usuario_atual, verificar_admin
from service import evento_service

router = APIRouter(prefix="/eventos", tags=["Eventos"])

# Cadastrar, atualizar e excluir: somente administrador
@router.post("", response_model=EventoResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verificar_admin)])
def criar_evento(evento: EventoCreate, db: Session = Depends(get_db)):
    return evento_service.criar_evento(db, evento)

# Consultar: qualquer usuário autenticado
@router.get("", response_model=List[EventoResponse], dependencies=[Depends(get_usuario_atual)])
def listar_eventos(db: Session = Depends(get_db)):
    return evento_service.listar_eventos(db)

@router.get("/{id}", response_model=EventoResponse, dependencies=[Depends(get_usuario_atual)])
def buscar_evento(id: int, db: Session = Depends(get_db)):
    return evento_service.buscar_evento_por_id(db, id)

@router.put("/{id}", response_model=EventoResponse, dependencies=[Depends(verificar_admin)])
def atualizar_evento(id: int, evento: EventoUpdate, db: Session = Depends(get_db)):
    return evento_service.atualizar_evento(db, id, evento)

@router.delete("/{id}", dependencies=[Depends(verificar_admin)])
def deletar_evento(id: int, db: Session = Depends(get_db)):
    return evento_service.deletar_evento(db, id)
