import json
from datetime import datetime

ARQUIVO = "dados.json"

def carregar_dados():
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def salvar_dados(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def adicionar_dado(nome, valor):
    dados = carregar_dados()
    novo_dado = {
        "id": len(dados) + 1,
        "nome": nome,
        "valor": valor,
        "data_criacao": datetime.now().isoformat()
    }
    dados.append(novo_dado)
    salvar_dados(dados)
    return novo_dado

def listar_dados():
    return carregar_dados()

def atualizar_dado(id, nome=None, valor=None):
    dados = carregar_dados()
    for dado in dados:
        if dado["id"] == id:
            if nome is not None:
                dado["nome"] = nome
            if valor is not None:
                dado["valor"] = valor
            salvar_dados(dados)
            return dado
    return None

def deletar_dado(id):
    dados = carregar_dados()
    dados = [dado for dado in dados if dado["id"] != id]
    salvar_dados(dados)
    return True