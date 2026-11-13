import os

from flask import Flask, jsonify, request

app = Flask(__name__)

# Percentual fixo da promocao (so vale quando a Feature Flag esta ligada)
DESCONTO_PERCENTUAL = 10


def feature_desconto_ativa():
    """Feature Flag controlada por variavel de ambiente.

    Lida a CADA requisicao (e nao uma vez so na importacao), entao mudar
    FEATURE_DESCONTO_PROMO muda o comportamento sem alterar o codigo.
    """
    valor = os.getenv("FEATURE_DESCONTO_PROMO", "false")
    return valor.strip().lower() == "true"


@app.route('/')
def home():
    return jsonify({"mensagem": "Bem-vindo a API FastOrder!"})


@app.route('/api/status')
def status():
    return jsonify({
        "status": "operacional",
        "servico": "FastOrder-Web",
        "features": {"desconto_promo": feature_desconto_ativa()},
    })


@app.route('/api/soma')
def soma():
    try:
        a = float(request.args.get('a'))
        b = float(request.args.get('b'))
    except (TypeError, ValueError):
        return jsonify({
            "erro": "Informe os parametros numericos a e b. Ex: ?a=2&b=3"
        }), 400

    resultado = a + b
    if resultado.is_integer():
        resultado = int(resultado)
    return jsonify({"resultado": resultado})


@app.route('/api/desconto')
def desconto():
    # Dark launch: a rota existe no container, mas so responde com a flag on
    if not feature_desconto_ativa():
        return jsonify({"erro": "Funcionalidade indisponivel"}), 404

    try:
        preco = float(request.args.get('preco'))
    except (TypeError, ValueError):
        return jsonify({
            "erro": "Informe um preco numerico. Ex: ?preco=100"
        }), 400

    if preco < 0:
        return jsonify({"erro": "O preco nao pode ser negativo"}), 400

    preco_final = round(preco * (1 - DESCONTO_PERCENTUAL / 100), 2)
    return jsonify({
        "preco_original": preco,
        "desconto_percentual": DESCONTO_PERCENTUAL,
        "preco_final": preco_final,
    })


if __name__ == '__main__':
    # Host e debug vem do ambiente: nada de debug=True nem 0.0.0.0 fixos
    # no codigo (o Bandit acusa os dois). O Dockerfile define
    # FLASK_HOST=0.0.0.0.
    app.run(
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    ) 

import subprocess

def falha_bandit():
    subprocess.Popen("ls", shell=True)
