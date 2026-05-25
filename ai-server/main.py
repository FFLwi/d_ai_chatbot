from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
#from langchain_openai import ChatOpenAI

from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

app = FastAPI()

#llm = ChatOpenAI(model="gpt-4o-mini")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str

@app.get("/hello")
def hello():
    return {"message": "hello fastapi"}

#request = AskRequest(question="안녕?")
@app.post("/ai/ask", response_model=AskResponse)
def ask(request: AskRequest):
    try:
        prompt = f"""
        너는 친절한 AI 도우미다.
        답변은 한국어로 간결하고 이해하기 쉽게 작성해라.

        사용자 질문:
        {request.question}
        """
         
        #response = llm.invoke(request.question)
        response = llm.invoke(prompt)
        return AskResponse(answer=response.content)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )