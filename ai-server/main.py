from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str

@app.get("/hello")
def hello():
    return {"message": "hello fastapi"}

#request = AskRequest(question="안녕?")
@app.post("/ai/ask")
def ask(request: AskRequest):
    return AskResponse(answer=f"Python AI 서버가 받은 질문:{request.question}")
