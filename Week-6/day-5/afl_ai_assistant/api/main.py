from fastapi import FastAPI
from api.routes import router as chat_router

app = FastAPI(
    title="AFL AI Assistant API",
    description="Enterprise-grade API for the AFL AI Assistant Capstone.",
    version="1.0.0"
)

app.include_router(chat_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
