import axios from "axios";
import type {
  DecisionItem, DecisionSummary, Rubric, SkillRunResponse,
  CompareResult, ReviewQueueItem, JournalEntry,
} from "./types";

const api = axios.create({ baseURL: "/api" });

// ── Decisions ────────────────────────────────────────────────────────────────

export const decisions = {
  list: (params?: {
    type?: string; status?: string; priority?: string;
    search?: string; sort_by?: string;
  }) => api.get<DecisionSummary[]>("/decisions", { params }).then(r => r.data),

  get: (id: string) => api.get<DecisionItem>(`/decisions/${id}`).then(r => r.data),

  create: (data: Partial<DecisionItem> & { title: string; type: string }) =>
    api.post<DecisionItem>("/decisions", data).then(r => r.data),

  update: (id: string, data: Partial<DecisionItem>) =>
    api.patch<DecisionItem>(`/decisions/${id}`, data).then(r => r.data),

  delete: (id: string) => api.delete(`/decisions/${id}`),

  updateStatus: (id: string, status: string, rationale?: string) =>
    api.post<DecisionItem>(`/decisions/${id}/status`, { status, rationale }).then(r => r.data),

  addNote: (id: string, body: string, note_type = "General") =>
    api.post(`/decisions/${id}/notes`, { body, note_type }).then(r => r.data),

  deleteNote: (id: string, note_id: string) =>
    api.delete(`/decisions/${id}/notes/${note_id}`),
};

// ── Rubrics ───────────────────────────────────────────────────────────────────

export const rubrics = {
  list: () => api.get<Rubric[]>("/rubrics").then(r => r.data),
  get: (id: string) => api.get<Rubric>(`/rubrics/${id}`).then(r => r.data),
  create: (data: Partial<Rubric> & { name: string }) =>
    api.post<Rubric>("/rubrics", data).then(r => r.data),
  update: (id: string, data: Partial<Rubric>) =>
    api.patch<Rubric>(`/rubrics/${id}`, data).then(r => r.data),
  delete: (id: string) => api.delete(`/rubrics/${id}`),
  addFactor: (id: string, factor: { name: string; weight: number; description?: string }) =>
    api.post(`/rubrics/${id}/factors`, factor).then(r => r.data),
  deleteFactor: (id: string, factorId: string) =>
    api.delete(`/rubrics/${id}/factors/${factorId}`),
};

// ── Scoring ───────────────────────────────────────────────────────────────────

export const scoring = {
  create: (data: {
    decision_item_id: string; rubric_id: string;
    factors: { factor_name: string; factor_weight: number; factor_score: number; justification?: string }[];
    confidence_level?: string; scoring_notes?: string;
  }) => api.post("/scores", data).then(r => r.data),

  forDecision: (id: string) => api.get(`/scores/decision/${id}`).then(r => r.data),
  delete: (scoreId: string) => api.delete(`/scores/${scoreId}`),
};

// ── AI Skills ─────────────────────────────────────────────────────────────────

export const ai = {
  skills: () => api.get<{ skills: string[] }>("/ai/skills").then(r => r.data.skills),

  run: (skill_name: string, decision_item_id?: string, extra_context?: string) =>
    api.post<SkillRunResponse>("/ai/run", { skill_name, decision_item_id, extra_context })
      .then(r => r.data),

  history: (decision_id: string) =>
    api.get(`/ai/history/${decision_id}`).then(r => r.data),
};

// ── Compare ───────────────────────────────────────────────────────────────────

export const compare = {
  get: (ids: string[]) =>
    api.get<CompareResult>("/compare", { params: { ids } }).then(r => r.data),
};

// ── Review Queue ──────────────────────────────────────────────────────────────

export const reviewQueue = {
  get: () => api.get<ReviewQueueItem[]>("/review-queue").then(r => r.data),
};

// ── Journal ───────────────────────────────────────────────────────────────────

export const journal = {
  forDecision: (id: string) =>
    api.get<JournalEntry[]>(`/journal/${id}`).then(r => r.data),
  all: (limit = 50) =>
    api.get<JournalEntry[]>("/journal", { params: { limit } }).then(r => r.data),
};

// ── Health ────────────────────────────────────────────────────────────────────

export const health = {
  check: () => axios.get("/health").then(r => r.data),
};
