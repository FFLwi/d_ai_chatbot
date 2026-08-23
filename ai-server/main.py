from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
#from langchain_openai import ChatOpenAI

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import math
from langchain_chroma import Chroma

load_dotenv()

app = FastAPI()

#llm = ChatOpenAI(model="gpt-4o-mini")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)
# RAG에서 문장/Chunk를 숫자 Vector로 변환하기 위한 Embedding 모델
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)
# =========================
# 1. 일반 답변용 Prompt
# =========================
answer_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            너는 친절한 AI 도우미다.
            답변은 반드시 한국어로 작성한다.
            답변은 간결하고 이해하기 쉽게 작성한다.
            """
        ),
        (
            "human",
            "{question}"
        )
    ]
)
# 일반 답변용 Parser
# AIMessage -> str 로 변환한다.
answer_parser = StrOutputParser()
# 일반 답변용 Chain
# 질문 -> PromptTemplate -> Gemini -> 문자열 답변
answer_chain = answer_prompt_template | llm | answer_parser


# =========================
# 2. 질문 분석용 Prompt
# =========================
analysis_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            너는 사용자의 질문을 분석하는 AI다.

            반드시 아래 JSON 형식으로만 답변해라.
            설명 문장이나 마크다운은 붙이지 마라.

            {{
              "topic": "질문의 핵심 주제",
              "difficulty": "easy 또는 medium 또는 hard",
              "keywords": ["키워드1", "키워드2", "키워드3"],
              "summary": "질문을 한 문장으로 요약"
            }}
            """
        ),
        (
            "human",
            "{question}"
        )
    ]
)


# 질문 분석용 Parser
# AIMessage -> dict 로 변환한다.
analysis_parser = JsonOutputParser()


# 질문 분석용 Chain
# 질문 -> PromptTemplate -> Gemini -> JSON(dict)
analysis_chain = analysis_prompt_template | llm | analysis_parser
# =========================
# 3. RAG 답변용 Prompt / Chain
# =========================

