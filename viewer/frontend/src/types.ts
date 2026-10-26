export type TraceEvent = {
  type: "trace";
  title: string;
  detail?: string;
  path?: string;
  lineRange?: [number, number];
};

export type AnswerDeltaEvent = {
  type: "answer_delta";
  text: string;
};

export type AnswerDoneEvent = {
  type: "answer_done";
  text: string;
};

export type ErrorEvent = {
  type: "error";
  message: string;
};

export type ChatStreamEvent = TraceEvent | AnswerDeltaEvent | AnswerDoneEvent | ErrorEvent;

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  traces: TraceEvent[];
  isStreaming?: boolean;
  error?: string;
};

