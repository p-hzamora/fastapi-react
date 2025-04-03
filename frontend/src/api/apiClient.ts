import { TODO_ENDPOINTS } from "../types/todo";
import { AUTH_ENDPOINTS } from "../types/auth";

const API_ENDPOINTS = {
  ...TODO_ENDPOINTS,
  ...AUTH_ENDPOINTS,
} as const;

type Endpoints = typeof API_ENDPOINTS;
type TodoKeys = keyof Endpoints


type EndpointResponse<K extends TodoKeys> = Endpoints[K]["responseType"];

type EndpointParams<K extends TodoKeys> = Endpoints[K] extends { paramType: infer P } ? P : never;
type EndPointBody<K extends TodoKeys> = Endpoints[K] extends { requestType: infer R } ? R : never
type EndpointRequest<K extends TodoKeys> = Endpoints[K] extends {requestType: infer Req }? Req: never

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl
  }


  async request<K extends TodoKeys>(
    endpointKey: K,
    options?: {
      params?: EndpointParams<K>,
      query?: EndpointRequest<K>,
      body?: EndPointBody<K>,
      headers?: HeadersInit;
    }
  ): Promise<EndpointResponse<K>> {
    const endpoint = API_ENDPOINTS[endpointKey]
    const { method, path } = endpoint;

    const finalPath = this.replacePath(path, options?.params)
    const queryString = this.buildQueryString(options?.query)

    const url = `${this.baseUrl}${finalPath}${queryString}`

    const defaultheaders: HeadersInit = {
      'Content-Type': 'application/json',
      'Accept': "application/json", // i want to be able to modify this param or add Authorization from outside of my app
    }

    const headers:HeadersInit = {
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

    return fetch(url, requestOptions)
      .then(res => { return res.json() })
      .catch(()=> {
        throw new Error("Error searching movies")
      });

  }

  private replacePath<K extends TodoKeys>(path:string, params?: EndpointParams<K>):string{
    if (!params)return path;

    let finalPath = path;
    for (const [key,value] of Object.entries(params)){
      finalPath = finalPath.replace(`{${key}}`, String(value))
    }
    return finalPath;
  }

  private buildQueryString<K extends TodoKeys>(query?:EndpointRequest<K>):string{
    if (!query) return '';

    const params = new URLSearchParams();
    Object.entries(query).forEach(([key, value])=>{
      if (Array.isArray(value)){
        value.forEach(v=>params.append(key, String(v)));
      }else{
        params.append(key,String(value))
      }
    });

    const queryString = params.toString();
    return queryString? `?${queryString}`: '';
  }
}
