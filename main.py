from fastapi import FastAPI
from database import create_tables, SessionLocal
from controller import evento_controller, participante_controller, inscricao_controller, relatorio_controller
from controller import usuario_controller, auth_controller
from service.usuario_service import criar_admin_inicial

# Criar tabelas no banco de dados SQLite na inicialização
create_tables()

# Criar o administrador inicial (se ADMIN_EMAIL e ADMIN_SENHA estiverem definidos)
db = SessionLocal()
try:
    criar_admin_inicial(db)
finally:
    db.close()

app = FastAPI(
    title="API de Gerenciamento de Eventos Acadêmicos",
    description="APS 4 - Autenticação e Segurança com JWT, hash de senhas e perfis de acesso",
    version="4.0.0"
)

# Inclusão dos roteadores (controllers)
app.include_router(auth_controller.router)
app.include_router(usuario_controller.router)
app.include_router(evento_controller.router)
app.include_router(participante_controller.router)
app.include_router(inscricao_controller.router)
app.include_router(relatorio_controller.router)

@app.get("/", tags=["Root"])
def root():
    return {
        "mensagem": "API de Gestão de Eventos Acadêmicos - APS 4 rodando com sucesso!",
        "documentacao": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
