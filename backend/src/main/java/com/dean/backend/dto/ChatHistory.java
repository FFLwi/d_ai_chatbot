package com.dean.backend.dto;

import java.time.LocalDateTime;

public class ChatHistory {
    private Long id;
    private String question;
    private String answer;
    private LocalDateTime createdAt;

    public ChatHistory(){

    }

    public Long getId(){
        return id;
    }

    public void setId(Long id){
        this.id = id ;
    }
    public String getQuestion(){
        return question;
    }
    public void setQuestion(String question){
        this.question = question;
    }
    public String getAnswer(){
        return answer;
    }
    public void setAnswer(String answer){
        this.answer = answer;
    }

    public LocalDateTime getCreatedAt(){
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt){
        this.createdAt = createdAt;
    }
}
