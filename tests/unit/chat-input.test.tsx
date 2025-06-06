"use client";

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ChatInput } from '@/components/chat/chat-input';

// Mock dos hooks e funções necessárias
jest.mock('@/hooks/use-textarea', () => ({
  useTextarea: () => ({
    textareaRef: { current: document.createElement('textarea') },
    value: '',
    setValue: jest.fn(),
    handleChange: jest.fn()
  })
}));

describe('ChatInput', () => {
  const mockSendMessage = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  it('renderiza o componente de entrada de chat', () => {
    render(
      <ChatInput 
        onSendMessage={mockSendMessage} 
        isLoading={false} 
        placeholder="Digite sua mensagem..." 
        maxTokens={4096}
      />
    );
    
    // Verifica se o textarea está presente
    const textarea = screen.getByPlaceholderText('Digite sua mensagem...');
    expect(textarea).toBeInTheDocument();
    
    // Verifica se o botão de enviar está presente
    const sendButton = screen.getByRole('button', { name: /enviar/i });
    expect(sendButton).toBeInTheDocument();
  });
  
  it('desabilita o botão de enviar quando está carregando', () => {
    render(
      <ChatInput 
        onSendMessage={mockSendMessage} 
        isLoading={true} 
        placeholder="Digite sua mensagem..." 
        maxTokens={4096}
      />
    );
    
    // Verifica se o botão de enviar está desabilitado
    const sendButton = screen.getByRole('button', { name: /enviar/i });
    expect(sendButton).toBeDisabled();
  });
});
