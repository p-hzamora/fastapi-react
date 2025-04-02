
import { TodoEndpoints } from './todo';
import { AuthEndpoints } from './auth';
import { ItemEndpoints } from './item';

// Combine all endpoint types
export type ApiEndpoints = TodoEndpoints & AuthEndpoints & ItemEndpoints;

// Helper type to extract endpoint information
export type EndpointKey = keyof ApiEndpoints;

export type HttpMethod<T extends EndpointKey> = T extends `${infer M} ${string}` ? M : never;
export type Route<T extends EndpointKey> = T extends `${string} ${infer R}` ? R : never;

export type RequestBody<T extends EndpointKey> = ApiEndpoints[T]["request"];
export type ResponseBody<T extends EndpointKey> = ApiEndpoints[T]["response"];
export type PathParams<T extends EndpointKey> = ApiEndpoints[T] extends { params: infer P } ? P : never;

// Re-export all types for convenience
export * from './todo';
export * from './auth';
export * from './item';