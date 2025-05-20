import * as React from "react";

// Exportação dos componentes de chat
export const ChatInterface = React.lazy(() => import("./chat-interface").then(module => ({ default: module.default || module.ChatInterface })));
export const ChatInput = React.lazy(() => import("./chat-input").then(module => ({ default: module.default || module.ChatInput })));
export const ChatMessage = React.lazy(() => import("./chat-message").then(module => ({ default: module.default || module.ChatMessage })));
export const ConversationHeader = React.lazy(() => import("./conversation-header").then(module => ({ default: module.default || module.ConversationHeader })));
export const ConversationSidebar = React.lazy(() => import("./conversation-sidebar").then(module => ({ default: module.default || module.ConversationSidebar })));
export const MessagesArea = React.lazy(() => import("./messages-area").then(module => ({ default: module.default || module.MessagesArea })));
export const ModelSelector = React.lazy(() => import("./model-selector").then(module => ({ default: module.default || module.ModelSelector })));

// Exportação padrão para facilitar importações
const ChatComponents = {
  ChatInterface,
  ChatInput,
  ChatMessage,
  ConversationHeader,
  ConversationSidebar,
  MessagesArea,
  ModelSelector
};

export default ChatComponents;
