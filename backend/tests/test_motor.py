# backend/tests/test_motor.py
from fastapi.testclient import TestClient
from main import app, ESTADO_MEMORIA

client = TestClient(app)

def test_estado_inicial():
    response = client.get("/estado")
    assert response.status_code == 200
    estado = response.json()
    assert estado["fila"] == [] # Tem que começar vazia
    assert estado["jogos"]["1"] is None # Quadra 1 vazia (no JSON, chaves viram strings)

def test_entrar_na_fila():
    # Simula o Robson clicando para entrar na fila
    payload = {"jogador_id": "id-do-robson-123"}
    response = client.post("/fila/entrar", json=payload)
    
    assert response.status_code == 200
    assert "id-do-robson-123" in response.json()["fila"]
    
    # Tenta entrar de novo para garantir que não duplica
    client.post("/fila/entrar", json=payload)
    
    # Puxa o estado global para verificar
    estado_atual = client.get("/estado").json()
    assert len(estado_atual["fila"]) == 1 # Tem que continuar sendo apenas 1

def test_sair_da_fila():
    # 1. Injetamos um estado controlado na memória
    ESTADO_MEMORIA["fila"] = ["id-1", "id-2", "id-3"]
    
    # 2. Ação: Pedimos para o id-2 sair
    client.post("/fila/sair", json={"jogador_id": "id-2"})
    
    # 3. Verificação: O id-2 deve sumir, mantendo a ordem dos restantes
    assert ESTADO_MEMORIA["fila"] == ["id-1", "id-3"]

def test_mover_para_final():
    ESTADO_MEMORIA["fila"] = ["id-a", "id-b", "id-c"]
    
    # Ação: O id-a foi beber água e perdeu a vez
    client.post("/fila/final", json={"jogador_id": "id-a"})
    
    # Verificação: Ele deve ser o último da lista agora
    assert ESTADO_MEMORIA["fila"] == ["id-b", "id-c", "id-a"]

def test_embaralhar_fila():
    fila_original = ["j1", "j2", "j3", "j4", "j5"]
    ESTADO_MEMORIA["fila"] = fila_original.copy()
    
    client.post("/fila/embaralhar")
    
    # Verificação de integridade: Todos os elementos originais ainda devem estar na lista
    assert sorted(ESTADO_MEMORIA["fila"]) == sorted(fila_original)
    
    # A ordem exata pode bater com a original por pura probabilidade (embora baixa),
    # o teste garante que a rota funciona sem perder dados ou causar erro 500.

def test_iniciar_partida_com_balanceamento():
    # 1. Limpa a fila na memória para garantir um teste isolado
    ESTADO_MEMORIA["fila"] = []
    
    # 2. Criamos 8 jogadores na API (4 Homens e 4 Mulheres) para formar um jogo 4v4
    ids_criados = []
    for i in range(8):
        sexo = "M" if i < 4 else "F" # Primeiros 4 são M, últimos 4 são F
        resp = client.post("/jogadores", json={
            "nome": f"Jogador {i}",
            "sexo": sexo,
            "whatsapp": f"8590000000{i}" 
        })
        jogador_id = resp.json()["id"]
        ids_criados.append(jogador_id)
        
        # Aproveita e já coloca na fila da memória
        client.post("/fila/entrar", json={"jogador_id": jogador_id})
        
    # 3. Verifica se os 8 estão na fila
    assert len(ESTADO_MEMORIA["fila"]) >= 8
    
    # 4. Inicia a partida na Quadra 1
    resp_inicio = client.post("/quadras/1/iniciar")
    assert resp_inicio.status_code == 200
    
    estado_jogo = resp_inicio.json()["estado_quadra"]
    
    # 5. Verifica se os times foram formados corretamente
    assert estado_jogo["status"] == "JOGANDO"
    assert len(estado_jogo["timeA"]) == 4
    assert len(estado_jogo["timeB"]) == 4
    assert estado_jogo["placar"]["A"] == 0
    assert estado_jogo["placar"]["B"] == 0