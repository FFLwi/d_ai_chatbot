package com.dean.backend.mapper;

import com.dean.backend.dto.ChatHistory;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

@Mapper
public interface ChatHistoryMapper {
    void insertChatHistory(ChatHistory chatHistory);
    List<ChatHistory> selectChatHistoryList();
}