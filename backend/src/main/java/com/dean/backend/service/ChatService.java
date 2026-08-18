package com.dean.backend.service;

import com.dean.backend.dto.AnalyzeResponse;
import com.dean.backend.dto.AskRequest;
import com.dean.backend.dto.AskResponse;
import com.dean.backend.dto.ChatHistory;
import com.dean.backend.mapper.ChatHistoryMapper;

import java.util.Collections;
import java.util.List;

import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class ChatService {

    private final ChatHistoryMapper chatHistoryMapper;
    private final RestTemplate restTemplate = new RestTemplate();

    public ChatService(ChatHistoryMapper chatHistoryMapper) {
        this.chatHistoryMapper = chatHistoryMapper;
    }

    // 일반 AI 답변 요청
    // Spring Boot -> FastAPI /ai/ask 호출
    public String generateAnswer(String question) {
        try {
            String fastApiUrl = "http://127.0.0.1:8000/ai/ask";

            AskRequest requestBody = new AskRequest();
            requestBody.setQuestion(question);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<AskRequest> httpEntity = new HttpEntity<>(requestBody, headers);

            ResponseEntity<AskResponse> response = restTemplate.exchange(
                    fastApiUrl,
                    HttpMethod.POST,
                    httpEntity,
                    AskResponse.class
            );

            AskResponse responseBody = response.getBody();

            if (responseBody == null) {
                return "FastAPI 응답이 비어 있습니다.";
            }

            String answer = responseBody.getAnswer();

            ChatHistory chatHistory = new ChatHistory();
            chatHistory.setQuestion(question);
            chatHistory.setAnswer(answer);

            chatHistoryMapper.insertChatHistory(chatHistory);

            return answer;

        } catch (Exception e) {
            e.printStackTrace();
            return "AI 서버와 연결할 수 없습니다: " + e.getMessage();
        }
    }

    // 대화 이력 조회
    public List<ChatHistory> getChatHistoryList() {
        return chatHistoryMapper.selectChatHistoryList();
    }

    // 질문 분석 요청
    // Spring Boot -> FastAPI /ai/analyze 호출
    public AnalyzeResponse analyzeQuestion(String question) {
        try {
            String fastApiUrl = "http://127.0.0.1:8000/ai/analyze";

            AskRequest requestBody = new AskRequest();
            requestBody.setQuestion(question);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<AskRequest> httpEntity = new HttpEntity<>(requestBody, headers);

            ResponseEntity<AnalyzeResponse> response = restTemplate.exchange(
                    fastApiUrl,
                    HttpMethod.POST,
                    httpEntity,
                    AnalyzeResponse.class
            );

            AnalyzeResponse responseBody = response.getBody();

            if (responseBody == null) {
                AnalyzeResponse emptyResponse = new AnalyzeResponse();
                emptyResponse.setTopic("unknown");
                emptyResponse.setDifficulty("unknown");
                emptyResponse.setKeywords(Collections.emptyList());
                emptyResponse.setSummary("FastAPI 응답이 비어 있습니다.");
                return emptyResponse;
            }

            return responseBody;

        } catch (Exception e) {
            e.printStackTrace();

            AnalyzeResponse errorResponse = new AnalyzeResponse();
            errorResponse.setTopic("error");
            errorResponse.setDifficulty("unknown");
            errorResponse.setKeywords(Collections.emptyList());
            errorResponse.setSummary("AI 분석 서버와 연결할 수 없습니다: " + e.getMessage());

            return errorResponse;
        }
    }
}