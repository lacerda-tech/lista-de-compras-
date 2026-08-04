from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta

app = FastAPI()
security = HTTPBearer()

# Config do JW
JWT_SECRET = "sua_chave_secreta_super_segura"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# (user1 / 124)
users_db = {
    "user1": {
        "username": "user1",
        "password": "$argon2id$v=19$m=65536,t=3,p=4$..." 
    }
}

# CADASTRADO
users_db["user1"] = {
    "username": "user1",
    "password": pwd_context.hash("124")
}

produtos = [
    {"id": 1, "nome": "Arroz", "quantidade": 2, "marca": "Tio João"},
    {"id": 2, "nome": "Feijão", "quantidade": 1, "marca": "Carioca"}
]
proximo_id = 3

class UserSchema(BaseModel):
    username: str
    password: str

# Rota de Cadastro
@app.post("/register")
def register(user: UserSchema):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Usuário já cadastrado.")
    hashed_password = pwd_context.hash(user.password)
    users_db[user.username] = {"username": user.username, "password": hashed_password}
    return {"message": "Usuário registrado com sucesso!"}

# Rota de Login 
@app.post("/login")
def login(user: UserSchema):
    db_user = users_db.get(user.username)
    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos.")
    
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload = {"sub": user.username, "exp": expiration}
    token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
    
    return {"access_token": token, "token_type": "bearer"}

# Validador do Token JWT
def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Token inválido ou expirado.")

# Rotas de Produtos (Protegidas com JWT)
@app.get("/itens")
def listar_todos(username: str = Depends(verify_jwt)):
    return produtos

@app.get("/itens/{id_produto}")
def buscar(id_produto: int, username: str = Depends(verify_jwt)):
    for item in produtos:
        if item["id"] == id_produto:
            return item
    return {"erro": "Produto não encontrado"}

@app.post("/itens")
def adicionar(nome: str, quantidade: int, marca: str, username: str = Depends(verify_jwt)):
    global proximo_id
    novo = {
        "id": proximo_id,
        "nome": nome,
        "quantidade": quantidade,
        "marca": marca
    }
    produtos.append(novo)
    proximo_id += 1
    return novo

@app.put("/itens/{id_produto}")
def atualizar(id_produto: int, nome: str, quantidade: int, marca: str, username: str = Depends(verify_jwt)):
    for item in produtos:
        if item["id"] == id_produto:
            item["nome"] = nome
            item["quantidade"] = quantidade
            item["marca"] = marca
            return item
    return {"erro": "Produto não encontrado"}

@app.delete("/itens/{id_produto}")
def deletar(id_produto: int, username: str = Depends(verify_jwt)):
    for item in produtos:
        if item["id"] == id_produto:
            produtos.remove(item)
            return {"mensagem": "Removido com sucesso"}
    return {"erro": "Produto não encontrado"}