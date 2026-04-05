import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Client الرئيسي — يشير إلى /api للوصول لجميع الـ endpoints العامة
// (orders, chat, users, etc.)
export const apiClient = axios.create({
  baseURL: `${API_BASE}/api`,
})

// Client for general APIs (Categories, localization, etc.)
export const generalClient = axios.create({
  baseURL: `${API_BASE}/api`,
})

// إضافة Token تلقائياً لكل طلب
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('customer_token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

// معالجة انتهاء الجلسة
apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('customer_token')
      localStorage.removeItem('customer_user')
      // التحويل المباشر للبوابة المركزية عند انتهاء الصلاحية
      window.location.href = 'http://localhost:8000/login/'
    }
    return Promise.reject(err)
  }
)

// client منفصل لتسجيل الدخول (لا يحتاج token)
export const authClient = axios.create({
  baseURL: `${API_BASE}/api/users`,
})

// Apply token to generalClient as well
generalClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('customer_token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})
