package com.dean.backend.service;

import com.dean.backend.dto.AskRequest;
import com.dean.backend.dto.AskResponse;
import com.dean.backend.mapper.ChatHistoryMapper;

import java.util.List;

import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import com.dean.backend.dto.ChatHistory;
import com.dean.backend.mapper.ChatHistoryMapper;

@Service
public class ChatService {
    private final ChatHistoryMapper chatHistoryMapper;
    private final RestTemplate restTemplate = new RestTemplate();

    public ChatService(ChatHistoryMapper chatHistoryMapper) {
        this.chatHistoryMapper = chatHistoryMapper;
    }

    public String generateAnswer(String question){
        try{
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

            if(responseBody == null){
                return "FastAPI 응답이 비어 있습니다.";
            }
            //return responseBody.getAnswer();
            String answer = responseBody.getAnswer();

            ChatHistory chatHistory = new ChatHistory();
            chatHistory.setQuestion(question);
            chatHistory.setAnswer(answer);

            chatHistoryMapper.insertChatHistory(chatHistory);

            return answer;

        } catch (Exception e){
            return "AI 서버와 연결할 수 없습니다.";
        }
    }

    public List<ChatHistory> getChatHistoryList() {
        return chatHistoryMapper.selectChatHistoryList();
    }
    
}
