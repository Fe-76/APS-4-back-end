from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from model.usuario import Usuario
from schema.auth_schema import LoginRequest
from security.security import verificar_senha, criar_token

def autenticar(db: Session, login: LoginRequest) -> dict:
    usuario = db.query(Usuario).filter(Usuario.email == login.email).first()

    # mesma mensagem para e-mail inexistente e senha errada
    if not usuario or not verificar_senha(login.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = criar_token(usuario.id)
    return {"access_token": token, "token_type": "bearer"}
