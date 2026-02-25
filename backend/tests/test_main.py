# backend/tests/test_main.py
from fastapi.testclient import TestClient
from main import app, ESTADO_MEMORIA

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "Online", "app": "VôleiFlow 2.0"}

# Nosso novo teste
# def test_listar_configuracoes_vazias():
#     # 1. Ação: Simulamos um acesso GET na nova rota
#     response = client.get("/configuracoes")
    
#     # 2. Verificação: O servidor respondeu com sucesso (200 OK)?
#     assert response.status_code == 200
    
#     # 3. Verificação: Como não populamos o banco, o retorno DEVE ser uma lista vazia
#     assert response.json() == []

def test_criar_configuracao():
    # Enviando um JSON para a rota POST
    payload = {"chave": "PontosMaximos", "valor": 21}
    response = client.post("/configuracoes", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"chave": "PontosMaximos", "valor": 21}

def test_atualizar_configuracao_existente():
    # Mudando o valor da mesma chave para ver se atualiza em vez de duplicar
    payload = {"chave": "PontosMaximos", "valor": 15}
    response = client.post("/configuracoes", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"chave": "PontosMaximos", "valor": 15}

def test_criar_jogador():
    # Simulando o Front-end enviando um JSON com seus dados
    payload = {
        "nome": "Robson",
        "whatsapp": "85999999999",
        "sexo": "M",
        "avatar": "🏐"
    }
    response = client.post("/jogadores", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Robson"
    assert "id" in data # Verifica se o UUID foi gerado
    assert data["is_ativo"] == True # O padrão deve ser True

def test_listar_jogadores_ativos():
    response = client.get("/jogadores")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list) # Tem que ser uma lista
    assert len(data) > 0 # Como acabamos de criar o Robson no teste acima, não pode estar vazia
    assert data[0]["nome"] == "Robson"

def test_atualizar_status_jogador():
    # 1. Cria um jogador específico para testar o status
    response_criacao = client.post("/jogadores", json={
        "nome": "João do Teste",
        "whatsapp": "85911112222", # Número diferente para não dar erro de "unique"
        "sexo": "M",
        "avatar": "👤"
    })
    
    # Pegamos o ID real que o banco gerou
    jogador_id = response_criacao.json()["id"]
    
    # 2. Testa o PATCH enviando apenas o comando para marcar presença
    response_patch = client.patch(f"/jogadores/{jogador_id}/status", json={"is_presente": True})
    
    assert response_patch.status_code == 200
    assert response_patch.json()["is_presente"] == True

def test_atualizar_placar_e_encerrar():
    # 0. SETUP: Configurar a quadra 1 artificialmente para isolar o teste
    # Garantimos que, não importa o que aconteça, a quadra tem um jogo rodando
    ESTADO_MEMORIA["jogos"][1] = {
        "status": "JOGANDO",
        "inicio": "2026-02-24T12:00:00Z",
        "placar": {"A": 0, "B": 0},
        "timeA": ["jogador_simulado_1", "jogador_simulado_2"],
        "timeB": ["jogador_simulado_3", "jogador_simulado_4"],
        "vitoriasConsecutivas": {"A": 0, "B": 0}
    }
    ESTADO_MEMORIA["fila"] = [] # Zeramos a fila temporariamente
    fila_antes = 0

    # 1. Testa Placar (Adiciona 1 ponto pro Time A, duas vezes)
    client.post("/quadras/1/placar", json={"time": "A", "delta": 1})
    resp_placar = client.post("/quadras/1/placar", json={"time": "A", "delta": 1})
    
    assert resp_placar.status_code == 200
    assert resp_placar.json()["placar"]["A"] == 2
    
    # 2. Testa subtrair placar
    client.post("/quadras/1/placar", json={"time": "A", "delta": -1})
    estado_atual = client.get("/estado").json()
    assert estado_atual["jogos"]["1"]["placar"]["A"] == 1
    
    # 3. Testa Encerramento Manual
    resp_encerrar = client.post("/quadras/1/encerrar")
    assert resp_encerrar.status_code == 200
    
    estado_final = client.get("/estado").json()
    
    # A quadra deve estar vazia
    assert estado_final["jogos"]["1"] is None
    
    # A fila deve ter recebido as 4 pessoas que simulamos na quadra
    assert len(estado_final["fila"]) == fila_antes + 4

def test_registrar_vitoria_e_rotacao():
    # 0. SETUP: Criamos uma quadra rodando (4v4)
    ESTADO_MEMORIA["jogos"][1] = {
        "status": "JOGANDO",
        "inicio": "2026-02-24T12:00:00Z",
        "placar": {"A": 20, "B": 18},
        "timeA": ["v_1", "v_2", "v_3", "v_4"],
        "timeB": ["p_1", "p_2", "p_3", "p_4"],
        "vitoriasConsecutivas": {"A": 0, "B": 0}
    }
    # Fila tem 4 desafiantes esperando (Para bater com o TamanhoTime = 4 do Banco)
    ESTADO_MEMORIA["fila"] = ["d_1", "d_2", "d_3", "d_4"] 
    
    # 1. Ação: Time A faz o último ponto e ganha
    resp = client.post("/quadras/1/vitoria", json={
        "time_vencedor": "A",
        "placar_a": 21,
        "placar_b": 18
    })
    
    assert resp.status_code == 200
    
    # 2. Verificações do Estado da Quadra
    estado = client.get("/estado").json()
    jogo = estado["jogos"]["1"]
    
    # O jogo deve ter reiniciado
    assert jogo["placar"]["A"] == 0
    assert jogo["placar"]["B"] == 0
    assert jogo["vitoriasConsecutivas"]["A"] == 1
    
    # Os perdedores saíram e os desafiantes entraram no Time B
    assert "p_1" not in jogo["timeB"]
    assert "d_1" in jogo["timeB"]
    assert len(jogo["timeB"]) == 4
    
    # Os perdedores estão agora na fila principal
    assert "p_1" in estado["fila"]
    assert "p_4" in estado["fila"]