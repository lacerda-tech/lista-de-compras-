from fastapi import FastAPI

app = FastAPI()

produtos = [
    {"id": 1, "nome": "Arroz", "quantidade": 2, "marca": "Tio João"},
    {"id": 2, "nome": "Feijão", "quantidade": 1, "marca": "Carioca"}
]
proximo_id = 3

#ROTA DE TODOS OS ITENS/conectar a rota
@app.get("/itens")
def listar_todos():
    return produtos


@app.get("/itens/{id_produto}")
def buscar(id_produto: int):
    for item in produtos:
        if item["id"] == id_produto:
            return item
    return {"erro": "Produto não encontrado"}


@app.post("/itens")
def adicionar(nome: str, quantidade: int, marca: str):
    global proximo_id
    
    novo = {
        "id": proximo_id,
        "nome": nome,
        "quantidade": quantidade,
        "marca": marca
    }
    produtos.append(novo)
    proximo_id = proximo_id + 1
    return novo


@app.put("/itens/{id_produto}")
def atualizar(id_produto: int, quantidade: int, marca: str):
    for item in produtos:
        if item["id"] == id_produto:
            item["quantidade"] = quantidade
            item["marca"] = marca
            return item
    return {"erro": "Produto não encontrado"}


@app.delete("/itens/{id_produto}")
def deletar(id_produto: int):
    for item in produtos:
        if item["id"] == id_produto:
            produtos.remove(item)
            return {"mensagem": "Removido com sucesso"}
    return {"erro": "Produto não encontrado"}
#prcura e deleta o produto pelo numero int