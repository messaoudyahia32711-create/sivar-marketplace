import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  Tag, Plus, Search, Calendar, 
  Copy, Trash2, Eye, EyeOff, Gift, Zap
} from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Label } from '../../components/ui/label'
import { Badge } from '../../components/ui/badge'
import { 
  Dialog, DialogContent, DialogHeader, 
  DialogTitle, DialogTrigger, DialogFooter 
} from '../../components/ui/dialog'
import { 
  Select, SelectContent, SelectItem, 
  SelectTrigger, SelectValue 
} from '../../components/ui/select'
import { Card, CardContent } from '../../components/ui/card'
import { cn } from '../../lib/utils'
import { apiClient } from '../../api/client'
import { Skeleton } from '../../components/ui/skeleton'

export default function CouponsPage() {
  const [search, setSearch] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const queryClient = useQueryClient()

  // Fetch Coupons
  const { data: couponsData, isLoading } = useQuery({
    queryKey: ['coupons'],
    queryFn: () => apiClient.get('/coupons/').then(res => res.data)
  })

  // Mutations
  const toggleMutation = useMutation({
    mutationFn: (id: number) => apiClient.patch(`/coupons/${id}/toggle-status/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['coupons'] })
      toast.success('تم تحديث حالة الكوبون')
    }
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/coupons/${id}/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['coupons'] })
      toast.success('تم حذف الكوبون')
    }
  })

  const coupons = couponsData?.results || []
  const filteredCoupons = coupons.filter((c: any) => c.code.toLowerCase().includes(search.toLowerCase()))

  const toggleCoupon = (id: number) => {
    toggleMutation.mutate(id)
  }

  const deleteCoupon = (id: number) => {
    if (window.confirm('هل أنت متأكد من حذف هذا الكوبون؟')) {
      deleteMutation.mutate(id)
    }
  }

  const copyCode = (code: string) => {
    navigator.clipboard.writeText(code)
    toast.success(`تم نسخ الكود: ${code}`)
  }

  const stats = {
    total: coupons.length,
    active: coupons.filter((c: any) => c.is_active).length,
    totalUsed: coupons.reduce((s: number, c: any) => s + c.used, 0),
    expired: coupons.filter((c: any) => new Date(c.expires_at) < new Date()).length,
  }

  return (
    <div className="space-y-6 animate-fade-in" dir="rtl">
       <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-black flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center shadow-lg shadow-pink-500/20">
              <Tag className="w-5 h-5 text-white" />
            </div>
            العروض والكوبونات
          </h2>
          <p className="text-muted-foreground text-sm mt-2">أنشئ كوبونات خصم لجذب المزيد من العملاء</p>
        </div>
        <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2 rounded-xl bg-gradient-to-l from-pink-600 to-rose-600 hover:from-pink-700 hover:to-rose-700 shadow-lg shadow-pink-500/20">
              <Plus className="w-4 h-4" /> إنشاء كوبون
            </Button>
          </DialogTrigger>
          <CreateCouponModal onSuccess={() => setIsModalOpen(false)} />
        </Dialog>
      </div>

       <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'إجمالي الكوبونات', value: stats.total, icon: <Tag className="w-4 h-4 text-pink-400" />, color: 'glow-purple' },
          { label: 'كوبونات نشطة', value: stats.active, icon: <Zap className="w-4 h-4 text-emerald-400" />, color: 'glow-emerald' },
          { label: 'عدد الاستخدامات', value: stats.totalUsed, icon: <Gift className="w-4 h-4 text-blue-400" />, color: 'glow-blue' },
          { label: 'منتهية الصلاحية', value: stats.expired, icon: <Calendar className="w-4 h-4 text-orange-400" />, color: 'glow-orange' },
        ].map((stat, i) => (
          <Card key={i} className={cn("glass-card border-none", stat.color)}>
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-muted-foreground">{stat.label}</p>
                <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center">{stat.icon}</div>
              </div>
              <p className="text-3xl font-black">{isLoading ? <Skeleton className="w-12 h-8" /> : stat.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

       <div className="glass-card border-none p-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input value={search} onChange={e => setSearch(e.target.value)} placeholder="ابحث بكود الكوبون..." className="pr-10 rounded-xl bg-white/5 border-white/10 text-right" />
          </div>
        </div>

         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {isLoading ? (
             Array(3).fill(0).map((_, i) => <Skeleton key={i} className="h-[280px] rounded-2xl w-full" />)
          ) : filteredCoupons.map((coupon: any) => {
            const isExpired = new Date(coupon.expires_at) < new Date()
            const usagePercent = Math.round((coupon.used / coupon.max_uses) * 100)
            return (
              <div key={coupon.id} className={cn(
                "p-5 rounded-2xl border transition-all hover:scale-[1.02] group relative overflow-hidden",
                coupon.is_active && !isExpired 
                  ? "bg-gradient-to-br from-pink-500/5 to-violet-500/5 border-pink-500/20" 
                  : "bg-white/5 border-white/10 opacity-70"
              )}>
                 <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-l from-pink-500/50 to-violet-500/50 opacity-0 group-hover:opacity-100 transition-opacity" />
                
                 <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <button onClick={() => copyCode(coupon.code)} className="flex items-center gap-2 hover:text-pink-400 transition-colors">
                      <code className="text-lg font-black tracking-wider">{coupon.code}</code>
                      <Copy className="w-3 h-3 opacity-50" />
                    </button>
                  </div>
                  <Badge className={cn("rounded-full text-[10px]", coupon.is_active && !isExpired ? "bg-emerald-500/20 text-emerald-400" : "bg-gray-500/20 text-gray-400")}>
                    {isExpired ? 'منتهي' : coupon.is_active ? 'نشط' : 'متوقف'}
                  </Badge>
                </div>

                 <div className="flex items-baseline gap-2 mb-4">
                  <span className="text-4xl font-black text-pink-400">{coupon.value}</span>
                  <span className="text-lg font-bold text-muted-foreground">
                    {coupon.type === 'percentage' ? '%' : 'د.ج'} خصم
                  </span>
                </div>

                 <div className="space-y-2 text-xs text-muted-foreground mb-4">
                  <p>الحد الأدنى للطلب: {Number(coupon.min_order).toLocaleString()} د.ج</p>
                  <p>يُطبَّق على: {coupon.applies_to === 'all' ? 'الكل' : coupon.applies_to === 'products' ? 'المنتجات' : 'الخدمات'}</p>
                  <p>ينتهي: {new Date(coupon.expires_at).toLocaleDateString('ar-DZ')}</p>
                </div>

                 <div className="mb-4">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-muted-foreground">الاستخدام</span>
                    <span className="font-bold">{coupon.used}/{coupon.max_uses}</span>
                  </div>
                  <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-l from-pink-500 to-violet-500 rounded-full transition-all" style={{ width: `${usagePercent}%` }} />
                  </div>
                </div>

                 <div className="flex items-center gap-2">
                  <Button variant="ghost" size="sm" className="rounded-lg flex-1 h-8 text-xs gap-1" onClick={() => toggleCoupon(coupon.id)} disabled={toggleMutation.isPending}>
                    {coupon.is_active ? <><EyeOff className="w-3 h-3" /> إيقاف</> : <><Eye className="w-3 h-3" /> تفعيل</>}
                  </Button>
                  <Button variant="ghost" size="sm" className="rounded-lg h-8 text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10 gap-1" onClick={() => deleteCoupon(coupon.id)} disabled={deleteMutation.isPending}>
                    <Trash2 className="w-3 h-3" /> حذف
                  </Button>
                </div>
              </div>
            )
          })}
        </div>

        {!isLoading && filteredCoupons.length === 0 && (
          <div className="text-center py-16">
            <Tag className="w-16 h-16 mx-auto text-muted-foreground opacity-20 mb-4" />
            <p className="text-muted-foreground text-lg">لا توجد كوبونات</p>
            <p className="text-sm text-muted-foreground mt-1">أنشئ أول كوبون خصم لمتجرك الآن!</p>
          </div>
        )}
      </div>
    </div>
  )
}

function CreateCouponModal({ onSuccess }: { onSuccess: () => void }) {
  const [form, setForm] = useState({
    code: '', type: 'percentage', value: '', min_order: '', max_uses: '', expires_at: '', applies_to: 'all'
  })
  const queryClient = useQueryClient()
  
  const createMutation = useMutation({
    mutationFn: (data: any) => apiClient.post('/coupons/', data),
    onSuccess: () => {
      toast.success('تم إنشاء الكوبون بنجاح! 🎉')
      queryClient.invalidateQueries({ queryKey: ['coupons'] })
      onSuccess()
    },
    onError: (err: any) => {
      toast.error('حدث خطأ أثناء إنشاء الكوبون. يرجى مراجعة البيانات.')
    }
  })

  const updateForm = (field: string, value: any) => setForm(prev => ({ ...prev, [field]: value }))

  const generateCode = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    const code = Array.from({ length: 8 }, () => chars[Math.floor(Math.random() * chars.length)]).join('')
    updateForm('code', code)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(form)
  }

  return (
    <DialogContent className="max-w-lg glass-card border-white/10" dir="rtl">
      <DialogHeader>
        <DialogTitle className="text-2xl font-bold text-right flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-pink-500/20 flex items-center justify-center"><Tag className="w-4 h-4 text-pink-400" /></div>
          إنشاء كوبون جديد
        </DialogTitle>
      </DialogHeader>
      <form onSubmit={handleSubmit} className="space-y-4 pt-4">
        <div className="space-y-2">
          <Label className="text-sm font-semibold">كود الكوبون</Label>
          <div className="flex gap-2">
            <Input required value={form.code} onChange={e => updateForm('code', e.target.value.toUpperCase())} placeholder="مثلاً: WELCOME20" className="rounded-xl bg-white/5 border-white/10 text-right font-mono tracking-wider" />
            <Button type="button" variant="outline" onClick={generateCode} className="rounded-xl gap-1 border-white/10"><Zap className="w-4 h-4" /> توليد</Button>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label className="text-sm font-semibold">نوع الخصم</Label>
            <Select value={form.type} onValueChange={v => updateForm('type', v)}>
              <SelectTrigger className="rounded-xl bg-white/5 border-white/10"><SelectValue /></SelectTrigger>
              <SelectContent className="glass"><SelectItem value="percentage">نسبة مئوية %</SelectItem><SelectItem value="fixed">مبلغ ثابت د.ج</SelectItem></SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label className="text-sm font-semibold">القيمة</Label>
            <Input required type="number" value={form.value} onChange={e => updateForm('value', e.target.value)} placeholder={form.type === 'percentage' ? '20' : '500'} className="rounded-xl bg-white/5 border-white/10 text-right" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label className="text-sm font-semibold">الحد الأدنى للطلب</Label>
            <Input type="number" value={form.min_order} onChange={e => updateForm('min_order', e.target.value)} placeholder="2000" className="rounded-xl bg-white/5 border-white/10 text-right" />
          </div>
          <div className="space-y-2">
            <Label className="text-sm font-semibold">الحد الأقصى للاستخدامات</Label>
            <Input type="number" value={form.max_uses} onChange={e => updateForm('max_uses', e.target.value)} placeholder="100" className="rounded-xl bg-white/5 border-white/10 text-right" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label className="text-sm font-semibold">تاريخ الانتهاء</Label>
            <Input required type="date" value={form.expires_at} onChange={e => updateForm('expires_at', e.target.value)} className="rounded-xl bg-white/5 border-white/10" />
          </div>
          <div className="space-y-2">
            <Label className="text-sm font-semibold">يُطبق على</Label>
            <Select value={form.applies_to} onValueChange={v => updateForm('applies_to', v)}>
              <SelectTrigger className="rounded-xl bg-white/5 border-white/10"><SelectValue /></SelectTrigger>
              <SelectContent className="glass"><SelectItem value="all">الكل</SelectItem><SelectItem value="products">المنتجات فقط</SelectItem><SelectItem value="services">الخدمات فقط</SelectItem></SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter className="gap-2 pt-4">
          <Button type="button" variant="ghost" onClick={onSuccess} className="rounded-xl">إلغاء</Button>
          <Button type="submit" disabled={createMutation.isPending} className="rounded-xl gap-2 bg-gradient-to-l from-pink-600 to-rose-600"><Plus className="w-4 h-4" /> إنشاء الكوبون</Button>
        </DialogFooter>
      </form>
    </DialogContent>
  )
}
