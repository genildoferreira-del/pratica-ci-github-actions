import pytest
from app import app


# Cria um cliente de teste falso para nao precisarmos subir o servidor real
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_status_code(client):
    resposta = client.get('/')
    assert resposta.status_code == 200


def test_home_mensagem(client):
    resposta = client.get('/')
    dados = resposta.get_json()
    assert dados['mensagem'] == "Bem-vindo a API FastOrder!"


def test_status(client):
    resposta = client.get('/api/status')
    assert resposta.status_code == 200
    assert resposta.get_json()['status'] == "operacional"


def test_soma(client):
    resposta = client.get('/api/soma?a=10&b=5')
    assert resposta.status_code == 200
    assert resposta.get_json()['resultado'] == 15


def test_soma_parametro_invalido(client):
    resposta = client.get('/api/soma?a=abc&b=5')
    assert resposta.status_code == 400


# ---------- Feature Flag: FEATURE_DESCONTO_PROMO ----------

def test_desconto_desativado_por_padrao(client, monkeypatch):
    # Sem a variavel de ambiente, a flag fica DESLIGADA
    monkeypatch.delenv("FEATURE_DESCONTO_PROMO", raising=False)
    resposta = client.get('/api/desconto?preco=100')
    assert resposta.status_code == 404


def test_desconto_desativado_explicito(client, monkeypatch):
    monkeypatch.setenv("FEATURE_DESCONTO_PROMO", "false")
    resposta = client.get('/api/desconto?preco=100')
    assert resposta.status_code == 404


def test_desconto_ativado(client, monkeypatch):
    monkeypatch.setenv("FEATURE_DESCONTO_PROMO", "true")
    resposta = client.get('/api/desconto?preco=100')
    assert resposta.status_code == 200
    dados = resposta.get_json()
    assert dados['preco_final'] == 90
    assert dados['desconto_percentual'] == 10


def test_desconto_ativado_preco_invalido(client, monkeypatch):
    monkeypatch.setenv("FEATURE_DESCONTO_PROMO", "true")
    resposta = client.get('/api/desconto?preco=abc')
    assert resposta.status_code == 400


def test_desconto_ativado_preco_negativo(client, monkeypatch):
    monkeypatch.setenv("FEATURE_DESCONTO_PROMO", "true")
    resposta = client.get('/api/desconto?preco=-5')
    assert resposta.status_code == 400


def test_status_mostra_estado_da_flag(client, monkeypatch):
    monkeypatch.setenv("FEATURE_DESCONTO_PROMO", "true")
    ligada = client.get('/api/status').get_json()
    assert ligada['features']['desconto_promo'] is True

    monkeypatch.setenv("FEATURE_DESCONTO_PROMO", "false")
    desligada = client.get('/api/status').get_json()
    assert desligada['features']['desconto_promo'] is False