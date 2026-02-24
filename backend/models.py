# backend/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Jogador(Base):
    __tablename__ = "jogadores"

    id = Column(String, primary_key=True, default=generate_uuid)
    nome = Column(String, index=True)
    whatsapp = Column(String, index=True, nullable=True)
    sexo = Column(String(1)) # 'M' ou 'F'
    avatar = Column(String)
    is_ativo = Column(Boolean, default=True)
    is_presente = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relacionamento reverso para o histórico
    historico = relationship("PartidaHistorico", back_populates="jogador")

class Partida(Base):
    __tablename__ = "partidas"

    id = Column(String, primary_key=True, default=generate_uuid)
    quadra_id = Column(Integer)
    inicio = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    fim = Column(DateTime, nullable=True)
    placar_a = Column(Integer, default=0)
    placar_b = Column(Integer, default=0)
    vencedor = Column(String(1), nullable=True) # 'A', 'B' ou Null
    motivo_fim = Column(String, nullable=True) # 'Pontuacao', 'Cancelada'

    detalhes = relationship("PartidaHistorico", back_populates="partida")

class PartidaHistorico(Base):
    __tablename__ = "partidas_historico"

    id = Column(String, primary_key=True, default=generate_uuid)
    partida_id = Column(String, ForeignKey("partidas.id"))
    jogador_id = Column(String, ForeignKey("jogadores.id"))
    time = Column(String(1)) # 'A' ou 'B'
    resultado = Column(String) # 'Vitoria', 'Derrota', 'Empate'

    partida = relationship("Partida", back_populates="detalhes")
    jogador = relationship("Jogador", back_populates="historico")

class Configuracao(Base):
    __tablename__ = "configuracoes"

    chave = Column(String, primary_key=True) # Ex: 'PontosMaximos'
    valor = Column(Integer)