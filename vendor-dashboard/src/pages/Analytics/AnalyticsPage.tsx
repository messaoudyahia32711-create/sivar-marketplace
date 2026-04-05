import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
  AreaChart, Area
} from 'recharts'
import { BarChart3, Package, Briefcase, TrendingUp } from 'lucide-react'
import { apiClient } from '../../api/client'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Skeleton } from '../../components/ui/skeleton'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316']

type PeriodType = '7d' | '30d' | '12m'

export default function AnalyticsPage() {
  const [period, setPeriod] = useState<PeriodType>('12m')

  const { data: productData, isPending: pLoading } = useQuery({
    queryKey: ['analytics-product', period],
    queryFn: () => apiClient.get(`/analytics/revenue/?period=${period}&type=product`).then(r => r.data)
  })

  const { data: serviceData, isPending: sLoading } = useQuery({
    queryKey: ['analytics-service', period],
    queryFn: () => apiClient.get(`/analytics/revenue/?period=${period}&type=service`).then(r => r.data)
  })

  const { data: topProducts, isPending: tpLoading } = useQuery({
    queryKey: ['top-products-analytics'],
    queryFn: () => apiClient.get('/analytics/top-products/?metric=quantity&limit=10').then(r => r.data)
  })

  const { data: topRevenue, isPending: trLoading } = useQuery({
    queryKey: ['top-products-revenue'],
    queryFn: () => apiClient.get('/analytics/top-products/?metric=revenue&limit=5').then(r => r.data)
  })

  const fmt = (val: any) => new Intl.NumberFormat('ar-DZ', { style: 'currency', currency: 'DZD' }).format(Number(val))
  
  const finalProductData = productData?.data || []
  const finalServiceData = serviceData?.data || []

  // Merge product + service for combined chart
  const mergedData = finalProductData.map((p: any, i: number) => ({
    label: p.label,
    products: p.revenue || 0,
    services: finalServiceData[i]?.revenue || 0,
  }))

  // Revenue distribution for pie chart
  const totalProd = (productData?.data || []).reduce((s: number, d: any) => s + Number(d.revenue || 0), 0)
  const totalServ = (serviceData?.data || []).reduce((s: number, d: any) => s + Number(d.revenue || 0), 0)
  const pieData = [
    { name: 'المنتجات', value: totalProd },
    { name: 'الخدمات', value: totalServ },
  ].filter(d => d.value > 0)

  return (
    <div className="space-y-6 animate-fade-in" dir="rtl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <BarChart3 className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-3xl font-black">التحليلات التفصيلية</h2>
            <p className="text-sm text-muted-foreground">تتبع أداء متجرك بدقة</p>
          </div>
        </div>
        <div className="flex items-center gap-1 p-1 glass rounded-xl">
          {(['7d', '30d', '12m'] as PeriodType[]).map(p => (
            <Button key={p} variant={period === p ? 'default' : 'ghost'} size="sm" className="rounded-lg h-8 px-4 text-xs" onClick={() => setPeriod(p)}>
              {p === '7d' ? '7 أيام' : p === '30d' ? '30 يوم' : '12 شهر'}
            </Button>
          ))}
        </div>
      </div>

      {/* ── Combined Revenue Chart ── */}
      <Card className="glass-card border-none col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <TrendingUp className="w-4 h-4 text-blue-400" /> مقارنة إيرادات المنتجات والخدمات
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[350px] w-full">
            {pLoading || sLoading ? <Skeleton className="h-full w-full rounded-xl" /> : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={mergedData}>
                  <defs>
                    <linearGradient id="gProd" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="gServ" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="label" fontSize={11} tickLine={false} axisLine={false} stroke="rgba(255,255,255,0.3)" />
                  <YAxis fontSize={11} tickLine={false} axisLine={false} stroke="rgba(255,255,255,0.3)" tickFormatter={v => `${v}`} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'rgba(15,23,42,0.95)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff' }}
                    formatter={(val: any, name: any) => [fmt(val), name === 'products' ? 'المنتجات' : 'الخدمات']}
                  />
                  <Area type="monotone" dataKey="products" stroke="#3b82f6" strokeWidth={2.5} fillOpacity={1} fill="url(#gProd)" name="products" />
                  <Area type="monotone" dataKey="services" stroke="#10b981" strokeWidth={2.5} fillOpacity={1} fill="url(#gServ)" name="services" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
          <div className="flex items-center gap-6 mt-4 justify-center">
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-blue-500" /><span className="text-xs text-muted-foreground">المنتجات</span></div>
            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-emerald-500" /><span className="text-xs text-muted-foreground">الخدمات</span></div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        {/* ── Top Products by Quantity ── */}
        <Card className="glass-card border-none">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Package className="w-4 h-4 text-violet-400" /> أكثر 10 منتجات مبيعاً
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[320px] w-full">
              {tpLoading ? <Skeleton className="h-full w-full rounded-xl" /> : topProducts?.results?.length === 0 ? (
                <div className="h-full flex items-center justify-center text-muted-foreground text-sm">لا توجد بيانات</div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={topProducts?.results} layout="vertical">
                    <XAxis type="number" hide />
                    <YAxis dataKey="name" type="category" fontSize={10} width={100} tickLine={false} axisLine={false} stroke="rgba(255,255,255,0.5)" />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff' }} />
                    <Bar dataKey="total_sold" radius={[0, 8, 8, 0]}>
                      {topProducts?.results?.map((_: any, idx: number) => (
                        <Cell key={idx} fill={COLORS[idx % COLORS.length]} fillOpacity={0.8} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </CardContent>
        </Card>

        {/* ── Revenue Distribution Pie ── */}
        <Card className="glass-card border-none">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Briefcase className="w-4 h-4 text-emerald-400" /> توزيع الإيرادات
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center">
            <div className="h-[260px] w-full max-w-[300px]">
              {pLoading || sLoading ? <Skeleton className="h-full w-full rounded-xl" /> : pieData.length === 0 ? (
                <div className="h-full flex items-center justify-center text-muted-foreground text-sm">لا توجد بيانات</div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={pieData} cx="50%" cy="50%" innerRadius={65} outerRadius={90} paddingAngle={5} dataKey="value" strokeWidth={0}>
                      {pieData.map((_, idx) => (
                        <Cell key={idx} fill={idx === 0 ? '#3b82f6' : '#10b981'} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff' }} formatter={(val: any) => fmt(val)} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
            <div className="flex gap-6 mt-2">
              <div className="text-center">
                <div className="flex items-center gap-2 mb-1"><div className="w-3 h-3 rounded-full bg-blue-500" /><span className="text-xs text-muted-foreground">المنتجات</span></div>
                <p className="font-bold text-sm">{fmt(totalProd)}</p>
              </div>
              <div className="text-center">
                <div className="flex items-center gap-2 mb-1"><div className="w-3 h-3 rounded-full bg-emerald-500" /><span className="text-xs text-muted-foreground">الخدمات</span></div>
                <p className="font-bold text-sm">{fmt(totalServ)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* ── Top Products by Revenue ── */}
      <Card className="glass-card border-none">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <TrendingUp className="w-4 h-4 text-yellow-400" /> أعلى 5 منتجات إيراداً
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {trLoading ? Array(5).fill(0).map((_, i) => <Skeleton key={i} className="h-12 w-full rounded-xl" />) : (
              topRevenue?.results?.map((p: any, idx: number) => {
                const maxRev = topRevenue.results[0]?.total_revenue || 1
                const pct = Math.round((p.total_revenue / maxRev) * 100)
                return (
                  <div key={p.id} className="flex items-center gap-4 p-3 rounded-xl hover:bg-white/5 transition-all">
                    <span className="text-lg font-black text-muted-foreground w-6">{idx + 1}</span>
                    <div className="flex-1 min-w-0">
                      <p className="font-bold text-sm truncate">{p.name}</p>
                      <div className="w-full h-2 bg-white/5 rounded-full mt-2 overflow-hidden">
                        <div className="h-full rounded-full bg-gradient-to-l from-yellow-500 to-orange-500 transition-all" style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                    <span className="font-bold text-sm text-yellow-400 shrink-0">{fmt(p.total_revenue)}</span>
                  </div>
                )
              })
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
