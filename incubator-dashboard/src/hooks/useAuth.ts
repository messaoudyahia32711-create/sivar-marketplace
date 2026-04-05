import { authClient } from '../api/client'

export interface AuthUser {
  id: number
  username: string
  email: string
  role: 'CUSTOMER' | 'VENDOR' | 'INSTITUTION' | 'INCUBATOR'
  university_name?: string
  profile_picture?: string
}

export function useAuth() {
  const getUser = (): AuthUser | null => {
    const raw = localStorage.getItem('incubator_user')
    return raw ? JSON.parse(raw) : null
  }

  const getToken = (): string | null =>
    localStorage.getItem('incubator_token')

  const isAuthenticated = (): boolean =>
    !!getToken() && getUser()?.role === 'INCUBATOR'

  const login = async (username: string, password: string) => {
    const { data } = await authClient.post('/login/', { username, password })
    if (data.user?.role !== 'INCUBATOR') {
      throw new Error('هذا الحساب ليس حساب حاضنة.')
    }
    localStorage.setItem('incubator_token', data.token)
    localStorage.setItem('incubator_user', JSON.stringify(data.user))
    return data
  }

  const logout = async () => {
    try {
      const token = getToken()
      if (token) {
        await authClient.post('/logout/', {}, {
          headers: { Authorization: `Token ${token}` },
        })
      }
    } finally {
      localStorage.removeItem('incubator_token')
      localStorage.removeItem('incubator_user')
      // التحويل إلى البوابة المركزية عند تسجيل الخروج
      window.location.href = 'http://localhost:8000/login/'
    }
  }

  return { getUser, getToken, isAuthenticated, login, logout }
}
