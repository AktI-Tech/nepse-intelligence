import axios, { AxiosInstance } from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client: AxiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

export interface LiveMarketResponse {
  data: any;
}

export interface IndexResponse {
  data: any;
}

export const apiClient = {
  getLiveMarket: async (): Promise<LiveMarketResponse> => {
    const response = await client.get('/api/live-market');
    return response.data;
  },

  getNepseIndex: async (): Promise<IndexResponse> => {
    const response = await client.get('/api/nepse-index');
    return response.data;
  },

  getMarketHistory: async (symbol: string, limit: number = 100) => {
    const response = await client.get(`/api/market/history?symbol=${symbol}&limit=${limit}`);
    return response.data;
  },

  getStock: async (symbol: string) => {
    const response = await client.get(`/api/stocks/${symbol}`);
    return response.data;
  },

  getIndices: async () => {
    const response = await client.get('/api/indices');
    return response.data;
  },

  getHealth: async () => {
    const response = await client.get('/health');
    return response.data;
  },
};

export default apiClient;
