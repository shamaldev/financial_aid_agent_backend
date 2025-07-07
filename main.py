# main.py
from app.redis_client import close_redis_pool, init_redis_pool
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from router import user, auth, policies , chat, evaluations
from app.database import init_db, test_db_connection
from app.config import settings

import logging.config
from configs.logging_config  import LOG_CONFIG

from tools.llamaindex.llamaindex_config import init_embbed_model

os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project

app = FastAPI(
    title="Social Works API",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs"
)

# --- Redis startup/shutdown --------------------------------------
@app.on_event("startup")
async def on_startup():
    await init_redis_pool()

@app.on_event("shutdown")
async def on_shutdown():
    await close_redis_pool()

# --- Database ----------------------------------------------------
init_db()

# Embedding model
init_embbed_model()

# Logging 
logging.config.dictConfig(LOG_CONFIG)


#CORS ###### Adjust in production
# --- CORS --------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers -----------------------------------------------------
app.include_router(user.router,      prefix="/api/v1/users")
app.include_router(auth.router,      prefix="/api/v1")
app.include_router(policies.router, prefix="/api/v1/policies")
app.include_router(chat.router, prefix="/api/v1/chats")
app.include_router(evaluations.router, prefix="/api/v1/evaluations")


##### TEST
@app.get("/api/v1/health")
@app.get("/api/v1/healthz")
def health_check():
    return {"status": "ok"}


##### TEST
if not test_db_connection():
    raise RuntimeError("Database connection failed")








# # 1) Run at startup
# @app.on_event("startup")
# def on_startup():
#     if test_db_connection():
#         print("✅ Successfully connected to the database.")
#     else:
#         # you could also raise here to prevent the app from starting
#         print("❌ Could not connect to the database on startup.")

# # 2) Optional: expose an HTTP health‐check
# @app.get("/health/db", tags=["Health"])
# def db_health_check():
#     if test_db_connection():
#         return {"status": "database ok"}
#     raise HTTPException(status_code=503, detail="Database connection failed")