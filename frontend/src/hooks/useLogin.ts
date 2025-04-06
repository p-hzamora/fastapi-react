import { SessionUserResponse, SigninForm } from "../types/auth";
import { apiClient, ApiError } from "../api/apiClient";
import { useState } from "react";


export function useLogin() {
    const [error, setError] = useState<string>('');
    const [isLoading, setIsLoading] = useState(false);


    const getUser =  async ({email, password}:SigninForm):Promise<SessionUserResponse> =>{
        return await apiClient.formRequest("authSignin", { email, password })
            .then(data => {
                setIsLoading(false);
                console.log(data)
                return data
            })
            .catch(err => {
                if (err instanceof ApiError) {
                    console.error("API error:", err.message)
                    console.error("Status:", err.status)
                    console.error("Details:", err.data)
                }
                throw err
            })

    }
    return {getUser, isLoading, setIsLoading, error, setError}

    
}