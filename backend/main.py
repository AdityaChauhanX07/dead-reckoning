from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from persona.agent import ask_harold, ask_harold_stream
from vision.image_handler import analyze_clock_image

load_dotenv()

app = FastAPI(title="dead-reckoning")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


@app.post("/query")
async def query(request: QueryRequest):
    result = await ask_harold(request.question)
    return {"answer": result}


@app.post("/query/stream")
async def query_stream(request: QueryRequest):
    result = await ask_harold(request.question)
    return {"answer": result}


class ImageQueryRequest(BaseModel):
    image_base64: str
    mime_type: str = "image/jpeg"


@app.post("/query/image")
async def query_image(request: ImageQueryRequest):
    result = await analyze_clock_image(request.image_base64, request.mime_type)
    return {"answer": result}


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "harold-jennings", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
