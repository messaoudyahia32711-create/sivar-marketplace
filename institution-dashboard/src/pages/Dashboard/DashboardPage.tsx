import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  TrendingUp, ShoppingBag, Star, Package, 
  Users, Clock, Briefcase, AlertTriangle, ShoppingCart, 
  Building2, CheckCircle2, ArrowRightCircle, Sparkles, Trophy, X
} from 'lucide-react'
import { 
  XAxis, Tooltip, ResponsiveContainer, AreaChart, Area 
} from 'recharts'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../../api/client'
import { KpiCard } from '../../components/shared/KpiCard'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { useNewOrdersNotifier } from '../../hooks/useNewOrdersNotifier'
import { Skeleton } from '../../components/ui/skeleton'
import { StatusBadge } from '../../components/shared/StatusBadge'

type PeriodType = '7d' | '30d' | '12m'

export default function DashboardPage() {
  useNewOrdersNotifier()
  const navigate = useNavigate()
  const [chartPeriod, setChartPeriod] = useState<PeriodType>('30d')
  const [showIdentityModal, setShowIdentityModal] = useState(false)

  const { data: stats, isPending: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => apiClient.get('/dashboard/').then(res => res.data)
  })

  const { data: productRevenue, isPending: productRevenueLoading } = useQuery({
    queryKey: ['revenue-analytics', 'product', chartPeriod],
    queryFn: () => apiClient.get(`/analytics/revenue/?period=${chartPeriod}&type=product`).then(res => res.data)
  })

  const { data: serviceRevenue, isPending: serviceRevenueLoading } = useQuery({
    queryKey: ['revenue-analytics', 'service', chartPeriod],
    queryFn: () => apiClient.get(`/analytics/revenue/?period=${chartPeriod}&type=service`).then(res => res.data)
  })

  const { data: topProducts, isPending: productsLoading } = useQuery({
    queryKey: ['top-products'],
    queryFn: () => apiClient.get('/analytics/top-products/').then(res => res.data)
  })

  const { data: recentOrders, isPending: ordersLoading } = useQuery({
    queryKey: ['recent-orders'],
    queryFn: () => apiClient.get('/orders/?page_size=5').then(res => res.data)
  })

  const fmt = (val: string | number) => 
    new Intl.NumberFormat('ar-DZ', { style: 'currency', currency: 'DZD' }).format(Number(val))


  const productChartData = productRevenue?.data || []
  const serviceChartData = serviceRevenue?.data || []

  return (
    <div className="space-y-6 relative animate-fade-in" dir="rtl">
      {/* Background Decorations */}
      <div className="absolute -top-24 -right-24 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl animate-blob opacity-50 pointer-events-none" />
      <div className="absolute top-1/2 -left-24 w-72 h-72 bg-violet-500/5 rounded-full blur-3xl animate-blob animation-delay-2000 opacity-50 pointer-events-none" />
      <div className="absolute bottom-0 right-1/3 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl animate-blob animation-delay-4000 opacity-50 pointer-events-none" />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
        <div>
          <h2 className="text-3xl font-black">
            مرحباً، <span className="gradient-text">{stats?.store?.name || 'أيها المدير'}</span> 👋
          </h2>
          <p className="text-muted-foreground mt-1 text-sm">إليك ملخص شامل لأداء وتغطية مؤسستك اليوم.</p>
        </div>

        {/* ماذا تفعل الآن - الخطوة العملية */}
        <div className="glass-card border-l-4 border-l-blue-500 p-4 flex items-center gap-4 animate-glow">
          <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center shrink-0">
            <Sparkles className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <p className="text-[10px] text-blue-400 font-bold uppercase tracking-wider">ماذا تفعل الآن؟ (خطوة عملية)</p>
            <h4 className="font-bold text-sm">تحديث بيانات أعضاء الفريق الجدد</h4>
            <button 
              onClick={() => navigate('/team')}
              className="text-[11px] text-blue-400 flex items-center gap-1 mt-1 hover:underline active:scale-95 transition-transform"
            >
              انتقل للخطوة <ArrowRightCircle className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      {/* Identity Modal Overlay */}
      {showIdentityModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in zoom-in duration-200">
          <Card className="w-full max-w-lg glass-card border-white/10 shadow-2xl overflow-hidden">
            <div className="h-2 bg-gradient-to-r from-indigo-500 to-blue-500" />
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Building2 className="w-5 h-5 text-indigo-400" /> الملف القانوني للمؤسسة
              </CardTitle>
              <Button variant="ghost" size="icon" onClick={() => setShowIdentityModal(false)}>
                <X className="w-4 h-4" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 rounded-lg bg-white/5 space-y-1">
                  <p className="text-[10px] text-muted-foreground uppercase">الرقم الضريبي (NIF)</p>
                  <p className="font-mono text-sm">0001234567890123</p>
                </div>
                <div className="p-3 rounded-lg bg-white/5 space-y-1">
                  <p className="text-[10px] text-muted-foreground uppercase">رقم السجل التجاري</p>
                  <p className="font-mono text-sm">24/00-1234567B21</p>
                </div>
              </div>
              <div className="p-4 rounded-xl border border-emerald-500/20 bg-emerald-500/5 flex items-start gap-3">
                  <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  </div>
                  <div>
                    <p className="font-bold text-emerald-400 text-sm">المؤسسة موثقة رسمياً</p>
                    <p className="text-xs text-emerald-400/70">تم التحقق من كافة المستندات القانونية. المؤسسة مؤهلة للمشاركة في المناقصات والمعارض الكبرى.</p>
                  </div>
              </div>
              <Button className="w-full bg-indigo-600 hover:bg-indigo-700">تحديث المستندات</Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ── Row 1: 8 KPI Cards ── */}
      <div className="grid gap-4 grid-cols-2 lg:grid-cols-4 relative z-10">
        <KpiCard 
          title="إجمالي الأداء" 
          value={`${stats?.performance_score || 0}%`} 
          loading={statsLoading}
          icon={<Trophy className="w-5 h-5 text-yellow-400" />}
          subtitle="معدل إنجاز المهام"
          glowColor="glow-orange"
        />
        <KpiCard 
          title="إيرادات المنتجات" 
          value={fmt(stats?.total?.product_revenue || 0)} 
          loading={statsLoading}
          icon={<Package className="w-5 h-5 text-blue-400" />}
          change_pct={stats?.this_month?.revenue_change_pct}
          glowColor="glow-blue"
        />
        <KpiCard 
          title="أرباح الخدمات" 
          value={fmt(stats?.total?.service_revenue || 0)} 
          loading={statsLoading}
          icon={<Briefcase className="w-5 h-5 text-emerald-400" />}
          glowColor="glow-emerald"
        />
        <KpiCard 
          title="إجمالي الطلبات" 
          value={stats?.total?.orders || 0} 
          subtitle={`هذا الشهر: ${stats?.this_month?.orders || 0}`}
          loading={statsLoading}
          icon={<ShoppingCart className="w-5 h-5 text-violet-400" />}
          change_pct={stats?.this_month?.orders_change_pct}
          glowColor="glow-purple"
        />
        <KpiCard 
          title="مخزون حرج" 
          value={stats?.low_stock_count || 0} 
          loading={statsLoading}
          variant={stats?.low_stock_count > 0 ? 'warning' : 'default'}
          icon={<AlertTriangle className="w-5 h-5 text-orange-400" />}
          glowColor="glow-orange"
        />
        <KpiCard 
          title="طلبات اليوم" 
          value={stats?.today?.orders || 0} 
          subtitle={`إيراد اليوم: ${fmt(stats?.today?.revenue || 0)}`}
          loading={statsLoading}
          icon={<Clock className="w-5 h-5 text-cyan-400" />}
        />
        <KpiCard 
          title="عملاء جُدد اليوم" 
          value={stats?.today?.new_customers || 0} 
          loading={statsLoading}
          icon={<Users className="w-5 h-5 text-pink-400" />}
        />
        <KpiCard 
          title="المنتجات النشطة" 
          value={stats?.total?.products || 0} 
          loading={statsLoading}
          icon={<Package className="w-5 h-5 text-indigo-400" />}
        />
      </div>

      {/* ── Row 2: Institution Identity & Stats ── */}
      <div className="grid gap-6 md:grid-cols-3 relative z-10">
        {/* Institution Identity Card */}
        <Card className="glass-card border-none overflow-hidden col-span-1 border-r-4 border-r-indigo-500/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-bold flex items-center gap-2">
              <Building2 className="w-4 h-4 text-indigo-400" /> هوية المؤسسة
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/5">
               <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                 <Building2 className="w-8 h-8 text-white" />
               </div>
               <div>
                  <p className="font-bold text-sm">{stats?.store?.name || 'مؤسستك'}</p>
                  <p className="text-[11px] text-indigo-400">ID: INS-{new Date().getFullYear()}-{stats?.store?.id || '001'}</p>
               </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-muted-foreground">حالة التوثيق</span>
                <span className="text-emerald-400 font-bold flex items-center gap-1">موثقة <CheckCircle2 className="w-3 h-3" /></span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-muted-foreground">تاريخ الانضمام</span>
                <span>{stats?.store?.created_at ? new Date(stats.store.created_at).toLocaleDateString('ar-DZ') : '—'}</span>
              </div>
            </div>
            <Button 
              onClick={() => setShowIdentityModal(true)}
              variant="secondary" 
              className="w-full h-8 text-[11px] rounded-lg hover:bg-indigo-500 hover:text-white transition-colors"
            >
              إدارة الملف القانوني
            </Button>
          </CardContent>
        </Card>

        <div className="md:col-span-2 space-y-4">
            {/* Period Selector */}
            <div className="flex items-center justify-end gap-1 p-1 glass rounded-xl w-fit mr-auto">
              {(['7d', '30d', '12m'] as PeriodType[]).map(p => (
                <Button key={p} variant={chartPeriod === p ? 'default' : 'ghost'} size="sm" className="rounded-lg h-7 px-3 text-[10px]"
                  onClick={() => setChartPeriod(p)}
                >
                  {p === '7d' ? '7 أيام' : p === '30d' ? '30 يوم' : '12 شهر'}
                </Button>
              ))}
            </div>

            {/* Revenue Analytics charts */}
            <div className="grid gap-4 md:grid-cols-2">
             {/* Product Revenue Chart */}
             <Card className="glass-card border-none overflow-hidden group">
               <CardHeader className="flex flex-row items-center justify-between pb-2">
                 <CardTitle className="text-base font-bold flex items-center gap-2">
                   <Package className="w-4 h-4 text-blue-400" /> مبيعات المنتجات
                 </CardTitle>
               </CardHeader>
               <CardContent>
                 <div className="h-[200px] w-full mt-2" style={{ minWidth: 0, minHeight: 0 }}>
                   {productRevenueLoading ? <Skeleton className="h-full w-full rounded-xl" /> : (
                     <ResponsiveContainer width="100%" height="100%">
                       <AreaChart data={productChartData}>
                         <defs>
                           <linearGradient id="colorProd" x1="0" y1="0" x2="0" y2="1">
                             <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                             <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                           </linearGradient>
                         </defs>
                         <XAxis dataKey="label" hide />
                         <Tooltip 
                           contentStyle={{ backgroundColor: 'rgba(15,23,42,0.9)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff' }}
                           formatter={(val: any) => [fmt(val), 'المنتجات']}
                         />
                         <Area type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorProd)" />
                       </AreaChart>
                     </ResponsiveContainer>
                   )}
                 </div>
               </CardContent>
             </Card>

             {/* Service Revenue Chart */}
             <Card className="glass-card border-none overflow-hidden group">
               <CardHeader className="flex flex-row items-center justify-between pb-2">
                 <CardTitle className="text-base font-bold flex items-center gap-2">
                   <Briefcase className="w-4 h-4 text-emerald-400" /> مبيعات الخدمات
                 </CardTitle>
               </CardHeader>
               <CardContent>
                 <div className="h-[200px] w-full mt-2" style={{ minWidth: 0, minHeight: 0 }}>
                   {serviceRevenueLoading ? <Skeleton className="h-full w-full rounded-xl" /> : (
                     <ResponsiveContainer width="100%" height="100%">
                       <AreaChart data={serviceChartData}>
                         <defs>
                           <linearGradient id="colorServ" x1="0" y1="0" x2="0" y2="1">
                             <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                             <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                           </linearGradient>
                         </defs>
                         <XAxis dataKey="label" hide />
                         <Tooltip 
                           contentStyle={{ backgroundColor: 'rgba(15,23,42,0.9)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff' }}
                           formatter={(val: any) => [fmt(val), 'الخدمات']}
                         />
                         <Area type="monotone" dataKey="revenue" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorServ)" />
                       </AreaChart>
                     </ResponsiveContainer>
                   )}
                 </div>
               </CardContent>
             </Card>
           </div>
        </div>
      </div>

      {/* ── Row 3: Top Products & Recent Orders ── */}
      <div className="grid gap-6 md:grid-cols-2 relative z-10">
        {/* Top Products */}
        <Card className="glass-card border-none">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base font-bold flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-yellow-400" /> أعلى المنتجات أداءً
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {productsLoading ? (
                Array(4).fill(0).map((_, i) => <Skeleton key={i} className="h-14 w-full rounded-xl" />)
              ) : topProducts?.results?.length === 0 ? (
                <p className="text-center text-muted-foreground py-8 text-sm">لا توجد منتجات بعد</p>
              ) : (
                topProducts?.results?.map((product: any, idx: number) => (
                  <div key={product.id} className="flex items-center p-3 rounded-xl hover:bg-white/5 transition-all group">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500/20 to-violet-500/20 flex items-center justify-center font-black text-sm text-blue-400 shrink-0">
                      {idx + 1}
                    </div>
                    <div className="mr-3 flex-1 min-w-0">
                      <p className="font-bold text-sm truncate">{product.name}</p>
                      <p className="text-[11px] text-muted-foreground">{product.total_sold} مبيعة</p>
                    </div>
                    <div className="text-left shrink-0">
                      <p className="font-bold text-sm text-blue-400">{fmt(product.total_revenue)}</p>
                      <div className="flex items-center gap-1 text-[10px] text-yellow-500 justify-end">
                        <Star className="w-2.5 h-2.5 fill-current" />
                        <span>{product.avg_rating || '—'}</span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Recent Orders */}
        <Card className="glass-card border-none">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base font-bold flex items-center gap-2">
              <ShoppingBag className="w-4 h-4 text-amber-400" /> آخر الطلبات
            </CardTitle>
            <Button variant="ghost" size="sm" className="text-xs rounded-lg" onClick={() => window.location.href = '/vendor-dashboard/orders'}>
              عرض الكل
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {ordersLoading ? (
                Array(4).fill(0).map((_, i) => <Skeleton key={i} className="h-14 w-full rounded-xl" />)
              ) : recentOrders?.results?.length === 0 ? (
                <p className="text-center text-muted-foreground py-8 text-sm">لا توجد طلبات بعد</p>
              ) : (
                recentOrders?.results?.slice(0, 5).map((order: any) => (
                  <div key={order.id} className="flex items-center justify-between p-3 rounded-xl hover:bg-white/5 transition-all">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                        <span className="text-xs font-bold text-amber-400">#{order.id}</span>
                      </div>
                      <div>
                        <p className="font-bold text-sm">{order.customer_name}</p>
                        <p className="text-[11px] text-muted-foreground">
                          {new Date(order.created_at).toLocaleDateString('ar-DZ', { day: 'numeric', month: 'short' })}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <StatusBadge status={order.status} />
                      <span className="font-bold text-sm">{fmt(order.vendor_subtotal)}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* ── Row 4: Store Rating ── */}
      <div className="relative z-10">
        <Card className="glass-card border-none">
          <CardContent className="p-6">
            <div className="flex items-center gap-6">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-yellow-500/20 to-orange-500/20 flex items-center justify-center relative">
                <span className="text-3xl font-black text-yellow-400">{stats?.total?.avg_rating || '5.0'}</span>
              </div>
              <div className="flex-1">
                <p className="font-bold text-lg">تقييم المؤسسة العام</p>
                <p className="text-sm text-muted-foreground">بناءً على مراجعات العملاء والمستفيدين</p>
                <div className="flex items-center gap-1 mt-2">
                  {Array(5).fill(0).map((_, i) => (
                    <Star key={i} className={`w-4 h-4 ${i < Math.round(stats?.total?.avg_rating || 5) ? 'text-yellow-400 fill-yellow-400' : 'text-gray-600'}`} />
                  ))}
                </div>
              </div>
              <div className="hidden md:flex gap-4">
                <div className="text-center">
                  <p className="text-2xl font-black">{stats?.pending_orders_count || 0}</p>
                  <p className="text-xs text-muted-foreground">طلب معلق</p>
                </div>
                <div className="w-px bg-white/10" />
                <div className="text-center">
                  <p className="text-2xl font-black">{stats?.total?.products || 0}</p>
                  <p className="text-xs text-muted-foreground">منتج</p>
                </div>
                <div className="w-px bg-white/10" />
                <div className="text-center">
                  <p className="text-2xl font-black">{stats?.total?.services || 0}</p>
                  <p className="text-xs text-muted-foreground">خدمة</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
