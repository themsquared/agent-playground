export interface ModelDescription {
  [modelId: string]: string;
}

export interface Providers {
  [provider: string]: ModelDescription;
}

export interface ModelsResponse {
  [provider: string]: {
    [modelId: string]: string;
  };
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface ConversationHistory {
  history: Message[];
}

export interface ActionParameter {
  description: string;
}

export interface ActionInfo {
  description: string;
  required_parameters: {
    [key: string]: string;
  };
}

export interface Actions {
  [actionName: string]: ActionInfo;
}

export interface Action {
  action: string;
  parameters: Record<string, any>;
}

export interface LLMResponse {
  content: string;
  model_used: string;
  usage: {
    prompt_tokens?: number;
    completion_tokens?: number;
    total_tokens?: number;
    total_duration?: number;
    prompt_eval_duration?: number;
    eval_duration?: number;
  };
  cost: {
    input_cost: number;
    output_cost: number;
    total_cost: number;
  };
  action_results?: string[];
}

export interface GenerateRequest {
  provider: string;
  model: string;
  prompt: string;
  temperature: number;
  max_tokens?: number;
}

export interface ActionResult {
  success: boolean;
  message: string;
  data?: any;
  error?: string;
}

export interface GenerateResponse {
  content: string;
  model_used: string;
  usage: any;
  cost: {
    input_cost: number;
    output_cost: number;
    total_cost: number;
  };
  action_results: ActionResult[];
}

export interface EvaluationResult {
  id?: string;
  provider: string;
  modelId: string;
  questionIndex: number;
  response: string;
  rank?: number;
  cost: number;
}

export interface EvaluationTest {
  id: string;
  name: string;
  created_at: string;
  questions: string[];
  total_cost: number;
  results: EvaluationResult[];
}

export interface SaveEvaluationRequest {
  name: string;
  questions: string[];
  total_cost: number;
  results: EvaluationResult[];
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string;
    borderColor?: string;
    borderWidth?: number;
  }[];
} 