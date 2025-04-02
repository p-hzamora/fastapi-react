export const API_VERSION = import.meta.env.VITE_API_VERSION || 'v1';
export const API_PATH = `api/${API_VERSION}`;

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const API_URL= `${API_BASE_URL}/${API_PATH}` // "http://localhost:8000/api/v1"