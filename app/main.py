from fastapi import FastAPI
from app.configuration.database import db, client
from app.routers import book_router, library_router, user_router, category_router

app = FastAPI(
    title="Library System API",
    version="1.0",
    description="API para gerenciamento de bibliotecas, livros e usuários.",
    docs_url="/swagger",
)

# -- ROUTERS --
# app.include_router(book_router.router, prefix="/books", tags=["Books"])
# app.include_router(library_router.router, prefix="/libraries", tags=["Libraries"])
# app.include_router(user_router.router, prefix="/users", tags=["Users"])
app.include_router(category_router.router, prefix="/categories", tags=["Categories"])

@app.on_event("startup")
async def startup_db_client():
    print("✅ Conectado ao MongoDB!")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    print("🛑 Conexão com MongoDB encerrada!")

# Root path test
@app.get("/")
async def root():
    return {"message": "🚀 Bem-vindo à API de Biblioteca!"}