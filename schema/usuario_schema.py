from pydantic import BaseModel, EmailStr, Field
from typing import Literal

class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=1, description="Nome do usuário não pode ser vazio.")
    email: EmailStr = Field(..., description="E-mail usado para fazer login.")
    senha: str = Field(..., min_length=6, description="A senha deve ter pelo menos 6 caracteres.")
    # Não existe campo "perfil" aqui: se o cliente mandar "perfil": "administrador",
    # o Pydantic ignora e o usuário é criado como "usuario".

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    perfil: str

    class Config:
        from_attributes = True

class PerfilUpdate(BaseModel):
    perfil: Literal["administrador", "usuario"]
