import { createContext, ReactNode, useEffect, useReducer } from 'react'
import { AuthContextType, AuthState, SigninForm, User } from '../types/auth'
import { apiClient, ApiError } from '../api/apiClient'

const AuthType = {
  LOGIN_REQUEST: 'LOGIN_REQUEST',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  CLEAR_ERROR: 'CLEAR_ERROR',
} as const

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
}

export const AuthContext = createContext<AuthContextType>({
  ...initialState,
  login: async () => {},
  logout: () => {},
  clearError: () => {},
})

type AuthActionType =
  | { type: typeof AuthType.LOGIN_REQUEST }
  | { type: typeof AuthType.LOGIN_SUCCESS; payload: { user: User } }
  | { type: typeof AuthType.LOGIN_FAILURE; payload: string }
  | { type: typeof AuthType.LOGOUT }
  | { type: typeof AuthType.CLEAR_ERROR }

const authReducer = (state: AuthState, action: AuthActionType): AuthState => {
  switch (action.type) {
    case AuthType.LOGIN_REQUEST:
      return {
        ...state,
        isLoading: true,
        error: null,
      }
    case AuthType.LOGIN_SUCCESS:
      return {
        ...state,
        isLoading: false,
        isAuthenticated: true,
        user: action.payload.user,
        error: null,
      }
    case AuthType.LOGIN_FAILURE:
      return {
        ...state,
        isLoading: false,
        isAuthenticated: false,
        user: null,
        error: action.payload,
      }
    case AuthType.LOGOUT:
      return {
        ...initialState,
      }
    case AuthType.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      }
    default:
      return state
  }
}

interface AuthProviderProps {
  children: ReactNode
}

export default function AuthProvider({ children }: AuthProviderProps) {
  const [state, dispatch] = useReducer(authReducer, initialState)

  useEffect(() => {
    const loadUser = async () => {
      const storedUser = localStorage.getItem('user')

      if (storedUser) {
        const user = JSON.parse(storedUser as string) as User
        dispatch({
          type: AuthType.LOGIN_SUCCESS,
          payload: {
            user,
          },
        })
      }
    }
    loadUser()
  }, [])

  const login = async (credentials: SigninForm) => {
    dispatch({ type: AuthType.LOGIN_REQUEST })
    try {
      const user = await apiClient.formRequest('authSignin', {body:credentials})

      localStorage.setItem('user', JSON.stringify(user))

      // Update state
      dispatch({
        type: AuthType.LOGIN_SUCCESS,
        payload: { user },
      })
    } catch (error) {
      let errorMessage = 'Login failed. Please try again'
      if (error instanceof ApiError) {
        errorMessage = error.message
      }

      dispatch({
        type: AuthType.LOGIN_FAILURE,
        payload: errorMessage,
      })
    }
  }

  const logout = () => {
    localStorage.removeItem('user')
    apiClient.request('authSignout')
    dispatch({
      type: AuthType.LOGOUT,
    })
  }

  const clearError = () => {
    dispatch({ type: AuthType.CLEAR_ERROR })
  }

  return (
    <AuthContext.Provider
        value={
            {
                ...state,
                login,
                logout,
                clearError
            }
        }
    >
        {children}
    </AuthContext.Provider>
  )
}
