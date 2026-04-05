import { authClient } from '../api/client'

export interface AuthUser {
  id: number
  username: string
  role: string
}

export function useAuth() {
  const getUser = (): AuthUser | null => {
    const raw = localStorage.getItem('institution_user')
    return raw ? JSON.parse(raw) : null
  }

  const getToken = (): string | null =>
    localStorage.getItem('institution_token')

  const isAuthenticated = (): boolean =>
    !!getToken() && getUser()?.role === 'INSTITUTION'

  const login = async (username: string, password: string) => {
    const { data } = await authClient.post('/login/', { username, password })
    if (data.user?.role !== 'INSTITUTION') {
      throw new Error('هذا الحساب ليس حساب مؤسسة.')
    }
    localStorage.setItem('institution_token', data.token)
    localStorage.setItem('institution_user', JSON.stringify(data.user))
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
      localStorage.removeItem('institution_token')
      localStorage.removeItem('institution_user')
      // التحويل إلى البوابة المركزية عند تسجيل الخروج
      window.location.href = 'http://localhost:8000/login/'
    }
  }

  return { getUser, getToken, isAuthenticated, login, logout }
}
