import axios, { AxiosRequestConfig } from 'axios';
import { 
  EndpointKey, 
  HttpMethod, 
  Route, 
  RequestBody, 
  ResponseBody, 
  PathParams 
} from './api';

import { API_URL } from '../constants';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for auth headers
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Function to replace path parameters in URL
function replacePathParams<T extends EndpointKey>(
  route: Route<T>,
  params?: PathParams<T>
): string {
  if (!params) return route;
  let url = route;
  Object.entries(params).forEach(([key, value]) => {
    url = url.replace(`{${key}}`, encodeURIComponent(String(value)));
  });
  return url;
}

// Main function to make API calls
export async function apiCall<T extends EndpointKey>(
  endpoint: T,
  data?: RequestBody<T>,
  params?: PathParams<T>,
  config?: Omit<AxiosRequestConfig, 'url' | 'method' | 'data'>
): Promise<ResponseBody<T>> {
  const method = endpoint.split(' ')[0].toLowerCase() as Lowercase<HttpMethod<T>>;
  const route = endpoint.substring(endpoint.indexOf(' ') + 1) as Route<T>;
  const url = replacePathParams(route, params);
  
  try {
    const response = await apiClient({
      method,
      url,
      data,
      ...config,
    });
    return response.data;
  } catch (error) {
    // Handle error or rethrow
    console.error('API call failed:', error);
    throw error;
  }
}

// Convenience methods
export const api = {
  get: <T extends Extract<EndpointKey, `GET ${string}`>>(
    endpoint: T,
    params?: PathParams<T>,
    config?: AxiosRequestConfig
  ) => apiCall(endpoint, undefined, params, config),
  
  post: <T extends Extract<EndpointKey, `POST ${string}`>>(
    endpoint: T,
    data?: RequestBody<T>,
    params?: PathParams<T>,
    config?: AxiosRequestConfig
  ) => apiCall(endpoint, data, params, config),
  
  put: <T extends Extract<EndpointKey, `PUT ${string}`>>(
    endpoint: T,
    data?: RequestBody<T>,
    params?: PathParams<T>,
    config?: AxiosRequestConfig
  ) => apiCall(endpoint, data, params, config),
  
  patch: <T extends Extract<EndpointKey, `PATCH ${string}`>>(
    endpoint: T,
    data?: RequestBody<T>,
    params?: PathParams<T>,
    config?: AxiosRequestConfig
  ) => apiCall(endpoint, data, params, config),
  
  delete: <T extends Extract<EndpointKey, `DELETE ${string}`>>(
    endpoint: T,
    params?: PathParams<T>,
    config?: AxiosRequestConfig
  ) => apiCall(endpoint, undefined, params, config),
  
  options: <T extends Extract<EndpointKey, `OPTIONS ${string}`>>(
    endpoint: T,
    params?: PathParams<T>,
    config?: AxiosRequestConfig
  ) => apiCall(endpoint, undefined, params, config),
  
  trace: <T extends Extract<EndpointKey, `TRACE ${string}`>>(
    endpoint: T,
    params?: PathParams<T>,
    config?: AxiosRequestConfig
  ) => apiCall(endpoint, undefined, params, config),
};

export default api;