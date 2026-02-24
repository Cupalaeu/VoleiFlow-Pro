# backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine
import schemas
from pydantic import BaseModel

# Garante que as tabelas existam (útil caso o arquivo .db seja deletado acidentalmente)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="VôleiFlow API", version="2.0")

# A nossa variável global que todos os dispositivos vão enxergar
ESTADO_MEMORIA = {
    "fila": [], # Guardará apenas as strings dos IDs dos jogadores
    "jogos": {
        1: None,
        2: None
    }
}

# Molde simples para receber o ID de quem quer entrar na fila
class FilaEntrarRequest(BaseModel):
    jogador_id: str

# --- Adicione estas rotas lá no final do arquivo ---

@app.get("/estado")
def obter_estado():
    # Qualquer dispositivo pode bater aqui para saber como está a quadra agora
    return ESTADO_MEMORIA

@app.post("/fila/entrar")
def entrar_na_fila(requisicao: FilaEntrarRequest):
    jogador_id = requisicao.jogador_id
    
    # Regra de Negócio: Não deixa entrar duplicado
    if jogador_id not in ESTADO_MEMORIA["fila"]:
        ESTADO_MEMORIA["fila"].append(jogador_id)
        
    return {"mensagem": "Adicionado com sucesso", "fila": ESTADO_MEMORIA["fila"]}

# Nossa função 'recepcionista' para gerenciar a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "Online", "app": "VôleiFlow 2.0"}

# Nossa nova rota conectada ao banco de dados
@app.get("/configuracoes")
def listar_configuracoes(db: Session = Depends(get_db)):
    # Faz uma query (consulta) pedindo todos os registros da tabela Configuracao
    configuracoes = db.query(models.Configuracao).all()
    return configuracoes

@app.post("/configuracoes", response_model=schemas.ConfiguracaoResponse)
def criar_ou_atualizar_configuracao(config: schemas.ConfiguracaoCreate, db: Session = Depends(get_db)):
    # Busca se a configuração já existe no banco
    db_config = db.query(models.Configuracao).filter(models.Configuracao.chave == config.chave).first()
    
    if db_config:
        # Atualiza se existir
        db_config.valor = config.valor
    else:
        # Cria nova se não existir
        db_config = models.Configuracao(chave=config.chave, valor=config.valor)
        db.add(db_config)
    
    db.commit() # Salva no banco
    db.refresh(db_config) # Atualiza a variável com os dados do banco
    return db_config

@app.post("/jogadores", response_model=schemas.JogadorResponse)
def criar_jogador(jogador: schemas.JogadorCreate, db: Session = Depends(get_db)):
    # Transforma o molde do Pydantic no modelo do SQLAlchemy
    db_jogador = models.Jogador(
        nome=jogador.nome,
        whatsapp=jogador.whatsapp,
        sexo=jogador.sexo,
        avatar=jogador.avatar
    )
    db.add(db_jogador)
    db.commit()
    db.refresh(db_jogador)
    return db_jogador

# O response_model como list[] garante que o FastAPI vai devolver um Array JSON
@app.get("/jogadores", response_model=list[schemas.JogadorResponse])
def listar_jogadores_ativos(db: Session = Depends(get_db)):
    # Busca todos onde is_ativo é Verdadeiro
    jogadores = db.query(models.Jogador).filter(models.Jogador.is_ativo == True).all()
    return jogadores

@app.put("/jogadores/{jogador_id}", response_model=schemas.JogadorResponse)
def atualizar_jogador(jogador_id: str, atualizacao: schemas.JogadorUpdate, db: Session = Depends(get_db)):
    db_jogador = db.query(models.Jogador).filter(models.Jogador.id == jogador_id).first()
    if not db_jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    # Extrai apenas os campos que o Front-end enviou na requisição
    dados_atualizacao = atualizacao.model_dump(exclude_unset=True)
    
    # Atualiza dinamicamente o modelo do banco
    for chave, valor in dados_atualizacao.items():
        setattr(db_jogador, chave, valor)
        
    db.commit()
    db.refresh(db_jogador)
    return db_jogador

@app.patch("/jogadores/{jogador_id}/status", response_model=schemas.JogadorResponse)
def alterar_status_jogador(jogador_id: str, status: schemas.JogadorStatusUpdate, db: Session = Depends(get_db)):
    db_jogador = db.query(models.Jogador).filter(models.Jogador.id == jogador_id).first()
    if not db_jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    dados_status = status.model_dump(exclude_unset=True)
    for chave, valor in dados_status.items():
        setattr(db_jogador, chave, valor)
        
    db.commit()
    db.refresh(db_jogador)
    return db_jogador