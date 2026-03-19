from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, events, participations, feedback, recommendations

app = FastAPI(
    title="CampConnect API",
    description="Backend for CampConnect — student social events platform",
    version="1.0.0",
)

# ─── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(events.router)
app.include_router(participations.router)
app.include_router(feedback.router)
app.include_router(recommendations.router)


# ─── Health check & Root ───────────────────────────────────────────────────────
@app.get("/", tags=["health"])
async def root():
    return {
        "message": "Welcome to the CampConnect API!",
        "docs_url": "/docs",
        "health_check": "/health"
    }

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
