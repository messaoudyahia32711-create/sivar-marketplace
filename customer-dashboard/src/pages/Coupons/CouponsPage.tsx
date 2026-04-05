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

  // Fetch Coupons من الـ API الحقيقي
  const { data: couponsData, isLoading } = useQuery({
    queryKey: ['coupons'],
    queryFn: () => apiClient.get('/vendors/api/coupons/').then(res => res.data)
  })

  // Mutations
  const toggleMutation = useMutation({
    mutationFn: (id: number) => apiClient.patch(`/vendors/api/coupons/${id}/toggle-status/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['coupons'] })
      toast.success('تم تحديث حالة الكوبون')
    }
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/vendors/api/coupons/${id}/`),
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
            كوبوناتي
          </h2>
          <p className="text-muted-foreground text-sm mt-2">عرض كوبونات الخصم المتاحة لك</p>
        </div>
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

                <div className="flex items-center gap-2 justify-center">
                  <button onClick={() => copyCode(coupon.code)} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-pink-500/10 hover:bg-pink-500/20 text-pink-400 text-xs font-bold transition-colors">
                    <Copy className="w-3 h-3" /> نسخ الكود
                  </button>
                </div>
              </div>
            )
          })}
        </div>

        {!isLoading && filteredCoupons.length === 0 && (
          <div className="text-center py-16">
            <Tag className="w-16 h-16 mx-auto text-muted-foreground opacity-20 mb-4" />
            <p className="text-muted-foreground text-lg">لا توجد كوبونات متاحة حالياً</p>
            <p className="text-sm text-muted-foreground mt-1">ستظهر الكوبونات المتاحة هنا عندما يوفرها التجار</p>
          </div>
        )}
      </div>
    </div>
  )
}
