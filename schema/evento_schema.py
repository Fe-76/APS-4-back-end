from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time

class EventoBase(BaseModel):
    titulo: str = Field(..., min_length=1, description="Título do evento não pode ser vazio.")
    descricao: Optional[str] = None
    data: date = Field(..., description="Data de realização (AAAA-MM-DD).")
    horario: time = Field(..., description="Horário de realização (HH:MM).")
    local: str = Field(..., min_length=1, description="Local do evento.")
    capacidade: int = Field(..., gt=0, description="A capacidade deve ser maior que zero.")
    categoria: str = Field(..., min_length=1, description="Categoria do evento.")

class EventoCreate(EventoBase):
    pass

class EventoUpdate(EventoBase):
    pass

class EventoResponse(EventoBase):
    id: int

    class Config:
        from_attributes = True
