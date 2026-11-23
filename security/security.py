import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from database import get_db
from model.usuario import Usuario

# ---------------- Configuração ----------------

# A chave secreta vem da variável de ambiente SECRET_KEY (não fica no código).
# Se ela não for definida, é gerada uma chave aleatória a cada execução
# (funciona, mas os tokens deixam de valer quando a API reinicia).
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    print("AVISO: SECRET_KEY não definida. Usando uma chave temporária.")
    SECRET_KEY = secrets.token_hex(32)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# pwdlib com o algoritmo recomendado (Argon2)
password_hash = PasswordHash.recommended()

# Lê o cabeçalho "Authorization: Bearer <token>"
bearer = HTTPBearer(auto_error=False)

ERRO_CREDENCIAIS = "Não foi possível validar as credenciais."
ERRO_PERMISSAO = "Você não possui permissão para executar esta operação."


# ---------------- Senhas ----------------

def gerar_hash_senha(senha: str) -> str:
    return password_hash.hash(senha)

def verificar_senha(senha: str, senha_hash: str) -> bool:
    return password_hash.verify(senha, senha_hash)


# ---------------- Token JWT ----------------

def criar_token(usuario_id: int, minutos: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=minutos)
    dados = {
        "sub": str(usuario_id),  # identificador do usuário
        "exp": expiracao         # prazo de validade
    }
    return jwt.encode(dados, SECRET_KEY, algorithm=ALGORITHM)

def ler_token(token: str) -> int:
    # jwt.decode verifica a assinatura e a expiração
    try:
        dados = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(dados["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERRO_CREDENCIAIS,
            headers={"WWW-Authenticate": "Bearer"}
        )


# ---------------- Dependências usadas nas rotas ----------------

def get_usuario_atual(
    credenciais: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
) -> Usuario:
    if credenciais is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERRO_CREDENCIAIS,
            headers={"WWW-Authenticate": "Bearer"}
        )

    usuario_id = ler_token(credenciais.credentials)

    # o usuário vem do banco, o perfil nunca vem do cliente
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERRO_CREDENCIAIS,
            headers={"WWW-Authenticate": "Bearer"}
        )
    return usuario

def verificar_admin(usuario: Usuario = Depends(get_usuario_atual)) -> Usuario:
    if usuario.perfil != "administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERRO_PERMISSAO)
    return usuario
