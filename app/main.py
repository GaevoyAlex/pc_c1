from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Liberandun API",
    description="API for liberandum",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost:3000"
    ],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Главная страница API"""
    return {
        "message": "Crypto Market API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "endpoints": {
            "auth": "/auth",
            "market": "/market",
            "admin": "/admin"
        }
    }



try:
    from app.routes.auth import router as auth_router
    app.include_router(auth_router, prefix="/auth")

    from app.routes.data.markets import router as market_router
    app.include_router(market_router, prefix="/market", tags=["Market data"])



    try:
        from app.routes.admin.main_admin import router as admin_router
        app.include_router(admin_router, prefix="/admin")
        print("[INFO][APP] - Admin роуты подключены")
    except ImportError as e:
        print(f"[WARNING][APP] - Admin роуты не найдены: {e}")
        print("[INFO][APP] - Создайте файл app/routes/admin/admin.py с роутером")
    
    try:
        from app.routes.auth.password_change import password_router
        app.include_router(password_router, prefix="/auth", tags=["authentication"])
        print("[INFO][APP] - Password change роуты подключены")
    except ImportError as e:
        print(f"[WARNING][APP] - Password change роуты не найдены: {e}")

except Exception as e:
    print(f"[ERROR][APP] - Ошибка подключения роутов: {e}")
    import traceback
    traceback.print_exc()

@app.on_event("startup")
async def startup_event():
    try:
        from app.core.database.connector import get_db_connector
        connector = get_db_connector()
        
        if connector:
            system_info = connector.get_system_info()
            print(f"[INFO][APP] - Статус БД: {system_info.get('status')}")
            print(f"[INFO][APP] - Таблиц: {system_info.get('total_tables')}")
        else:
            print("[ERROR][APP] - Не удалось инициализировать базу данных")
            
    except Exception as e:
        print(f"[ERROR][APP] - Ошибка инициализации: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )