# backend/tests/test_motor.py
from fastapi.testclient import TestClient
from main import app

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