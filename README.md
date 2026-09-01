# d_ai_chatbot

## 프로젝트 개요
React - Spring Boot - FastAPI 기반 대화형 AI 웹 애플리케이션

LangChain과 Chroma Vector DB를 활용한 RAG 기능과
MySQL 기반 대화 이력 및 Conversation Memory를 구현하였다.

## Architecture

React (Vite)
    ↓
Spring Boot
    ├── MyBatis → MySQL
    │              └─ 대화 이력 저장/조회
    │
    └── REST API
          ↓
       FastAPI
          ├─ LangChain
          ├─ Retriever
          ├─ Chroma Vector DB
          └─ Gemini LLM

## 주요 기능

### 1. RAG 기반 질의응답
- 문서 Chunking
- Document / Query Embedding
- Chroma Vector DB 저장
- Retriever 기반 Vector Similarity Search
- 관련 Document Chunk 검색
- 검색 Context 기반 Gemini 답변 생성

### 2. 대화 Memory
- conversationId 기반 대화방 구분
- MySQL 질문/답변 이력 저장
- 이전 대화 조회
- History를 AI Prompt에 전달
- 연속적인 Context 기반 질의응답

### 3. 대화 이력 관리
- 전체 대화 이력 조회
- 이전 대화방 재진입
- 기존 conversationId 기반 대화 계속하기

### 4. 질문 분석
- LangChain JsonOutputParser 적용
- topic
- difficulty
- keywords
- summary
형태의 구조화 JSON 응답

## 기술 스택

Frontend
- React
- Vite

Backend
- Spring Boot
- MyBatis
- MySQL

AI Server
- Python
- FastAPI
- LangChain

AI / RAG
- Gemini
- Google Generative AI Embedding
- Chroma Vector DB
- Retriever

## 주요 API

Spring Boot
- POST /api/chat/rag
- GET /api/chat/history
- GET /api/chat/history/{conversationId}

FastAPI
- POST /ai/rag
- POST /ai/index
- POST /ai/analyze
- POST /ai/vector-search

## 향후 확장 계획
- LangGraph 기반 질문 유형 분기
- 외부 API 연동
- 사용자 문서 업로드 기반 RAG
- Streaming 응답
- Agent 기능 확장
