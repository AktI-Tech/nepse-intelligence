import { useQuery, UseQueryResult } from '@tanstack/react-query';
import apiClient from '../api';

export const useLiveMarket = (): UseQueryResult<any> => {
  return useQuery({
    queryKey: ['liveMarket'],
    queryFn: () => apiClient.getLiveMarket(),
    refetchInterval: 5000,
    staleTime: 2000,
  });
};

export const useNepseIndex = (): UseQueryResult<any> => {
  return useQuery({
    queryKey: ['nepseIndex'],
    queryFn: () => apiClient.getNepseIndex(),
    refetchInterval: 5000,
    staleTime: 2000,
  });
};

export const useStock = (symbol: string) => {
  return useQuery({
    queryKey: ['stock', symbol],
    queryFn: () => apiClient.getStock(symbol),
    refetchInterval: 10000,
    staleTime: 5000,
    enabled: !!symbol,
  });
};

export const useMarketHistory = (symbol: string, limit: number = 100) => {
  return useQuery({
    queryKey: ['marketHistory', symbol, limit],
    queryFn: () => apiClient.getMarketHistory(symbol, limit),
    refetchInterval: 60000,
    staleTime: 30000,
    enabled: !!symbol,
  });
};
