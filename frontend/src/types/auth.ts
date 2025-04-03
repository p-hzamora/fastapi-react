export interface ApiKey {
  api_key?: string
}

export interface SessionUserResponse {
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
    path: "/api_key",
    responseType: {} as ApiKey,
  },
  authDeleteApiKey: {
    method: "DELETE",
    path: "/api_key",
    responseType: {} as boolean,
  },
  authGetApiKey: {
    method: "GET",
    path: "/api_key",
    responseType: {} as ApiKey,
  },
  authSignin: {
    method: "POST",
    path: "/signin",
    responseType: {} as SessionUserResponse,
    requestType: {} as SigninForm,
  },
  authSignup: {
    method: "POST",
    path: "/signup",
    responseType: {} as SessionUserResponse,
    requestType: {} as SignupForm,
  },
  authSignout: {
    method: "GET",
    path: "/signout",
    responseType: undefined,
  }
} as const;
