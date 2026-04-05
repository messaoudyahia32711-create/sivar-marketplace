import { useState, useEffect, useMemo } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { toast } from 'sonner'
import { authClient } from '../../api/client'

export default function LoginPage() {
  const navigate    = useNavigate()
  const [searchParams] = useSearchParams()

  // ── 💡 التعديل الجذري: سحب التوكن باستخدام useSearchParams ──
  const ssoToken = useMemo(() => searchParams.get('token'), [searchParams])

  useEffect(() => {
    const handleAuth = async () => {
      // 1. إذا لم يوجد توكن، التحويل فوراً للبوابة المركزية
      if (!ssoToken) {
        window.location.href = 'http://localhost:8000/login/'
        return
      }

      // 2. إذا وجد توكن، نقوم بعملية الـ SSO المعتادة
      try {
        localStorage.setItem('incubator_token', ssoToken)
        const { data } = await authClient.get('profile/', {
           headers: { Authorization: `Token ${ssoToken}` }
        })
        
        if (data.role !== 'INCUBATOR') {
           throw new Error('هذا الحساب لا يملك صلاحيات الحاضنة')
        }
        
        localStorage.setItem('incubator_user', JSON.stringify(data))
        toast.success('تم تسجيل الدخول بنجاح!')
        navigate('/dashboard')
      } catch (err: any) {
        localStorage.removeItem('incubator_token')
        localStorage.removeItem('incubator_user')
        toast.error(err.message || 'فشل الدخول الموحد، سيتم تحويلك للبوابة')
        setTimeout(() => {
          window.location.href = 'http://localhost:8000/login/'
        }, 2000)
      }
    }
    
    handleAuth()
  }, [ssoToken, navigate])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#0F0F0F]" dir="rtl">
        <div className="relative">
            <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-[#D4AF37] to-[#8A7322] flex items-center justify-center mb-8 animate-pulse shadow-[0_0_50px_rgba(212,175,55,0.3)]">
                <span className="text-3xl font-black text-[#0F0F0F]">S</span>
            </div>
        </div>
        
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#D4AF37] mb-6"></div>
        
        <h2 className="text-[#D4AF37] text-2xl font-black mb-2 tracking-wide">
          {ssoToken ? 'جاري التحقق من الهوية...' : 'جاري تحويلك للبوابة المركزية...'}
        </h2>
        <p className="text-gray-400 text-sm">منصة سيفار (Sivar) - الدخول الموحد</p>
        
        <div className="mt-12 text-gray-600 text-[10px] uppercase tracking-[0.2em]">
            Secure Authentication Pipeline
        </div>
    </div>
  )
}
