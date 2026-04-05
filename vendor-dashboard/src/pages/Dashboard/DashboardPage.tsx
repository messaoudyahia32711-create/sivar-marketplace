import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  TrendingUp, ShoppingBag, Star, Package, 
  Users, Clock, Briefcase, AlertTriangle, ShoppingCart
} from 'lucide-react'
import { 
  XAxis, Tooltip, ResponsiveContainer, AreaChart, Area 
} from 'recharts'
import { apiClient } from '../../api/client'
import { KpiCard } from '../../components/shared/KpiCard'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { Badge } from '../../components/ui/badge'
import { useNewOrdersNotifier } from '../../hooks/useNewOrdersNotifier'
import { Skeleton } from '../../components/ui/skeleton'
import { StatusBadge } from '../../components/shared/StatusBadge'

type PeriodType = '7d' | '30d' | '12m'

export default function DashboardPage() {
  useNewOrdersNotifier()
  const [chartPeriod, setChartPeriod] = useState<PeriodType>('30d')

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
      <div className="flex items-center justify-between relative z-10">
        <div>
          <h2 className="text-3xl font-black">
            مرحباً، <span className="gradient-text">{stats?.store?.name || 'أيها التاجر'}</span> 👋
          </h2>
          <p className="text-muted-foreground mt-1 text-sm">إليك ملخص شامل لنشاط متجرك.</p>
        </div>
      </div>

      {/* ── Row 1: 8 KPI Cards ── */}
      <div className="grid gap-4 grid-cols-2 lg:grid-cols-4 relative z-10">
        <KpiCard 
          title="أرباح المنتجات" 
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
        <KpiCard 
          title="الخدمات النشطة" 
          value={stats?.total?.services || 0} 
          loading={statsLoading}
          icon={<Briefcase className="w-5 h-5 text-teal-400" />}
        />
      </div>

      {/* ── Row 2: Period Selector + Charts ── */}
      <div className="relative z-10 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold">تحليل الإيرادات</h3>
          <div className="flex items-center gap-1 p-1 glass rounded-xl">
            {(['7d', '30d', '12m'] as PeriodType[]).map(p => (
              <Button key={p} variant={chartPeriod === p ? 'default' : 'ghost'} size="sm" className="rounded-lg h-8 px-4 text-xs"
                onClick={() => setChartPeriod(p)}
              >
                {p === '7d' ? '7 أيام' : p === '30d' ? '30 يوم' : '12 شهر'}
              </Button>
            ))}
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Product Revenue Chart */}
          <Card className="glass-card border-none overflow-hidden group">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-base font-bold flex items-center gap-2">
                <Package className="w-4 h-4 text-blue-400" /> مبيعات المنتجات
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[280px] w-full mt-2" style={{ minWidth: 0, minHeight: 0 }}>
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
              <div className="h-[280px] w-full mt-2" style={{ minWidth: 0, minHeight: 0 }}>
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
                <span className="text-3xl font-black text-yellow-400">{stats?.total?.avg_rating ? stats.total.avg_rating : '0.0'}</span>
              </div>
              <div className="flex-1">
                <p className="font-bold text-lg">تقييم المتجر العام</p>
                <p className="text-sm text-muted-foreground">{stats?.total?.avg_rating ? 'بناءً على مراجعات العملاء' : 'بدون تقييم حتى الآن'}</p>
                <div className="flex items-center gap-1 mt-2">
                  {Array(5).fill(0).map((_, i) => (
                    <Star key={i} className={`w-4 h-4 ${stats?.total?.avg_rating && i < Math.round(stats.total.avg_rating) ? 'text-yellow-400 fill-yellow-400' : 'text-gray-600'}`} />
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
