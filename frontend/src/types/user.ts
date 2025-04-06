interface Settings {
    ui: Record<string, unknown>
    additionalProp1: unknown
}

export interface UserModel {
    id: string,
    name: string,
    email: string,
    role: 'pending' | 'role' | 'admin',
    profile_image_url: string,
    last_active_at: 0,
    updated_at: 0,
    created_at: 0,
    api_key: string,
    settings: Settings,
    "info": string

}
export interface UserResponse {
    name: string,
    profile_image_url: string,
    active: boolean
}


export interface UserRoleUpdateForm {
    id: string
    role: string

}


export const USER_ENDPOINTS = {
    userGetUsers: {
        method: "GET",
        path: "/user",
        responseType: {} as UserModel[],
        paramType: {} as { skip: number, limit: number }
    },
    userUpdateUserRole: {
        method: "POST",
        path: "/user/update/role",
        responseType: {} as UserModel,
        requestType: {} as UserRoleUpdateForm
    },
    userInsertNewUser: {
        method: "POST",
        path: "/user/{user_id}",
        responseType: {} as UserResponse,
        paramType: {} as { user_id: string }
    },
    userGetUserById: {
        method: "GET",
        path: "/user/{user_id}",
        responseType: {} as UserResponse,
        paramType: {} as { user_id: string }

    }
} as const;



// response