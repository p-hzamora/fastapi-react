/**
 * Auth related types matching your Python models
 */
export interface Auth {
    id: string;
    email: string;
    password: string;
    active: boolean;
  }
  
  export interface Token {
    token: string;
    token_type: string;
  }
  
  export interface ApiKey {
    api_key?: string | null;
  }
  
  export interface UserResponse {
    id: string;
    email: string;
    name: string;
    role: string;
    profile_image_url: string;
  }
  
  export interface SigninResponse extends Token, UserResponse {}
  
  export interface SigninForm {
    email: string;
    password: string;
  }
  
  export interface LdapForm {
    user: string;
    password: string;
  }
  
  export interface ProfileImageUrlForm {
    profile_image_url: string;
  }
  
  export interface UpdateProfileForm extends ProfileImageUrlForm {
    name: string;
  }
  
  export interface UpdatePasswordForm {
    password: string;
    new_password: string;
  }
  
  export interface SignupForm {
    name: string;
    email: string;
    password: string;
    profile_image_url?: string;
  }
  
  // API endpoint definitions for Auth
  export type AuthEndpoints = {
    "POST /api_key": {
      response: ApiKey;
      request: undefined;
    };
    "DELETE /api_key": {
      response: boolean;
      request: undefined;
    };
    "GET /api_key": {
      response: ApiKey;
      request: undefined;
    };
    "POST /signin": {
      response: SigninResponse;
      request: SigninForm;
    };
    "POST /signup": {
      response: SigninResponse;
      request: SignupForm;
    };
    "GET /signout": {
      response: boolean;
      request: undefined;
    };
    "POST /update/profile": {
      response: UserResponse;
      request: UpdateProfileForm;
    };
    "POST /update/password": {
      response: boolean;
      request: UpdatePasswordForm;
    };
    "POST /update/role": {
      response: UserResponse;
      request: { id: string; role: string };
    };
    "GET /users/": {
      response: UserResponse[];
      request: undefined;
    };
  };