rag_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            너는 주어진 참고자료를 기반으로 답변하는 AI다.

            아래 참고자료를 우선적으로 사용해서 답변해라.
            참고자료에 없는 내용은 추측하지 말고
            알 수 없다고 답변해라.

            참고자료:
            {context}
            """
        ),
        (
            "human",
            "{question}"
        )
    ]
)

# RAG도 최종 답변은 문자열로 받을 것이므로
# StrOutputParser 사용
rag_parser = StrOutputParser()

# context + question
#      ↓
# PromptTemplate
#      ↓
# Gemini
#      ↓
# 문자열
rag_chain = rag_prompt_template | llm | rag_parser


# =========================
# Request / Response DTO
# =========================
class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str

class AnalyzeResponse(BaseModel):
    topic: str
    difficulty: str
    keywords: list[str]
    summary: str

@app.get("/hello")
def hello():
    return {"message": "hello fastapi"}
# =========================
# -. rag 확인용 
# =========================
@app.get("/ai/documents")
def get_documents():
    try:
        chunks = load_and_split_documents()

        return {
            "chunk_count": len(chunks),
            "chunks": [
                {
                    "index": index,
                    "content": chunk.page_content,
                    "metadata": chunk.metadata
                }
                for index, chunk in enumerate(chunks)
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================
# 1. 일반 답변 API
# =========================
@app.post("/ai/ask", response_model=AskResponse)
def ask(request: AskRequest):
    try:
        answer = answer_chain.invoke(
            {
                "question": request.question
            }
        )

        return AskResponse(
            answer=answer
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
# =========================
# 2. 질문 분석 API
# =========================
@app.post("/ai/analyze", response_model=AnalyzeResponse)
def analyze(request: AskRequest):
    try:
        result = analysis_chain.invoke(
            {
                "question": request.question
            }
        )

        return AnalyzeResponse(
            **result
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
# =========================
# 3. RAG 1단계: 문서 로딩 + 분할
# =========================

# 현재 main.py 파일 위치를 기준으로 docs/company_info.txt 경로를 잡는다.
# 이렇게 하면 터미널 실행 위치가 달라도 경로 문제가 줄어든다.
BASE_DIR = Path(__file__).resolve().parent
DOCUMENT_PATH = BASE_DIR / "docs" / "company_info.txt"
# =========================
# Vector Store 설정
# =========================

# Embedding Vector를 실제로 저장할 로컬 폴더
VECTOR_DB_PATH = BASE_DIR / "chroma_db"


# Chroma Vector Store 생성
#
# 중요:
# 여기서는 아직 문서를 Embedding하지 않는다.
# Vector Store라는 저장 공간만 준비한다.
#
# persist_directory를 지정했기 때문에
# 벡터가 로컬 디스크에 저장된다.
vector_store = Chroma(
    collection_name="company_info",
    embedding_function=embeddings,
    persist_directory=str(VECTOR_DB_PATH)
)


# Vector Store를 Retriever로 변환
#
# Retriever 역할:
#
# 질문
#   ↓
# Vector Store 검색
#   ↓
# 관련 Document TOP 2 반환
#
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 2
    }
)

def load_and_split_documents():
    """
    docs/company_info.txt 파일을 읽고,
    LangChain Document 객체 목록을 Chunk 단위로 나누어 반환
    """

    # 1. TextLoader
    # 텍스트 파일을 읽어서 LangChain Document 객체로 변환한다.
    # 반환값은 list[Document] 형태다.
    loader = TextLoader(
        file_path=str(DOCUMENT_PATH),
        encoding="utf-8"
    )

    documents = loader.load()

    # 2. TextSplitter
    # 긴 문서를 검색하기 좋은 작은 조각으로 나눈다.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=150,
        chunk_overlap=30,
        length_function=len
    )

    # Document 목록을 Chunk Document 목록으로 변환한다.
    chunks = text_splitter.split_documents(documents)

    return chunks

# =========================
# 4-1. Vector Store에 문서 저장
# =========================
def save_documents_to_vector_store():

    # 1. 문서 읽기 + Chunk 분할
    chunks = load_and_split_documents()

    # Chunk마다 고정된 ID 생성
    #
    # 예:
    # company_info_0
    # company_info_1
    # company_info_2
    ids = [
        f"company_info_{index}"
        for index in range(len(chunks))
    ]

    # Document를 Vector Store에 저장한다.
    #
    # 내부적으로:
    #
    # Chunk
    #   ↓
    # Embedding
    #   ↓
    # Vector
    #   ↓
    # Chroma 저장
    #
    vector_store.add_documents(
        documents=chunks,
        ids=ids
    )

    return len(chunks)

# =========================
# 4. RAG 2단계: Chunk Embedding
# =========================
def embed_chunks():

    # 기존 함수로 문서를 Chunk 단위로 가져온다.
    chunks = load_and_split_documents()

    # Document 객체에서 실제 텍스트만 꺼낸다.
    chunk_texts = [
        chunk.page_content
        for chunk in chunks
    ]

    # 여러 Chunk 문자열을 Vector로 변환한다.
    chunk_vectors = embeddings.embed_documents(
        chunk_texts
    )

    # 원본 Chunk와 변환된 Vector를 같이 반환
    return chunks, chunk_vectors


# =========================
# Embedding 결과 확인용 API
# =========================
@app.get("/ai/embeddings")
def get_embeddings():
    try:

        chunks, chunk_vectors = embed_chunks()

        return {
            "chunk_count": len(chunks),
            "embeddings": [
                {
                    "index": index,
                    "content": chunks[index].page_content,

                    # Vector가 몇 차원인지 확인
                    "vector_size": len(chunk_vectors[index]),

                    # Vector 전체는 너무 길어서 앞 10개만 보여준다.
                    "vector_preview": chunk_vectors[index][:10]
                }
                for index in range(len(chunks))
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
# =========================
# 5. RAG 3단계: Vector 유사도 계산
# =========================
def cosine_similarity(vector_a, vector_b):

    # 두 Vector의 내적
    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    # vector_a의 길이
    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    # vector_b의 길이
    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    # 0으로 나누는 것 방지
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    # Cosine Similarity 반환
    return dot_product / (magnitude_a * magnitude_b)

def search_similar_chunks(question: str, top_k: int = 2):

    # 1. 기존 문서를 Chunk로 만들고 Embedding
    chunks, chunk_vectors = embed_chunks()

    # 2. 사용자의 질문도 Embedding
    question_vector = embeddings.embed_query(
        question
    )

    results = []

    # 3. 질문 Vector와 모든 Chunk Vector를 비교
    for index, chunk_vector in enumerate(chunk_vectors):

        similarity = cosine_similarity(
            question_vector,
            chunk_vector
        )

        results.append(
            {
                "index": index,
                "content": chunks[index].page_content,
                "similarity": similarity
            }
        )

    # 4. 유사도가 높은 순서대로 정렬
    results.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    # 5. 상위 top_k개만 반환
    return results[:top_k]


# =========================
# 유사 Chunk 검색 확인용 API
# =========================
@app.post("/ai/search")
def search_chunks(request: AskRequest):
    try:

        results = search_similar_chunks(
            question=request.question,
            top_k=2
        )

        return {
            "question": request.question,
            "results": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
# # =========================
# # 6. RAG 실제 답변 API -  OLD
# # =========================
# @app.post("/ai/rag", response_model=AskResponse)
# def rag_ask(request: AskRequest):
#     try:

#         # 1. 질문과 유사한 Chunk TOP 2 검색
#         retrieved_chunks = search_similar_chunks(
#             question=request.question,
#             top_k=2
#         )

#         # 2. 검색된 Chunk의 content만 꺼내서
#         # 하나의 참고자료(context) 문자열로 합친다.
#         context = "\n\n".join(
#             item["content"]
#             for item in retrieved_chunks
#         )

#         # 3. 질문 + 검색된 참고자료를 RAG Chain에 전달
#         answer = rag_chain.invoke(
#             {
#                 "question": request.question,
#                 "context": context
#             }
#         )

#         # 4. 최종 답변 반환
#         return AskResponse(
#             answer=answer
#         )

#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=str(e)
#         )

# =========================
# 6. Vector Store + Retriever RAG API
# =========================
@app.post("/ai/rag", response_model=AskResponse)
def rag_ask(request: AskRequest):

    try:

        # 1. Retriever에게 질문 전달
        #
        # 내부적으로:
        #
        # 질문
        # ↓
        # Embedding
        # ↓
        # Vector Store
        # ↓
        # 관련 Document TOP 2
        #
        retrieved_docs = retriever.invoke(
            request.question
        )


        # 2. 검색된 Document의 실제 내용만
        # context 문자열로 합친다.
        context = "\n\n".join(
            doc.page_content
            for doc in retrieved_docs
        )


        # 3. 질문 + 검색된 참고자료를 Gemini에게 전달
        answer = rag_chain.invoke(
            {
                "question": request.question,
                "context": context
            }
        )


        # 4. 최종 답변 반환
        return AskResponse(
            answer=answer
        )


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================
# Vector Store 문서 등록 API
# =========================
@app.post("/ai/index")
def index_documents():

    try:

        chunk_count = save_documents_to_vector_store()

        return {
            "message": "Vector Store 저장 완료",
            "chunk_count": chunk_count
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
# =========================
# Retriever 검색 확인 API
# =========================
@app.post("/ai/vector-search")
def vector_search(request: AskRequest):

    try:

        # Retriever에게 질문 전달
        #
        # 질문
        # ↓
        # 질문 Embedding
        # ↓
        # Vector Store 검색
        # ↓
        # 관련 Document TOP 2
        retrieved_docs = retriever.invoke(
            request.question
        )

        return {
            "question": request.question,

            "results": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }

                for doc in retrieved_docs
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )