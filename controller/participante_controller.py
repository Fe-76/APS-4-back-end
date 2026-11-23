from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schema.participante_schema import ParticipanteCreate, ParticipanteUpdate, ParticipanteResponse
from security.security import get_usuario_atual, verificar_admin
from service import participante_service

router = APIRouter(prefix="/participantes", tags=["Participantes"])

# Cadastrar e consultar: qualquer usuário autenticado
@router.post("", response_model=ParticipanteResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_usuario_atual)])
def criar_participante(participante: ParticipanteCreate, db: Session = Depends(get_db)):
    return participante_service.criar_participante(db, participante)

@router.get("", response_model=List[ParticipanteResponse], dependencies=[Depends(get_usuario_atual)])
def listar_participantes(db: Session = Depends(get_db)):
    return participante_service.listar_participantes(db)

@router.get("/{id}", response_model=ParticipanteResponse, dependencies=[Depends(get_usuario_atual)])
def buscar_participante(id: int, db: Session = Depends(get_db)):
    return participante_service.buscar_participante_por_id(db, id)

# Atualizar e excluir: somente administrador
@router.put("/{id}", response_model=ParticipanteResponse, dependencies=[Depends(verificar_admin)])
def atualizar_participante(id: int, participante: ParticipanteUpdate, db: Session = Depends(get_db)):
    return participante_service.atualizar_participante(db, id, participante)

@router.delete("/{id}", dependencies=[Depends(verificar_admin)])
def deletar_participante(id: int, db: Session = Depends(get_db)):
    return participante_service.deletar_participante(db, id)
