package com.dean.backend.controller;

import com.dean.backend.dto.AnalyzeResponse;

import com.dean.backend.dto.AskRequest;
import com.dean.backend.dto.AskResponse;

import com.dean.backend.dto.ChatHistory;
import com.dean.backend.service.ChatService;
import java.util.Collections;
import java.util.List;

import org.springframework.web.bind.annotation.*;
@CrossOrigin(origins = "http://localhost:5173")
@RestController
@RequestMapping("/api/chat")
public class ChatController {
    private final ChatService chatService;

    public ChatController(ChatService chatService){
        this.chatService = chatService;
    }

     // 일반 AI 답변 요청
    // POST http://localhost:8080/api/chat/ask
    @PostMapping("/ask")
    public AskResponse ask(@RequestBody AskRequest request) {
        String question = request.getQuestion();
        String answer = chatService.generateAnswer(question);

        return new AskResponse(answer);
    }

    // 질문 분석 요청
    // POST http://localhost:8080/api/chat/analyze
    @PostMapping("/analyze")
    public AnalyzeResponse analyze(@RequestBody AskRequest request) {
        return chatService.analyzeQuestion(request.getQuestion());
    }
    @GetMapping("/history")
    public List<ChatHistory> getHistory() {
        return chatService.getChatHistoryList();
    }

    @PostMapping("/rag")
    public AskResponse rag(@RequestBody AskRequest request) {

    String answer =
            chatService.generateRagAnswer(
                    request.getQuestion()
            );

    return new AskResponse(answer);
}

}
