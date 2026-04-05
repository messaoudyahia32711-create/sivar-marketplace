import { useState, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { User, Camera, Save, Phone, Mail, MapPin, Lock } from 'lucide-react'
import { toast } from 'sonner'
import { apiClient, generalClient } from '../../api/client'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Label } from '../../components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import {
  Select, SelectContent, SelectItem,
  SelectTrigger, SelectValue
} from '../../components/ui/select'
import { Skeleton } from '../../components/ui/skeleton'

export default function SettingsPage() {
  const [formData, setFormData] = useState<any>({
    first_name: '', last_name: '', email: '', phone_number: '',
  })
  const [passwordData, setPasswordData] = useState({
    old_password: '', new_password: '', confirm_password: '',
  })
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null)

  // ── Fetch profile ──
  const { data: profile, isPending: isLoading } = useQuery({
    queryKey: ['customer-profile'],
    queryFn: () => apiClient.get('/users/profile/').then(res => res.data),
  })

  useEffect(() => {
    if (profile) {
      setFormData({
        first_name: profile.first_name || '',
        last_name: profile.last_name || '',
        email: profile.email || '',
        phone_number: profile.phone_number || '',
      })
      setAvatarPreview(profile.profile_picture || null)
    }
  }, [profile])

  // ── Update profile ──
  const updateProfile = useMutation({
    mutationFn: (data: FormData) => apiClient.put('/users/profile/', data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    onSuccess: () => toast.success('تم تحديث الملف الشخصي بنجاح ✅'),
    onError: () => toast.error('فشل تحديث الملف الشخصي')
  })

  // ── Change password ──
  const changePassword = useMutation({
    mutationFn: (data: typeof passwordData) => apiClient.post('/users/change-password/', data),
    onSuccess: () => {
      toast.success('تم تغيير كلمة المرور بنجاح ✅')
      setPasswordData({ old_password: '', new_password: '', confirm_password: '' })
    },
    onError: (err: any) => {
      const msg = err.response?.data?.message || err.response?.data?.error || 'فشل تغيير كلمة المرور'
      toast.error(msg)
    }
  })

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setFormData({ ...formData, profile_picture: file })
      const reader = new FileReader()
      reader.onloadend = () => setAvatarPreview(reader.result as string)
      reader.readAsDataURL(file)
    }
  }

  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const data = new FormData()
    Object.keys(formData).forEach(key => {
      if (formData[key] !== null && formData[key] !== undefined) data.append(key, formData[key])
    })
    updateProfile.mutate(data)
  }

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error('كلمة المرور الجديدة غير متطابقة')
      return
    }
    if (passwordData.new_password.length < 6) {
      toast.error('كلمة المرور يجب أن تكون 6 أحرف على الأقل')
      return
    }
    changePassword.mutate(passwordData)
  }

  if (isLoading) return <div className="space-y-6"><Skeleton className="h-64 w-full rounded-2xl" /><Skeleton className="h-48 w-full rounded-2xl" /></div>

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in" dir="rtl">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center shadow-lg">
          <User className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-3xl font-black">إعدادات الحساب</h2>
          <p className="text-sm text-muted-foreground">إدارة ملفك الشخصي وتغيير كلمة المرور</p>
        </div>
      </div>

      {/* ── Profile Form ── */}
      <form onSubmit={handleProfileSubmit} className="space-y-6">
        {/* Avatar */}
        <Card className="glass-card border-none">
          <CardContent className="p-6 flex items-center gap-6">
            <div className="relative group">
              <div className="w-24 h-24 rounded-2xl border-4 border-background bg-background shadow-xl overflow-hidden">
                {avatarPreview ? (
                  <img src={avatarPreview} className="w-full h-full object-cover" alt="Avatar" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-500 to-violet-600">
                    <span className="text-3xl font-bold text-white">
                      {formData.first_name?.[0]?.toUpperCase() || profile?.username?.[0]?.toUpperCase() || 'م'}
                    </span>
                  </div>
                )}
              </div>
              <label className="absolute inset-0 cursor-pointer bg-black/50 opacity-0 group-hover:opacity-100 flex items-center justify-center text-white transition-opacity rounded-2xl">
                <Camera className="w-5 h-5" />
                <input type="file" className="hidden" accept="image/*" onChange={handleAvatarChange} />
              </label>
            </div>
            <div>
              <p className="font-bold text-lg">{profile?.username}</p>
              <p className="text-sm text-muted-foreground">حساب زبون</p>
              <p className="text-xs text-blue-400 mt-1">انقر على الصورة لتغييرها</p>
            </div>
          </CardContent>
        </Card>

        {/* Personal Info */}
        <Card className="glass-card border-none">
          <CardHeader><CardTitle className="text-right text-base">المعلومات الشخصية</CardTitle></CardHeader>
          <CardContent className="space-y-4 text-right">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>الاسم الأول</Label>
                <div className="relative">
                  <User className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input value={formData.first_name} onChange={e => setFormData({ ...formData, first_name: e.target.value })}
                    className="pr-10 rounded-xl bg-white/5 border-white/10" placeholder="الاسم الأول" />
                </div>
              </div>
              <div className="space-y-2">
                <Label>الاسم الأخير</Label>
                <div className="relative">
                  <User className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input value={formData.last_name} onChange={e => setFormData({ ...formData, last_name: e.target.value })}
                    className="pr-10 rounded-xl bg-white/5 border-white/10" placeholder="الاسم الأخير" />
                </div>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>البريد الإلكتروني</Label>
                <div className="relative">
                  <Mail className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input type="email" value={formData.email} onChange={e => setFormData({ ...formData, email: e.target.value })}
                    className="pr-10 rounded-xl bg-white/5 border-white/10" placeholder="example@email.com" />
                </div>
              </div>
              <div className="space-y-2">
                <Label>رقم الهاتف</Label>
                <div className="relative">
                  <Phone className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input value={formData.phone_number} onChange={e => setFormData({ ...formData, phone_number: e.target.value })}
                    className="pr-10 rounded-xl bg-white/5 border-white/10" placeholder="0555 123 456" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Submit Profile */}
        <div className="flex justify-end">
          <Button className="gap-2 rounded-xl bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-500/20" type="submit" disabled={updateProfile.isPending}>
            <Save className="w-4 h-4" />
            {updateProfile.isPending ? 'جاري الحفظ...' : 'حفظ التعديلات'}
          </Button>
        </div>
      </form>

      {/* ── Change Password ── */}
      <form onSubmit={handlePasswordSubmit}>
        <Card className="glass-card border-none">
          <CardHeader>
            <CardTitle className="text-right flex items-center gap-2 justify-end text-base">
              <Lock className="w-4 h-4 text-amber-400" /> تغيير كلمة المرور
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-right">
            <div className="space-y-2">
              <Label>كلمة المرور الحالية</Label>
              <Input type="password" value={passwordData.old_password}
                onChange={e => setPasswordData({ ...passwordData, old_password: e.target.value })}
                className="rounded-xl bg-white/5 border-white/10" placeholder="••••••••" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>كلمة المرور الجديدة</Label>
                <Input type="password" value={passwordData.new_password}
                  onChange={e => setPasswordData({ ...passwordData, new_password: e.target.value })}
                  className="rounded-xl bg-white/5 border-white/10" placeholder="••••••••" />
              </div>
              <div className="space-y-2">
                <Label>تأكيد كلمة المرور</Label>
                <Input type="password" value={passwordData.confirm_password}
                  onChange={e => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                  className="rounded-xl bg-white/5 border-white/10" placeholder="••••••••" />
              </div>
            </div>
            <div className="flex justify-end mt-4">
              <Button className="gap-2 rounded-xl bg-amber-600 hover:bg-amber-700 shadow-lg shadow-amber-500/20" type="submit" disabled={changePassword.isPending}>
                <Lock className="w-4 h-4" />
                {changePassword.isPending ? 'جاري التغيير...' : 'تغيير كلمة المرور'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  )
}
