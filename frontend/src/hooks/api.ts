import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import type {
  CompanyListResponse,
  Company,
  CompareResponse,
  CopilotQueryResponse,
  DisclosureUploadResponse,
  FullAnalysisResponse,
  RAGStats,
  RoadmapResponse,
} from "../types/api";

export function useCompanies(params: {
  limit?: number;
  offset?: number;
  search?: string;
  country?: string;
  sector?: string;
  csrd_applicable?: boolean;
}) {
  return useQuery({
    queryKey: ["companies", params],
    queryFn: async () => {
      const { data } = await api.get<CompanyListResponse>("/companies", {
        params: {
          limit: params.limit ?? 50,
          offset: params.offset ?? 0,
          search: params.search || undefined,
          country: params.country || undefined,
          sector: params.sector || undefined,
          csrd_applicable: params.csrd_applicable,
        },
      });
      return data;
    },
  });
}

export function useCompany(id?: number | null) {
  return useQuery({
    queryKey: ["company", id],
    enabled: !!id,
    queryFn: async () => {
      const { data } = await api.get<Company>(`/companies/${id}`);
      return data;
    },
  });
}

export function useAnalysisFull(id?: number | null, query?: string) {
  return useQuery({
    queryKey: ["analysis-full", id, query],
    enabled: !!id,
    queryFn: async () => {
      const { data } = await api.post<FullAnalysisResponse>("/analysis/full", {
        company_id: id,
        query: query || null,
        top_k: 5,
        include_rag: true,
        include_report: true,
      });
      return data;
    },
  });
}

export function useCompare(id?: number | null, peerScope = "sector") {
  return useQuery({
    queryKey: ["compare", id, peerScope],
    enabled: !!id,
    queryFn: async () => {
      const { data } = await api.post<CompareResponse>("/analysis/compare", {
        company_id: id,
        peer_scope: peerScope,
      });
      return data;
    },
  });
}

export function useRoadmap(id?: number | null, horizonMonths = 12) {
  return useQuery({
    queryKey: ["roadmap", id, horizonMonths],
    enabled: !!id,
    queryFn: async () => {
      const { data } = await api.post<RoadmapResponse>("/analysis/roadmap", {
        company_id: id,
        horizon_months: horizonMonths,
      });
      return data;
    },
  });
}

export function useRagStats() {
  return useQuery({
    queryKey: ["rag-stats"],
    queryFn: async () => {
      const { data } = await api.get<RAGStats>("/copilot/stats");
      return data;
    },
    staleTime: 60_000,
  });
}

export function useCopilotQuery() {
  return useMutation({
    mutationFn: async (payload: { query: string; company_id?: number | null }) => {
      const { data } = await api.post<CopilotQueryResponse>("/copilot/query", {
        query: payload.query,
        company_id: payload.company_id ?? undefined,
        top_k: 5,
      });
      return data;
    },
  });
}

export function useUploadDisclosure() {
  return useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData();
      form.append("file", file);
      const { data } = await api.post<DisclosureUploadResponse>(
        "/upload/disclosure",
        form,
        { timeout: 180_000 }
      );
      return data;
    },
  });
}

export function useCopilotBrief() {
  return useMutation({
    mutationFn: async (payload: { query: string; company_id?: number | null }) => {
      const { data } = await api.post(
        "/copilot/brief",
        {
          query: payload.query,
          company_id: payload.company_id ?? undefined,
          top_k: 5,
        }
      );
      return data;
    },
  });
}
