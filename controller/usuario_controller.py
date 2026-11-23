from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schema.usuario_schema import UsuarioCreate, UsuarioResponse, PerfilUpdate
from security.security import verificar_admin
from service import usuario_service

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

# Rota pública: qualquer pessoa pode se cadastrar (sempre como "usuario")
@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    return usuario_service.criar_usuario(db, usuario)

@router.get("", response_model=List[UsuarioResponse], dependencies=[Depends(verificar_admin)])
def listar_usuarios(db: Session = Depends(get_db)):
    return usuario_service.listar_usuarios(db)

# Só um administrador pode transformar outro usuário em administrador
@router.put("/{id}/perfil", response_model=UsuarioResponse, dependencies=[Depends(verificar_admin)])
def alterar_perfil(id: int, dados: PerfilUpdate, db: Session = Depends(get_db)):
    return usuario_service.alterar_perfil(db, id, dados.perfil)
