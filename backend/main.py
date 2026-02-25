# backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine
import schemas
from pydantic import BaseModel
import random
from datetime import datetime, timezone
import random
from typing import Optional

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

class FilaAcaoRequest(BaseModel):
    jogador_id: str

# --- Adicione estas rotas lá no final do arquivo ---

@app.get("/estado")
def obter_estado():
    # Qualquer dispositivo pode bater aqui para saber como está a quadra agora
    return ESTADO_MEMORIA

@app.post("/fila/entrar")
def entrar_na_fila(requisicao: FilaAcaoRequest):
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

@app.post("/fila/sair")
def sair_da_fila(requisicao: FilaAcaoRequest):
    jogador_id = requisicao.jogador_id
    
    # Se o jogador estiver na fila, removemos
    if jogador_id in ESTADO_MEMORIA["fila"]:
        ESTADO_MEMORIA["fila"].remove(jogador_id)
        
    return {"mensagem": "Removido", "fila": ESTADO_MEMORIA["fila"]}

@app.post("/fila/final")
def mover_para_final(requisicao: FilaAcaoRequest):
    jogador_id = requisicao.jogador_id
    
    if jogador_id in ESTADO_MEMORIA["fila"]:
        ESTADO_MEMORIA["fila"].remove(jogador_id)
        ESTADO_MEMORIA["fila"].append(jogador_id) # Coloca no fim da lista
        
    return {"mensagem": "Movido para o final", "fila": ESTADO_MEMORIA["fila"]}

@app.post("/fila/embaralhar")
def embaralhar_fila():
    # random.shuffle altera a lista original diretamente na memória
    random.shuffle(ESTADO_MEMORIA["fila"])
    return {"mensagem": "Fila embaralhada", "fila": ESTADO_MEMORIA["fila"]}

@app.post("/quadras/{quadra_id}/iniciar")
def iniciar_partida(quadra_id: int, db: Session = Depends(get_db)):
    if quadra_id not in [1, 2]:
        raise HTTPException(status_code=400, detail="Quadra inválida.")
        
    jogo_atual = ESTADO_MEMORIA["jogos"].get(quadra_id)
    if jogo_atual and jogo_atual.get("status") == "JOGANDO":
        raise HTTPException(status_code=400, detail="Quadra já está em uso.")

    # 1. Pega a configuração de Tamanho do Time (Padrão 4 se não existir)
    config_tamanho = db.query(models.Configuracao).filter(models.Configuracao.chave == "TamanhoTime").first()
    tamanho_time = config_tamanho.valor if config_tamanho else 4
    necessarios = tamanho_time * 2

    # 2. Verifica se tem gente suficiente
    if len(ESTADO_MEMORIA["fila"]) < necessarios:
        raise HTTPException(status_code=400, detail=f"Fila insuficiente. Necessários: {necessarios}.")

    # 3. Separa os selecionados e atualiza a fila principal
    selecionados_ids = ESTADO_MEMORIA["fila"][:necessarios]
    ESTADO_MEMORIA["fila"] = ESTADO_MEMORIA["fila"][necessarios:]

    # 4. Aleatoriza PRIMEIRO (A sua regra de quebrar panelinhas)
    random.shuffle(selecionados_ids)

    # 5. Busca no banco de dados o sexo de quem foi selecionado
    jogadores_db = db.query(models.Jogador).filter(models.Jogador.id.in_(selecionados_ids)).all()
    mapa_sexo = {j.id: j.sexo for j in jogadores_db}

    mulheres = [jid for jid in selecionados_ids if mapa_sexo.get(jid) == 'F']
    homens = [jid for jid in selecionados_ids if mapa_sexo.get(jid) != 'F'] # Trata 'M' ou nulo como masculino

    time_a = []
    time_b = []

    # 6. Distribui as mulheres alternadamente
    for i, f_id in enumerate(mulheres):
        if i % 2 == 0:
            time_a.append(f_id)
        else:
            time_b.append(f_id)
            
    # 7. Preenche as vagas restantes com os homens
    for m_id in homens:
        if len(time_a) < tamanho_time:
            time_a.append(m_id)
        else:
            time_b.append(m_id)

    # 8. Grava o novo estado da quadra na memória
    ESTADO_MEMORIA["jogos"][quadra_id] = {
        "status": "JOGANDO",
        "inicio": datetime.now(timezone.utc).isoformat(),
        "placar": {"A": 0, "B": 0},
        "timeA": time_a,
        "timeB": time_b,
        "vitoriasConsecutivas": {"A": 0, "B": 0}
    }

    return {"mensagem": "Partida iniciada", "estado_quadra": ESTADO_MEMORIA["jogos"][quadra_id]}

