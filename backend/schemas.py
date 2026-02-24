# backend/schemas.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ConfiguracaoBase(BaseModel):
    chave: str
    valor: int

class ConfiguracaoCreate(ConfiguracaoBase):
    pass

class ConfiguracaoResponse(ConfiguracaoBase):
    # O jeito moderno do Pydantic V2 de ler dados do SQLAlchemy
    model_config = ConfigDict(from_attributes=True)



class JogadorBase(BaseModel):
    nome: str
    whatsapp: str
    sexo: str
    avatar: Optional[str] = None # Optional significa que pode vir vazio/nulo

class JogadorCreate(JogadorBase):
    pass

class JogadorResponse(JogadorBase):
    id: str
    is_ativo: bool
    is_presente: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)