/**
 * Shared TypeScript types for the AdaptRoute-Edu frontend.
 * Mirrors the backend Pydantic response schemas.
 */

// ── Auth ──────────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
  has_profile: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

// ── Learner Profile ───────────────────────────────────────────────────────────

export type SkillLevel = "beginner" | "intermediate" | "advanced";
export type PreferredPace = "slow" | "moderate" | "fast";

export interface LearnerProfile {
  id: string;
  user_id: string;
  full_name: string;
  skill_level: SkillLevel;
  learning_goal: string;
  preferred_pace: PreferredPace;
  daily_study_time: number;
  created_at: string;
  updated_at: string;
}

// ── Roadmap ───────────────────────────────────────────────────────────────────

export type RoadmapStatus = "active" | "completed" | "paused";

export interface Topic {
  id: string;
  roadmap_id: string;
  week_number: number;
  title: string;
  description: string | null;
  order_index: number;
  is_completed: boolean;
  created_at: string;
}

export interface WeekGroup {
  week_number: number;
  theme?: string;
  topics: Topic[];
}

export interface Roadmap {
  id: string;
  user_id: string;
  title: string;
  goal: string;
  total_weeks: number;
  status: RoadmapStatus;
  created_at: string;
  topics: Topic[];
  weeks: WeekGroup[];
}

// ── Content ───────────────────────────────────────────────────────────────────

export type ContentType = "notes" | "explanation" | "example";

export interface Content {
  id: string;
  topic_id: string;
  content_type: ContentType;
  body: string;
  llm_model_used: string | null;
  generated_at: string;
}

export interface TopicContentResponse {
  topic: Topic;
  contents: Content[];
}

// ── Quiz ──────────────────────────────────────────────────────────────────────

export interface QuizOption {
  label: string;
  text: string;
}

export interface QuizQuestion {
  id: string;
  question_text: string;
  question_type: "mcq" | "coding";
  options: QuizOption[] | null;
  order_index: number;
  // correct_answer is omitted from the "during quiz" response
  // it's only included in the results response
  correct_answer?: string;
  explanation?: string;
}

export interface Quiz {
  id: string;
  topic_id: string;
  title: string;
  total_questions: number;
  pass_percentage: number;
  created_at: string;
  questions: QuizQuestion[];
}

// ── Quiz Attempt ──────────────────────────────────────────────────────────────

export interface AttemptAnswer {
  question_id: string;
  given_answer: string;
}

export interface QuizSubmitRequest {
  answers: AttemptAnswer[];
  time_taken_seconds: number;
}

export interface AttemptAnswerDetail {
  question_id: string;
  given_answer: string;
  is_correct: boolean;
  correct_answer: string;
  explanation?: string;
}

export interface QuizAttemptResult {
  id: string;
  quiz_id: string;
  score: number;
  percentage: number;
  passed: boolean;
  time_taken_seconds: number;
  attempted_at: string;
  answers: AttemptAnswerDetail[];
}

// ── Dashboard ─────────────────────────────────────────────────────────────────

export interface DashboardStats {
  completed_topics: number;
  total_topics: number;
  completion_percentage: number;
  average_quiz_score: number;
  total_quiz_attempts: number;
  last_activity: string | null;
  roadmap_status: RoadmapStatus | null;
  roadmap_title: string | null;
}

// ── Routing Telemetry ─────────────────────────────────────────────────────────

export interface ModelCapability {
  model_id: string;
  display_name: string;
  tier: string;
  reasoning_score: number;
  code_score: number;
}

export interface RoutingLogItem {
  id: string;
  task_type: string;
  selected_model: string;
  routing_policy: string;
  latency_ms: number | null;
  reward_score: number | null;
  created_at: string;
}

export interface TelemetryStats {
  active_policy: string;
  total_requests: number;
  model_distribution: Record<string, number>;
  avg_latency_ms: number;
  total_estimated_cost_usd: number;
  avg_reward_score: number;
  available_models: ModelCapability[];
  recent_logs: RoutingLogItem[];
}

// ── Knowledge Tracing ────────────────────────────────────────────────────────

export type MasteryLevel = "mastered" | "proficient" | "developing" | "struggling";

export interface TopicMasteryDetail {
  topic_id: string;
  mastery_score: number;
  mastery_level: MasteryLevel;
  attempts_count: number;
  correct_count: number;
  accuracy_pct: number;
  last_attempt_at: string | null;
}

export interface MasteryStats {
  topics_tracked: number;
  avg_mastery: number;
  mastered_count: number;
  proficient_count: number;
  developing_count: number;
  struggling_count: number;
  overall_readiness: number;
  topic_details: TopicMasteryDetail[];
}

// ── API Error ─────────────────────────────────────────────────────────────────

export interface ApiError {
  detail: string;
}
