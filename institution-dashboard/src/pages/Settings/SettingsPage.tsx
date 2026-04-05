import { useState, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Building2, Camera, Save, Phone, FileText, Shield, Briefcase, Fingerprint } from 'lucide-react'
import { toast } from 'sonner'
import { apiClient, generalClient } from '../../api/client'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Label } from '../../components/ui/label'
import { Textarea } from '../../components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { 
  Select, SelectContent, SelectItem, 
  SelectTrigger, SelectValue 
} from '../../components/ui/select'
import { Skeleton } from '../../components/ui/skeleton'

export default function SettingsPage() {
  const [formData, setFormData] = useState<any>({
    name: '', description: '', phone: '', wilaya_id: '',
    nif: '0001234567890123', rc: '24/00-1234567B21', 
    official_email: '', address: '', default_team_role: 'member'
  })
  const [previews, setPreviews] = useState({ logo: null as string | null, banner: null as string | null })

  const { data: store, isPending: isLoading } = useQuery({
    queryKey: ['store-settings'],
    queryFn: () => apiClient.get('/store/').then(res => res.data),
  })

  useEffect(() => {
    if (store) {
      setFormData({
        name: store.name || '',
        phone: store.phone || '', wilaya_id: store.wilaya?.id?.toString() || '',
        description: store.description || '',
        official_email: store.email || '',
        address: store.address || '',
        default_team_role: 'member'
      })
      setPreviews({ logo: store.logo, banner: store.banner })
    }
  }, [store])

  const { data: wilayas } = useQuery({
    queryKey: ['wilayas'],
    queryFn: () => generalClient.get('/localization/wilayas/').then(res => res.data)
  })

  const updateStore = useMutation({
    mutationFn: (data: FormData) => apiClient.put('/store/', data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    onSuccess: () => toast.success('تم تحديث إعدادات المؤسسة بنجاح ✅'),
    onError: () => toast.error('فشل تحديث الإعدادات')
  })

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>, type: 'logo' | 'banner') => {
    const file = e.target.files?.[0]
    if (file) {
      setFormData({ ...formData, [type]: file })
      const reader = new FileReader()
      reader.onloadend = () => setPreviews({ ...previews, [type]: reader.result as string })
      reader.readAsDataURL(file)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const data = new FormData()
    Object.keys(formData).forEach(key => {
      if (formData[key] !== null && formData[key] !== undefined) data.append(key, formData[key])
    })
    updateStore.mutate(data)
  }

  if (isLoading) return <div className="space-y-6"><Skeleton className="h-64 w-full rounded-2xl" /><Skeleton className="h-48 w-full rounded-2xl" /></div>

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in" dir="rtl">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center shadow-lg">
          <Building2 className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-3xl font-black">إعدادات المؤسسة</h2>
          <p className="text-sm text-muted-foreground">إدارة الهوية المؤسساتية والبيانات القانونية</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Banner */}
        <Card className="glass-card border-none overflow-hidden relative group">
          <div className="h-48 bg-gradient-to-l from-blue-500/10 to-violet-500/10 flex items-center justify-center overflow-hidden">
            {previews.banner ? (
              <img src={previews.banner} className="w-full h-full object-cover" alt="Banner" />
            ) : (
              <div className="flex flex-col items-center gap-2 text-muted-foreground">
                <Camera className="w-10 h-10 opacity-30" />
                <p className="text-sm">رفع صورة الغلاف الرسمية للمؤسسة</p>
              </div>
            )}
            <label className="absolute inset-0 cursor-pointer bg-black/50 opacity-0 group-hover:opacity-100 flex items-center justify-center text-white transition-opacity font-bold text-sm backdrop-blur-sm">
              <Camera className="w-5 h-5 ml-2" /> تغيير الغلاف
              <input type="file" className="hidden" accept="image/*" onChange={e => handleImageChange(e, 'banner')} />
            </label>
          </div>
          <div className="absolute bottom-4 right-8">
            <div className="w-20 h-20 rounded-2xl border-4 border-background bg-background shadow-xl relative overflow-hidden group/logo">
              {previews.logo ? (
                <img src={previews.logo} className="w-full h-full object-cover" alt="Logo" />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-white/5"><Building2 className="w-6 h-6 text-muted-foreground opacity-30" /></div>
              )}
              <label className="absolute inset-0 cursor-pointer bg-black/50 opacity-0 group-hover/logo:opacity-100 flex items-center justify-center text-white transition-opacity">
                <Camera className="w-4 h-4" />
                <input type="file" className="hidden" accept="image/*" onChange={e => handleImageChange(e, 'logo')} />
              </label>
            </div>
          </div>
        </Card>

        {/* General Info */}
        <Card className="glass-card border-none">
          <CardHeader><CardTitle className="text-right text-base font-bold flex items-center gap-2 justify-end">المعلومات التعريفية <FileText className="w-4 h-4 text-blue-400" /></CardTitle></CardHeader>
          <CardContent className="space-y-4 text-right">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>اسم المؤسسة الرسمي</Label>
                <div className="relative">
                  <Building2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} 
                    className="pr-10 rounded-xl bg-white/5 border-white/10" />
                </div>
              </div>
              <div className="space-y-2">
                <Label>رقم الهاتف الرسمي</Label>
                <div className="relative">
                  <Phone className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input value={formData.phone} onChange={e => setFormData({ ...formData, phone: e.target.value })} 
                    className="pr-10 rounded-xl bg-white/5 border-white/10" />
                </div>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
               <div className="space-y-2">
                 <Label>البريد الإلكتروني المؤسساتي</Label>
                 <Input value={formData.official_email} onChange={e => setFormData({ ...formData, official_email: e.target.value })} 
                   className="rounded-xl bg-white/5 border-white/10 text-right" placeholder="contact@institution.dz" />
               </div>
               <div className="space-y-2">
                 <Label>الولاية / المقر</Label>
                 <Select value={formData.wilaya_id} onValueChange={v => setFormData({ ...formData, wilaya_id: v })}>
                   <SelectTrigger className="rounded-xl bg-white/5 border-white/10"><SelectValue placeholder="اختر الولاية" /></SelectTrigger>
                   <SelectContent className="glass rounded-xl">
                     {wilayas?.map((w: any) => (
                       <SelectItem key={w.id} value={w.id.toString()}>{w.name}</SelectItem>
                     ))}
                   </SelectContent>
                 </Select>
               </div>
            </div>
            <div className="space-y-2">
              <Label>العنوان التفصيلي</Label>
              <Input value={formData.address} onChange={e => setFormData({ ...formData, address: e.target.value })} 
                className="rounded-xl bg-white/5 border-white/10 text-right" />
            </div>
            <div className="space-y-2">
              <Label>نبذة عن المؤسسة</Label>
              <Textarea rows={3} value={formData.description} onChange={e => setFormData({ ...formData, description: e.target.value })} 
                className="rounded-xl bg-white/5 border-white/10 text-right resize-none" />
            </div>
          </CardContent>
        </Card>

        {/* Legal Info */}
        <Card className="glass-card border-none">
          <CardHeader><CardTitle className="text-right text-base font-bold flex items-center gap-2 justify-end">الوثائق القانونية <Shield className="w-4 h-4 text-indigo-400" /></CardTitle></CardHeader>
          <CardContent className="space-y-4 text-right">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>الرقم الضريبي (NIF)</Label>
                <div className="relative">
                  <Fingerprint className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input value={formData.nif} onChange={e => setFormData({ ...formData, nif: e.target.value })} 
                    className="pr-10 rounded-xl bg-white/5 border-white/10 font-mono" />
                </div>
              </div>
              <div className="space-y-2">
                <Label>رقم السجل التجاري (RC)</Label>
                <div className="relative">
                  <FileText className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input value={formData.rc} onChange={e => setFormData({ ...formData, rc: e.target.value })} 
                    className="pr-10 rounded-xl bg-white/5 border-white/10 font-mono" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Team Settings */}
        <Card className="glass-card border-none">
          <CardHeader>
            <CardTitle className="text-right flex items-center gap-2 justify-end text-base font-bold">
              تفضيلات الفريق <Briefcase className="w-4 h-4 text-blue-400" />
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-right">
            <div className="space-y-2">
              <Label>الدور الافتراضي للأعضاء الجدد</Label>
              <Select value={formData.default_team_role} onValueChange={v => setFormData({ ...formData, default_team_role: v })}>
                <SelectTrigger className="rounded-xl bg-white/5 border-white/10"><SelectValue /></SelectTrigger>
                <SelectContent className="glass rounded-xl">
                  <SelectItem value="member">عضو (صلاحيات محدودة)</SelectItem>
                  <SelectItem value="editor">محرر (إدارة المحتوى)</SelectItem>
                  <SelectItem value="admin">مدير فرعي</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-[10px] text-muted-foreground">سيتم تطبيق هذا الدور تلقائياً عند قبول دعوة انضمام عضو جديد.</p>
            </div>
          </CardContent>
        </Card>

        {/* Policies */}
        <Card className="glass-card border-none">
          <CardHeader>
            <CardTitle className="text-right flex items-center gap-2 justify-end text-base">
              <Shield className="w-4 h-4 text-blue-400" /> سياسة الإرجاع
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea placeholder="اكتب سياسة الإرجاع الخاصة بمتجرك..." rows={6} value={formData.return_policy}
              onChange={e => setFormData({ ...formData, return_policy: e.target.value })} 
              className="text-right rounded-xl bg-white/5 border-white/10 resize-none" />
          </CardContent>
        </Card>

        {/* Submit */}
        <div className="flex justify-end gap-3 sticky bottom-4 z-10 glass-card border-none p-4">
          <Button variant="ghost" type="button" className="rounded-xl">تجاهل التغييرات</Button>
          <Button className="gap-2 rounded-xl bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-500/20" type="submit" disabled={updateStore.isPending}>
            <Save className="w-4 h-4" />
            {updateStore.isPending ? 'جاري الحفظ...' : 'حفظ الإعدادات'}
          </Button>
        </div>
      </form>
    </div>
  )
}