# Molde para a requisição de alterar placar
class PlacarRequest(BaseModel):
    time: str # 'A' ou 'B'
    delta: int # 1 para somar, -1 para subtrair

@app.post("/quadras/{quadra_id}/placar")
def atualizar_placar(quadra_id: int, requisicao: PlacarRequest):
    jogo = ESTADO_MEMORIA["jogos"].get(quadra_id)
    if not jogo or jogo["status"] != "JOGANDO":
        raise HTTPException(status_code=400, detail="Nenhum jogo ativo nesta quadra.")
    
    time = requisicao.time.upper()
    if time not in ["A", "B"]:
        raise HTTPException(status_code=400, detail="Time inválido. Use 'A' ou 'B'.")
        
    novo_placar = jogo["placar"][time] + requisicao.delta
    # Impede placar negativo
    jogo["placar"][time] = max(0, novo_placar)
    
    return {"mensagem": "Placar atualizado", "placar": jogo["placar"]}

@app.post("/quadras/{quadra_id}/encerrar")
def encerrar_partida_manual(quadra_id: int, db: Session = Depends(get_db)):
    jogo = ESTADO_MEMORIA["jogos"].get(quadra_id)
    if not jogo or jogo["status"] != "JOGANDO":
        raise HTTPException(status_code=400, detail="Nenhum jogo ativo nesta quadra.")
        
    # 1. Salva a Partida Principal no Banco
    nova_partida = models.Partida(
        quadra_id=quadra_id,
        inicio=datetime.fromisoformat(jogo["inicio"]),
        fim=datetime.now(timezone.utc),
        placar_a=jogo["placar"]["A"],
        placar_b=jogo["placar"]["B"],
        vencedor=None, # Como foi manual, não tem vencedor formal
        motivo_fim="Cancelada"
    )
    db.add(nova_partida)
    db.commit()
    db.refresh(nova_partida)
    
    # 2. Salva o Histórico de cada jogador no Banco (O seu registro atuarial)
    todos_jogadores = []
    
    for j_id in jogo["timeA"]:
        hist = models.PartidaHistorico(partida_id=nova_partida.id, jogador_id=j_id, time="A", resultado="Empate")
        db.add(hist)
        todos_jogadores.append(j_id)
        
    for j_id in jogo["timeB"]:
        hist = models.PartidaHistorico(partida_id=nova_partida.id, jogador_id=j_id, time="B", resultado="Empate")
        db.add(hist)
        todos_jogadores.append(j_id)
        
    db.commit()
    
    # 3. Devolve a galera para a fila em ordem aleatória
    random.shuffle(todos_jogadores)
    ESTADO_MEMORIA["fila"].extend(todos_jogadores)
    
    # 4. Limpa a quadra
    ESTADO_MEMORIA["jogos"][quadra_id] = None
    
    return {"mensagem": "Partida encerrada manualmente e salva no histórico.", "fila": ESTADO_MEMORIA["fila"]}

class VitoriaRequest(BaseModel):
    time_vencedor: str # 'A' ou 'B'
    placar_a: Optional[int] = None
    placar_b: Optional[int] = None

