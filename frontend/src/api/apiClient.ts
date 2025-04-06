import { TODO_ENDPOINTS } from "../types/todo";
import { AUTH_ENDPOINTS } from "../types/auth";
import { USER_ENDPOINTS } from "../types/user";

import { API_URL, TOKEN } from "../constants";


const API_ENDPOINTS = {
  ...TODO_ENDPOINTS,
  ...AUTH_ENDPOINTS,
  ...USER_ENDPOINTS,
} as const;

type Endpoints = typeof API_ENDPOINTS;
type TodoKeys = keyof Endpoints


type EndpointResponse<K extends TodoKeys> = Endpoints[K]["responseType"];

type EndpointParams<K extends TodoKeys> = Endpoints[K] extends { paramType: infer P }
  ? P extends null ? never : P
  : never;


type EndpointRequest<K extends TodoKeys> = Endpoints[K] extends { requestType: infer Req }
  ? Req extends null ? never : Req
  : never


// First, create more precise type definitions
type RequestOptions<K extends TodoKeys> = {
  headers?: HeadersInit,
  params?: EndpointParams<K>,
  body?: EndpointRequest<K> | URLSearchParams,
}


export class ApiError extends Error {
  constructor(public status: number, public data: any) {
    const message = Array.isArray(data?.detail)
      ? data.detail.map((e: any) => e.msg).join(", ")
      : (data?.detail || "API error")
    super(message)
  }
}



export class ApiClient {
  private baseUrl: string;
  private token?: string;

  constructor(baseUrl: string, token?: string) {
    this.baseUrl = baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl
    this.token = token
  }


  setToken(token: string): void {
    this.token = token;
  }

  clearToken(): void {
    this.token = undefined;
  }

  // async request<K extends TodoKeys>(
  //   endpointKey: K,
  //   options?: {
  //     params?: EndpointParams<K>,
  //     body?: EndpointRequest<K> | URLSearchParams,
  //     headers?: HeadersInit
  //   }

  async request<K extends TodoKeys>(
    endpointKey: K,
    options?: RequestOptions<K>
  ): Promise<EndpointResponse<K>> {
    const endpoint = API_ENDPOINTS[endpointKey]
    const { method, path } = endpoint;

    const finalPath = this.replacePath(path, options?.params)
    const queryString = this.buildQueryString(options?.body)

    const url = `${this.baseUrl}${finalPath}/${queryString}`

    const defaultheaders: HeadersInit = {
      'Content-Type': 'application/json',
      'Accept': "application/json", // i want to be able to modify this param or add Authorization from outside of my app
    }

    if (this.token) {
      defaultheaders['Authorization'] = `Bearer ${this.token}`
    }
    const headers: HeadersInit = {
      ...defaultheaders,
      ...options?.headers,

    }

    const requestOptions: RequestInit = {
      method,
      headers,
      credentials: 'include',
    }

    if (options?.body && method != "GET") {
      requestOptions.body = JSON.stringify(options?.body)

    }

    return await fetch(url, requestOptions)
      .then(async res => {
        const data = await res.json()
        if (!res.ok) {
          throw new ApiError(res.status, data)
        }
        return data
      })
      .catch(() => {
        throw new Error("API error")
      });

  }

  private replacePath<K extends TodoKeys>(path: string, params?: EndpointParams<K>): string {
    if (!params) return path;

    let finalPath = path;
    for (const [key, value] of Object.entries(params)) {
      finalPath = finalPath.replace(`{${key}}`, String(value))
    }
    return finalPath;
  }

  private buildQueryString<K extends TodoKeys>(query?: EndpointRequest<K> | URLSearchParams): string {
    if (!query) return '';

    if (query instanceof URLSearchParams) { return query.toString() }

    const params = new URLSearchParams();
    Object.entries(query).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        value.forEach(v => params.append(key, String(v)));
      } else {
        params.append(key, String(value))
      }
    });

    const queryString = params.toString();
    return queryString ? `?${queryString}` : '';
  }

  async formRequest<K extends TodoKeys>(
    endpointKey: K,
    formData: Record<string, any>,
    options?: {
      params?: EndpointParams<K>,
      headers?: HeadersInit
    }
  ): Promise<EndpointResponse<K>> {

    const formUrlEncoded = this.convertToFormUrlEncoded(formData)
    return await this.request(
      endpointKey, {
      ...options,
      headers: {
        ...options?.headers,
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formUrlEncoded,
    },
    )
  }

  private convertToFormUrlEncoded(formData: Record<string, any>): URLSearchParams {
    const formBody = new URLSearchParams();

    // Add each field to the URLSearchParams object
    Object.entries(formData).forEach(([key, value]) => {
      // Skip undefined or null values
      if (value !== undefined && value !== null) {
        formBody.append(key, String(value));
      }
    });

    return formBody;
  }

}


export const apiClient = new ApiClient(API_URL, TOKEN)