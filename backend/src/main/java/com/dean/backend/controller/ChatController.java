package com.dean.backend.controller;

import com.dean.backend.dto.AskRequest;
import com.dean.backend.dto.AskResponse;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/chat")
public class ChatController {
    
    @PostMapping("/ask")
    public AskResponse ask(@RequestBody AskRequest request) {
        String question = request.getQuestion();
        String answer = "질문을 잘 받았습니다: " + question;

        return new AskResponse(answer);
    }
}
