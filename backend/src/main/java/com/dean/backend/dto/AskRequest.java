package com.dean.backend.dto;

public class AskRequest {

    private String question;
    private String conversationId;
    private String history;


    public AskRequest() {
    }

    public AskRequest(String question) {
        this.question = question;
    
    }

    public String getQuestion() {
        return question;
    }

    public void setQuestion(String question) {
        this.question = question;
    }

    public String getConversationId() {
    return conversationId;
    }

    public void setConversationId(String conversationId) {
    this.conversationId = conversationId;
    }

    public String getHistory() {
    return history;
}

    public void setHistory(String history) {
        this.history = history;
    }


}