@app.post("/quadras/{quadra_id}/vitoria")
def registrar_vitoria(quadra_id: int, req: VitoriaRequest, db: Session = Depends(get_db)):
    jogo = ESTADO_MEMORIA["jogos"].get(quadra_id)
    if not jogo or jogo["status"] != "JOGANDO":
        raise HTTPException(status_code=400, detail="Nenhum jogo ativo nesta quadra.")

    vencedor = req.time_vencedor.upper()
    if vencedor not in ["A", "B"]:
        raise HTTPException(status_code=400, detail="Vencedor inválido. Use 'A' ou 'B'.")
        
    perdedor = "B" if vencedor == "A" else "A"

    # 1. Ajuste final de placar (se o Front enviou correção no modal)
    if req.placar_a is not None: jogo["placar"]["A"] = req.placar_a
    if req.placar_b is not None: jogo["placar"]["B"] = req.placar_b

    # 2. Salva a Partida Principal no Banco
    nova_partida = models.Partida(
        quadra_id=quadra_id,
        inicio=datetime.fromisoformat(jogo["inicio"]),
        fim=datetime.now(timezone.utc),
        placar_a=jogo["placar"]["A"],
        placar_b=jogo["placar"]["B"],
        vencedor=vencedor,
        motivo_fim="Pontuacao"
    )
    db.add(nova_partida)
    db.flush() # Envia pro banco para gerar o ID, mas não commita ainda

    ids_vencedores = jogo[f"time{vencedor}"]
    ids_perdedores = jogo[f"time{perdedor}"]

    # 3. Salva o Histórico de cada jogador
    for j_id in ids_vencedores:
        db.add(models.PartidaHistorico(partida_id=nova_partida.id, jogador_id=j_id, time=vencedor, resultado="Vitoria"))
    for j_id in ids_perdedores:
        db.add(models.PartidaHistorico(partida_id=nova_partida.id, jogador_id=j_id, time=perdedor, resultado="Derrota"))
    db.commit()

    # 4. Rotaciona os Perdedores (Vão para a fila embaralhados)
    perdedores_embaralhados = ids_perdedores.copy()
    random.shuffle(perdedores_embaralhados)
    ESTADO_MEMORIA["fila"].extend(perdedores_embaralhados)

    # 5. Avalia o Limite de Vitórias
    config_max = db.query(models.Configuracao).filter(models.Configuracao.chave == "MaxVitorias").first()
    max_vitorias = config_max.valor if config_max else 3
    
    jogo["vitoriasConsecutivas"][vencedor] += 1
    jogo["vitoriasConsecutivas"][perdedor] = 0 # Reseta o outro lado

    if jogo["vitoriasConsecutivas"][vencedor] >= max_vitorias:
        # Atingiu o limite: Vencedores também saem
        vencedores_embaralhados = ids_vencedores.copy()
        random.shuffle(vencedores_embaralhados)
        ESTADO_MEMORIA["fila"].extend(vencedores_embaralhados)
        
        ESTADO_MEMORIA["jogos"][quadra_id] = None # Esvazia a quadra
        msg = f"Limite de {max_vitorias} vitórias atingido. Todos para a fila."
    else:
        # Não atingiu o limite: Puxa desafiantes (O "Loop" perfeito dos 8 jogadores)
        config_tamanho = db.query(models.Configuracao).filter(models.Configuracao.chave == "TamanhoTime").first()
        tamanho_time = config_tamanho.valor if config_tamanho else 4

        if len(ESTADO_MEMORIA["fila"]) >= tamanho_time:
            novos_desafiantes = ESTADO_MEMORIA["fila"][:tamanho_time]
            ESTADO_MEMORIA["fila"] = ESTADO_MEMORIA["fila"][tamanho_time:]
            
            # Substitui o time que perdeu
            jogo[f"time{perdedor}"] = novos_desafiantes
            # Reseta a quadra para a nova partida
            jogo["placar"] = {"A": 0, "B": 0}
            jogo["inicio"] = datetime.now(timezone.utc).isoformat()
            msg = "Vitória registrada. Novos desafiantes entraram."
        else:
            # Regra de fallback (quase impossível de ocorrer devido ao loop, mas previne travamento do app)
            vencedores_embaralhados = ids_vencedores.copy()
            random.shuffle(vencedores_embaralhados)
            ESTADO_MEMORIA["fila"].extend(vencedores_embaralhados)
            ESTADO_MEMORIA["jogos"][quadra_id] = None
            msg = "Fila insuficiente para continuar, quadra esvaziada."

    return {"mensagem": msg, "estado_quadra": ESTADO_MEMORIA["jogos"].get(quadra_id)}

class SubstituicaoRequest(BaseModel):
    id_saindo: str
    id_entrando: str

@app.post("/quadras/{quadra_id}/substituir")
def substituir_jogador(quadra_id: int, req: SubstituicaoRequest):
    jogo = ESTADO_MEMORIA["jogos"].get(quadra_id)
    
    # 1. Validações Iniciais
    if not jogo or jogo["status"] != "JOGANDO":
        raise HTTPException(status_code=400, detail="Nenhum jogo ativo nesta quadra.")
        
    if req.id_entrando not in ESTADO_MEMORIA["fila"]:
        raise HTTPException(status_code=400, detail="O jogador substituto não está na fila de espera.")

    # 2. Descobre em qual time o jogador que vai sair está
    time_alvo = None
    if req.id_saindo in jogo["timeA"]:
        time_alvo = "timeA"
    elif req.id_saindo in jogo["timeB"]:
        time_alvo = "timeB"
    else:
        raise HTTPException(status_code=400, detail="O jogador que vai sair não está na quadra.")

    # 3. Faz a troca no time (Sai um, Entra o outro)
    jogo[time_alvo].remove(req.id_saindo)
    jogo[time_alvo].append(req.id_entrando)

    # 4. Atualiza a fila (Remove o substituto e joga quem saiu pro final)
    ESTADO_MEMORIA["fila"].remove(req.id_entrando)
    ESTADO_MEMORIA["fila"].append(req.id_saindo)

    return {"mensagem": "Substituição realizada com sucesso", "estado_quadra": jogo}