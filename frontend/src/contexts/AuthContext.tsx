import { createContext, useContext, useState, useEffect } from 'react'
import type { ReactNode } from 'react'
import { api } from '../lib/api'

interface User {
  id: string
  username: string
  email: string
  role: 'user' | 'admin'
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  isAdmin: () => boolean
  isAuthenticated: () => boolean
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('auth_token')
  )
  const [loading, setLoading] = useState(true)

  // Set up axios interceptor for authentication
  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete api.defaults.headers.common['Authorization']
    }
  }, [token])

  // Validate token and get user info on app start
  useEffect(() => {
    const validateToken = async () => {
      if (token) {
        try {
          const response = await api.get('/auth/me')
          setUser(response.data.user)
        } catch (error) {
          // Token is invalid, clear it
          logout()
        }
      }
      setLoading(false)
    }

    validateToken()
  }, [])

  const login = async (username: string, password: string): Promise<void> => {
    try {
      const response = await api.post('/auth/login', {
        username,
        password
      })

      const { token: newToken, user: userData } = response.data
      
      setToken(newToken)
      setUser(userData)
      localStorage.setItem('auth_token', newToken)
      api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Login failed')
    }
  }

  const register = async (username: string, email: string, password: string): Promise<void> => {
    try {
      const response = await api.post('/auth/register', {
        username,
        email,
        password
      })

      const { token: newToken, user: userData } = response.data
      
      setToken(newToken)
      setUser(userData)
      localStorage.setItem('auth_token', newToken)
      api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Registration failed')
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('auth_token')
    delete api.defaults.headers.common['Authorization']
  }

  const isAdmin = (): boolean => {
    return user?.role === 'admin'
  }

  const isAuthenticated = (): boolean => {
    return user !== null && token !== null
  }

  const value: AuthContextType = {
    user,
    token,
    login,
    register,
    logout,
    isAdmin,
    isAuthenticated,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}