import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  user_id?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  sources?: Array<{
    title: string;
    category: string;
    relevance: number;
  }>;
}

export interface KnowledgeBaseItem {
  title: string;
  content: string;
  category: string;
  tags?: string[];
}

class ApiService {
  private axiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await this.axiosInstance.post<ChatResponse>('/api/chat', request);
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  async getChatHistory(sessionId: string): Promise<{ messages: Message[] }> {
    try {
      const response = await this.axiosInstance.get(`/api/chat/history/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting chat history:', error);
      throw error;
    }
  }

  async deleteSession(sessionId: string): Promise<void> {
    try {
      await this.axiosInstance.delete(`/api/chat/session/${sessionId}`);
    } catch (error) {
      console.error('Error deleting session:', error);
      throw error;
    }
  }

  async addKnowledge(item: KnowledgeBaseItem): Promise<{ success: boolean; id: string }> {
    try {
      const response = await this.axiosInstance.post('/api/knowledge-base/add', item);
      return response.data;
    } catch (error) {
      console.error('Error adding knowledge:', error);
      throw error;
    }
  }

  async searchKnowledge(query: string, limit: number = 5): Promise<any> {
    try {
      const response = await this.axiosInstance.get('/api/knowledge-base/search', {
        params: { query, limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error searching knowledge:', error);
      throw error;
    }
  }

  async def healthCheck(): Promise<any> {
    try {
      const response = await this.axiosInstance.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }

  async get(url: string, config?: any): Promise<any> {
    return await this.axiosInstance.get(url, config);
  }

  async post(url: string, data?: any, config?: any): Promise<any> {
    return await this.axiosInstance.post(url, data, config);
  }

  async delete(url: string, config?: any): Promise<any> {
    return await this.axiosInstance.delete(url, config);
  }
}

export const apiService = new ApiService();
