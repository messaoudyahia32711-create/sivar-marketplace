import { authClient } from '../api/client'

export interface AuthUser {
  id: number
  username: string
  role: string
}

export function useAuth() {
  const getUser = (): AuthUser | null => {
    const raw = localStorage.getItem('vendor_user')
    return raw ? JSON.parse(raw) : null
  }

  const getToken = (): string | null =>
    localStorage.getItem('vendor_token')

  const isAuthenticated = (): boolean =>
    !!getToken() && getUser()?.role === 'VENDOR'

  const login = async (username: string, password: string) => {
    const { data } = await authClient.post('/login/', { username, password })
    if (data.user?.role !== 'VENDOR') {
      throw new Error('هذا الحساب ليس حساب تاجر.')
    }
    localStorage.setItem('vendor_token', data.token)
    localStorage.setItem('vendor_user', JSON.stringify(data.user))
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
      localStorage.removeItem('vendor_token')
      localStorage.removeItem('vendor_user')
      // التحويل إلى البوابة المركزية عند تسجيل الخروج
      window.location.href = 'http://localhost:8000/login/'
    }
  }

  return { getUser, getToken, isAuthenticated, login, logout }
}
