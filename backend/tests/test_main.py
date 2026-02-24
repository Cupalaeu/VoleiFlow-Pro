# backend/tests/test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "Online", "app": "VôleiFlow 2.0"}

# Nosso novo teste
def test_listar_configuracoes_vazias():
    # 1. Ação: Simulamos um acesso GET na nova rota
    response = client.get("/configuracoes")
    
    # 2. Verificação: O servidor respondeu com sucesso (200 OK)?
    assert response.status_code == 200
    
    # 3. Verificação: Como não populamos o banco, o retorno DEVE ser uma lista vazia
    assert response.json() == []

# backend/tests/test_main.py (Adicionar no final)

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