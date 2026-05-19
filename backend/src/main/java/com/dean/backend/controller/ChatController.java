package com.dean.backend.controller;

import com.dean.backend.dto.AskRequest;
import com.dean.backend.dto.AskResponse;
import com.dean.backend.dto.ChatHistory;
import com.dean.backend.service.ChatService;

import java.util.List;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/chat")
public class ChatController {
    private final ChatService chatService;

    public ChatController(ChatService chatService){
        this.chatService = chatService;
    }

    @PostMapping("/ask")
    public AskResponse ask(@RequestBody AskRequest request) {
        String question = request.getQuestion();
        String answer = chatService.generateAnswer(question);

        return new AskResponse(answer);
    }

    @GetMapping("/history")
    public List<ChatHistory> getHistory() {
        return chatService.getChatHistoryList();
    }
}
