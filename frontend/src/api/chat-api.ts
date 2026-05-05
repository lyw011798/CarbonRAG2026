import type { ApiChatMessage, ChatRequest, ChatResponse } from "../types/chat";

const CHAT_PATH = "/chat";
const SKILL_PATH = "/skill";

export class ChatApiError extends Error {
  readonly status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ChatApiError";
    this.status = status;
  }
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const isApiChatMessage = (value: unknown): value is ApiChatMessage =>
  isRecord(value) &&
  (value.role === "assistant" || value.role === "user") &&
  typeof value.content === "string" &&
  value.content.trim().length > 0;

type SkillResponse = {
  filename: string;
  contentType: string;
  content: string;
};

const isSkillResponse = (value: unknown): value is SkillResponse =>
  isRecord(value) &&
  typeof value.filename === "string" &&
  value.filename.trim().length > 0 &&
  typeof value.contentType === "string" &&
  value.contentType.trim().length > 0 &&
  typeof value.content === "string";

const getEndpoint = (API_PATH: string): string => {
  const apiBaseUrl = import.meta.env.VITE_CHAT_API_BASE_URL?.trim();

  if (!apiBaseUrl) {
    return API_PATH;
  }

  return `${apiBaseUrl.replace(/\/+$/, "")}${API_PATH}`;
};

const readErrorDetail = async (response: Response): Promise<string> => {
  try {
    const body = await response.json();

    if (isRecord(body) && typeof body.error === "string" && body.error.trim()) {
      return body.error.trim();
    }

    if (
      isRecord(body) &&
      typeof body.message === "string" &&
      body.message.trim()
    ) {
      return body.message.trim();
    }
  } catch (error) {
    if (error instanceof SyntaxError) {
      return (
        response.statusText ||
        "The server returned an unreadable error response."
      );
    }

    throw new ChatApiError("The chat error response could not be read.");
  }

  return response.statusText || "The server returned an error response.";
};

export const sendChatMessage = async (
  messages: ApiChatMessage[],
  signal?: AbortSignal,
): Promise<ApiChatMessage> => {
  const requestBody: ChatRequest = { messages };

  try {
    const response = await fetch(getEndpoint(CHAT_PATH), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
      signal,
    });

    if (!response.ok) {
      const detail = await readErrorDetail(response);
      throw new ChatApiError(
        `Chat request failed (${response.status}): ${detail}`,
        response.status,
      );
    }

    const body: unknown = await response.json();

    if (!isRecord(body) || !isApiChatMessage(body.message)) {
      throw new ChatApiError(
        "The chat response could not be read because it did not include a valid assistant message.",
      );
    }

    const chatResponse: ChatResponse = { message: body.message };

    if (chatResponse.message.role !== "assistant") {
      throw new ChatApiError(
        "The chat response could not be read because the returned role was not assistant.",
      );
    }

    return chatResponse.message;
  } catch (error) {
    if (error instanceof ChatApiError) {
      throw error;
    }

    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ChatApiError(
        "The chat request was cancelled before it completed.",
      );
    }

    throw new ChatApiError(
      "Unable to reach the chat API. Check your connection and try again.",
    );
  }
};

export const summarizeConversation = async (
  messages: ApiChatMessage[],
  signal?: AbortSignal,
): Promise<void> => {
  const requestBody: ChatRequest = { messages };

  try {
    const response = await fetch(getEndpoint(SKILL_PATH), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
      signal,
    });

    if (!response.ok) {
      const detail = await readErrorDetail(response);
      throw new ChatApiError(
        `Summary request failed (${response.status}): ${detail}`,
        response.status,
      );
    }

    const body: unknown = await response.json();

    if (!isSkillResponse(body)) {
      throw new ChatApiError(
        "The summary response could not be read because it did not include a valid downloadable payload.",
      );
    }

    const blob = new Blob([body.content], { type: body.contentType });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.style.display = "none";
    link.href = url;
    link.download = body.filename;
    document.body.appendChild(link);

    link.click();

    window.URL.revokeObjectURL(url);
    document.body.removeChild(link);
  } catch (error) {
    if (error instanceof ChatApiError) {
      throw error;
    }

    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ChatApiError(
        "The summary request was cancelled before it completed.",
      );
    }

    throw new ChatApiError(
      "Unable to reach the summary API. Check your connection and try again.",
    );
  }
};
