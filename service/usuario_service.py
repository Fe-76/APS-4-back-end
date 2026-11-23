import os
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from model.usuario import Usuario
from schema.usuario_schema import UsuarioCreate
from security.security import gerar_hash_senha

def criar_usuario(db: Session, usuario_schema: UsuarioCreate) -> Usuario:
    existente = db.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um usuário cadastrado com este e-mail.")

    # o perfil é sempre "usuario" no cadastro público
    novo_usuario = Usuario(
        nome=usuario_schema.nome,
        email=usuario_schema.email,
        senha_hash=gerar_hash_senha(usuario_schema.senha),
        perfil="usuario"
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

def listar_usuarios(db: Session):
    return db.query(Usuario).all()

def buscar_usuario_por_id(db: Session, usuario_id: int) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return usuario

def alterar_perfil(db: Session, usuario_id: int, perfil: str) -> Usuario:
    usuario = buscar_usuario_por_id(db, usuario_id)
    usuario.perfil = perfil
    db.commit()
    db.refresh(usuario)
    return usuario

def criar_admin_inicial(db: Session):
    # Cria o primeiro administrador a partir das variáveis de ambiente
    # ADMIN_NOME, ADMIN_EMAIL e ADMIN_SENHA (se estiverem definidas).
    email = os.getenv("ADMIN_EMAIL")
    senha = os.getenv("ADMIN_SENHA")
    nome = os.getenv("ADMIN_NOME", "Administrador")

    if not email or not senha:
        return

    existente = db.query(Usuario).filter(Usuario.email == email).first()
    if existente:
        return

    admin = Usuario(
        nome=nome,
        email=email,
        senha_hash=gerar_hash_senha(senha),
        perfil="administrador"
    )
    db.add(admin)
    db.commit()
    print(f"Administrador inicial criado: {email}")
