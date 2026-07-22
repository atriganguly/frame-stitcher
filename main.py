from fastapi import FastAPI
from api.router import router as stitcher_router

app = FastAPI(
    title="FrameStitcher",
    description="Independent High-Speed CFR Video Compilation & Deduplication Engine",
    version="1.0.0"
)

app.include_router(stitcher_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "FrameStitcher"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)