export interface ApiKey {
  api_key?: string
}

export interface User {
  token: string
  token_type: string

  id: string
  name: string
  email: string
  role: string
  profile_image_url: string

  expires_at?: string
  permissios?: Record<string, unknown>
}


export interface SigninForm {
  email: string
  password: string

}


export interface SignupForm {
  name: string
  email: string
  password: string
  profile_image_url?: string

}

export const AUTH_ENDPOINTS = {
  authGenerateApiKey: {
    method: "POST",
    path: "/auth/api_key",
    responseType: {} as ApiKey,
  },
  authDeleteApiKey: {
    method: "DELETE",
    path: "/auth/api_key",
    responseType: {} as boolean,
  },
  authGetApiKey: {
    method: "GET",
    path: "/auth/api_key",
    responseType: {} as ApiKey,
  },
  authSignin: {
    method: "POST",
    path: "/auth/signin",
    responseType: {} as User,
    requestType: {} as SigninForm,
  },
  authSignup: {
    method: "POST",
    path: "/auth/signup",
    responseType: {} as User,
    requestType: {} as SignupForm,
  },
  authSignout: {
    method: "GET",
    path: "/auth/signout",
    responseType: undefined,
  }
} as const;

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface AuthContextType extends AuthState {
  login: (credentials: SigninForm) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}