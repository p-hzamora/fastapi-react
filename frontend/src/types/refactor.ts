import { API_URL } from "../constants";

// First, define your data models
export interface Todo {
  id: number;
  item: string;
}

export interface TodoForm {
  item: string;
}

// Define API routes using a constant map
// This serves both as runtime value AND as type source
export const API_ENDPOINTS = {
  getTodos: {
    method: 'GET',
    path: '/todo/',
    responseType: {} as Todo[],
  },
  createTodo: {
    method: 'POST',
    path: '/todo/',
    requestType: {} as TodoForm,
    responseType: {} as Todo,
  },
  getTodo: {
    method: 'GET',
    path: '/todo/{todo_id}',
    paramType: {} as { todo_id: number },
    responseType: {} as Todo,
  },
  updateTodo: {
    method: 'PATCH',
    path: '/todo/{todo_id}',
    paramType: {} as { todo_id: number },
    requestType: {} as TodoForm,
    responseType: {} as Todo,
  },
  deleteTodo: {
    method: 'DELETE',
    path: '/todo/{todo_id}',
    paramType: {} as { todo_id: number },
    responseType: {} as boolean,
  },
} as const;

// Derive types from the constant
export type ApiEndpoints = typeof API_ENDPOINTS;
export type EndpointKeys = keyof ApiEndpoints;

// Helper types to extract the properties from an endpoint
// type EndpointMethod<K extends EndpointKeys> = ApiEndpoints[K]['method'];
// type EndpointPath<K extends EndpointKeys> = ApiEndpoints[K]['path'];
type EndpointParams<K extends EndpointKeys> = ApiEndpoints[K] extends { paramType: infer P } ? P : never;
type EndpointRequest<K extends EndpointKeys> = ApiEndpoints[K] extends { requestType: infer R } ? R : never;
type EndpointResponse<K extends EndpointKeys> = ApiEndpoints[K]['responseType'];
type EndpointQuery<K extends EndpointKeys> = ApiEndpoints[K] extends { queryType: infer Q } ? Q : never;

// Helper function to replace path parameters
function replacePath(path: string, params?: Record<string, string | number>): string {
  if (!params) return path;
  
  let finalPath = path;
  for (const [key, value] of Object.entries(params)) {
    finalPath = finalPath.replace(`{${key}}`, String(value));
  }
  return finalPath;
}

// Helper function to build query string
function buildQueryString(query?: Record<string, string | number | boolean | string[]>): string {
  if (!query) return '';
  
  const params = new URLSearchParams();
  Object.entries(query).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach(v => params.append(key, String(v)));
    } else {
      params.append(key, String(value));
    }
  });
  
  const queryString = params.toString();
  return queryString ? `?${queryString}` : '';
}

// Client implementation
export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
  }

  async request<K extends EndpointKeys>(
    endpointKey: K,
    options: {
      params?: EndpointParams<K>;
      query?: EndpointQuery<K>;
      body?: EndpointRequest<K>;
    } = {}
  ): Promise<EndpointResponse<K>> {
    const endpoint = API_ENDPOINTS[endpointKey];
    const { method, path } = endpoint;
    
    const finalPath = replacePath(path, options.params as Record<string, string | number>);
    const queryString = buildQueryString(options.query as Record<string, string | number | boolean | string[]>);
    const url = `${this.baseUrl}${finalPath}${queryString}`;

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    const requestOptions: RequestInit = {
      method,
      headers,
      credentials: 'include',
    };

    if (options.body && method !== 'GET') {
      requestOptions.body = JSON.stringify(options.body);
    }

    const response = await fetch(url, requestOptions);

    if (!response.ok) {
      // Handle errors based on status code
      const errorData = await response.json().catch(() => null);
      throw new ApiError(response.status, response.statusText, errorData);
    }

    // Check if response is expected to be empty
    if (response.status === 204) {
      return null as unknown as EndpointResponse<K>;
    }

    // Parse response
    return response.json();
  }
}

// Custom error class
export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(status: number, statusText: string, data?: unknown) {
    super(statusText);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

// Create API client instance

export const api = new ApiClient(API_URL);

// Example usage with type safety
export async function fetchTodos(): Promise<Todo[]> {
  return api.request("getTodos");
}

export async function createTodo(item: string): Promise<Todo> {
  return api.request('createTodo', {
    body: { item }
  });
}


export async function updateTodo(id: number, item: string): Promise<Todo> {
  return api.request('updateTodo', {
    params: { todo_id: id },
    body: { item }
  });
}

export async function deleteTodo(id: number): Promise<boolean> {
  return api.request('deleteTodo', {
    params: { todo_id: id }
  });
}

