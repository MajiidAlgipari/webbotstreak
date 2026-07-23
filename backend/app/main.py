from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import auth, friends, messages, streak, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="BotStreak API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ganti ke domain frontend saat production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(friends.router)
app.include_router(messages.router)
app.include_router(streak.router)
app.include_router(admin.router)


@app.get("/api/health")
def health():
    return {"ok": True}
