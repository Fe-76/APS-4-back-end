from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from model.usuario import Usuario
from schema.auth_schema import LoginRequest, TokenResponse
from schema.usuario_schema import UsuarioResponse
from security.security import get_usuario_atual
from service import auth_service

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/login", response_model=TokenResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.autenticar(db, dados)

@router.get("/me", response_model=UsuarioResponse)
def meus_dados(usuario: Usuario = Depends(get_usuario_atual)):
    return usuario
