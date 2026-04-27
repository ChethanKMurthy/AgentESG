export type Company = {
  company_id: number;
  company_name: string;
  country?: string | null;
  eu_member_state?: string | null;
  region?: string | null;
  sector?: string | null;
  subsector?: string | null;
  industry?: string | null;
  revenue_usd?: number | null;
  total_assets_usd?: number | null;
  employees?: number | null;
  entity_type?: string | null;
  listing_status?: string | null;
  stock_symbol?: string | null;
  fiscal_year?: number | null;
  currency?: string | null;
  company_size_band?: string | null;
  csrd_applicable?: boolean | null;
};

export type CompanyListResponse = {
  total: number;
  items: Company[];
  limit: number;
  offset: number;
};

export type ESGMetric = {
  company_id: number;
  year: number;
  sector?: string | null;
  country?: string | null;
  scope_1_emissions_tco2e?: number | null;
  scope_2_emissions_tco2e?: number | null;
  scope_3_emissions_tco2e?: number | null;
  energy_consumption_mwh?: number | null;
  renewable_energy_percent?: number | null;
  water_usage_m3?: number | null;
  waste_generated_tons?: number | null;
  waste_recycled_percent?: number | null;
  employee_count?: number | null;
  female_employee_ratio?: number | null;
  board_independence_percent?: number | null;
  incident_count?: number | null;
  esg_score?: number | null;
};

export type RuleResult = {
  rule_id: string;
  category: string;
  severity: "info" | "low" | "medium" | "high" | "critical" | string;
  triggered: boolean;
  message: string;
  citations?: string[];
};

export type Citation = {
  index: number;
  chunk_id: string;
  source: string;
  score: number;
  snippet: string;
};

export type FullAnalysisResponse = {
  company_id: number;
  company?: Company | null;
  metrics?: ESGMetric | null;
  rule_results: RuleResult[];
  rule_summary: Record<string, number>;
  citations: Citation[];
  report?: string | null;
  trace: {
    agent: string;
    status: string;
    duration_ms: number;
    output_summary?: Record<string, unknown>;
    error?: string | null;
  }[];
  errors: string[];
  request_id?: string | null;
};

export type PeerStats = {
  n: number;
  min: number | null;
  mean: number | null;
  median: number | null;
  p25: number | null;
  p75: number | null;
  max: number | null;
  stdev: number | null;
};

export type BenchmarkStat = {
  metric: string;
  direction: "higher" | "lower" | string;
  value: number | null;
  peer_stats: PeerStats;
  percentile_rank: number | null;
  delta_vs_median: number | null;
  status: "leader" | "peer" | "laggard" | "unknown" | string;
};

export type CompareResponse = {
  company_id: number;
  year: number | null;
  peer_scope: string;
  peer_count: number;
  benchmarks: Record<string, BenchmarkStat>;
  composite_score: number | null;
  composite_percentile_rank: number | null;
  pillar_scores: {
    environment: number | null;
    social: number | null;
    governance: number | null;
  };
  derived_composite: number | null;
};

export type Gap = {
  id: string;
  category: string;
  metric?: string | null;
  severity: string;
  current?: number | null;
  target?: number | null;
  evidence: string;
  citations: string[];
  source: "rule" | "benchmark" | string;
};

export type RoadmapDriver = {
  kind: "rule" | "benchmark" | string;
  identifier: string;
  severity: string;
  weight: number;
  description: string;
  metric?: string | null;
  current?: number | null;
  target?: number | null;
  citations: string[];
};

export type RoadmapExplanation = {
  drivers: RoadmapDriver[];
  priority_factors: Record<string, number | string | boolean>;
  horizon_rationale: string;
  methodology: string;
  narrative?: string | null;
};

export type RoadmapItem = {
  id: string;
  title: string;
  description: string;
  category: string;
  severity: string;
  priority: number;
  horizon: string;
  actions: string[];
  kpis: string[];
  evidence: string;
  citations: string[];
  gap_ids: string[];
  confidence: string;
  explanation: RoadmapExplanation;
};

export type RoadmapResponse = {
  company_id: number;
  year: number | null;
  horizon_months: number;
  gaps: Gap[];
  items: RoadmapItem[];
  summary: Record<string, number>;
};

export type CopilotQueryResponse = {
  answer: string;
  citations: Citation[];
  request_id?: string | null;
  model?: string | null;
  retrieved: number;
  used_llm: boolean;
  company_id?: number | null;
};

export type BriefingFinding = {
  severity: string;
  text: string;
  citation_indexes: number[];
};

export type CopilotBriefResponse = {
  headline: string;
  verdict: string;
  summary: string;
  findings: BriefingFinding[];
  confidence: string;
  confidence_reason?: string | null;
  citations: Citation[];
  company_id?: number | null;
  model?: string | null;
  used_llm: boolean;
};

export type RAGStats = {
  ready: boolean;
  documents?: number;
  chunks?: number;
  embedding_model?: string;
  dim?: number;
};

export type DisclosureUploadResponse = {
  company_id: number;
  company_name: string;
  year: number;
  filename: string;
  page_count: number;
  text_chars: number;
  created: boolean;
  extracted_company: Record<string, any>;
  extracted_metrics: Record<string, any>;
  missing_metrics: string[];
  extraction_notes?: string | null;
  used_llm: boolean;
  model?: string | null;
};
