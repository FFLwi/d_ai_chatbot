package com.dean.backend.service;

import org.springframework.stereotype.Service;

@Service
public class ChatService {

    public String generateAnswer(String question){

        return "질문을 잘 받았습니다: " + question;
    }
    
}
