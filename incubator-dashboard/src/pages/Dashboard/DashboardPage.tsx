import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { 
  TrendingUp, Users, AlertTriangle, Building2, ClipboardList, Star
} from 'lucide-react'
import { 
  XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area, LineChart, Line, CartesianGrid 
} from 'recharts'
import { apiClient } from '../../api/client'
import { KpiCard } from '../../components/shared/KpiCard'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { useAuth } from '../../hooks/useAuth'
import { useNewOrdersNotifier } from '../../hooks/useNewOrdersNotifier'
import { Skeleton } from '../../components/ui/skeleton'
import { StatusBadge } from '../../components/shared/StatusBadge'


type PeriodType = '7d' | '30d' | '12m'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { getUser } = useAuth()
  const user = getUser()
  useNewOrdersNotifier()
  const [chartPeriod, setChartPeriod] = useState<PeriodType>('30d')

  const { data: incubatorStats, isPending: statsLoading } = useQuery({
    queryKey: ['incubator-stats'],
    queryFn: () => apiClient.get('/incubator/stats/').then(res => res.data)
  })

  const { data: analytics, isPending: analyticsLoading } = useQuery({
    queryKey: ['incubator-analytics', chartPeriod],
    queryFn: () => apiClient.get(`/incubator/analytics/?period=${chartPeriod}`).then(res => res.data)
  })

  const { data: recentRequests, isPending: requestsLoading } = useQuery({
    queryKey: ['recent-requests'],
    queryFn: () => apiClient.get('/incubator/organization-requests/').then(res => res.data)
  })

  const growthData = analytics?.growth || []
  const performanceLines = analytics?.performance_lines || []
  const displayTopPerformers = incubatorStats?.top_performers || []

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
            مرحباً، <span className="gradient-text">{user?.username || 'مدير الحاضنة'}</span> 👋
          </h2>
          <p className="text-muted-foreground mt-1 text-sm">إليك نظرة عامة على أداء المؤسسات المحتضنة.</p>
        </div>
      </div>

      {/* ── Row 1: 3 Main Performance KPI Cards ── */}
      <div className="grid gap-4 grid-cols-1 md:grid-cols-3 relative z-10">
        <KpiCard 
          title="مبيعات المعارض الموحدة" 
          value={`${(incubatorStats?.stats?.total_revenue || 0).toLocaleString()} د.ج`}
          loading={statsLoading}
          icon={<TrendingUp className="w-5 h-5 text-emerald-400" />}
          glowColor="glow-emerald"
          description="إجمالي المداخيل المحققة من كافة معارض المؤسسات"
        />
        <KpiCard 
          title="إجمالي المعروضات" 
          value={incubatorStats?.stats?.gallery_items || 0} 
          loading={statsLoading}
          icon={<ClipboardList className="w-5 h-5 text-blue-400" />}
          glowColor="glow-blue"
          description="عدد المنتجات والخدمات النشطة في المعارض"
        />
        <KpiCard 
          title="إجمالي العمليات" 
          value={incubatorStats?.stats?.total_orders || 0} 
          loading={statsLoading}
          icon={<Star className="w-5 h-5 text-amber-400" />}
          glowColor="glow-orange"
          description="عدد طلبات الشراء المكتملة"
        />
      </div>

      {/* ── Row 2: 4 Secondary Stats ── */}
      <div className="grid gap-4 grid-cols-2 lg:grid-cols-4 relative z-10">
        <KpiCard 
          title="المؤسسات المحتضنة" 
          value={incubatorStats?.stats?.total_orgs || 0} 
          loading={statsLoading}
          icon={<Building2 className="w-4 h-4 text-blue-400" />}
          variant="secondary"
        />
        <KpiCard 
          title="متوسط الأداء" 
          value={`${incubatorStats?.stats?.avg_performance || 0}%`} 
          loading={statsLoading}
          icon={<TrendingUp className="w-4 h-4 text-emerald-400" />}
          variant="secondary"
        />
        <KpiCard 
          title="المؤسسات النشطة" 
          value={incubatorStats?.stats?.active_orgs || 0} 
          loading={statsLoading}
          icon={<Users className="w-4 h-4 text-violet-400" />}
          variant="secondary"
        />
        <KpiCard 
          title="تحت المراجعة" 
          value={incubatorStats?.stats?.weak_orgs || 0} 
          loading={statsLoading}
          icon={<AlertTriangle className="w-4 h-4 text-orange-400" />}
          variant="secondary"
        />
      </div>

      {/* ── Row 3: Period Selector + Charts ── */}
      <div className="relative z-10 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold">تحليل مؤشرات المعارض والاحتضان</h3>
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
          {/* Performance Comparison (Multi-line) */}
          <Card className="glass-card border-none overflow-hidden group">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-base font-bold flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-blue-400" /> مقارنة نمو أداء المؤسسات
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[280px] w-full mt-2" style={{ minWidth: 0, minHeight: 0 }}>
                {analyticsLoading ? <Skeleton className="h-full w-full rounded-xl" /> : (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                      <XAxis 
                        dataKey="month" 
                        fontSize={10} 
                        tickLine={false} 
                        axisLine={false} 
                        stroke="rgba(255,255,255,0.3)" 
                        tickFormatter={(val) => val.split('-')[1]} // Show month only
                      />
                      <YAxis domain={[0, 100]} hide />
                      <Tooltip 
                        contentStyle={{ backgroundColor: 'rgba(15,23,42,0.9)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff' }}
                      />
                      {performanceLines?.map((line: any, idx: number) => (
                        <Line 
                          key={line.name}
                          type="monotone" 
                          data={line.data} 
                          dataKey="score" 
                          name={line.name}
                          stroke={['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'][idx % 5]} 
                          strokeWidth={3} 
                          dot={false}
                        />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Revenue & Growth Chart */}
          <Card className="glass-card border-none overflow-hidden group">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-base font-bold flex items-center gap-2">
                <Users className="w-4 h-4 text-emerald-400" /> نمو المبيعات والانتساب
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[280px] w-full mt-2" style={{ minWidth: 0, minHeight: 0 }}>
                {analyticsLoading ? <Skeleton className="h-full w-full rounded-xl" /> : (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={growthData}>
                      <defs>
                        <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                        </linearGradient>
                        <linearGradient id="colorOrgs" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <XAxis 
                        dataKey="label" 
                        fontSize={10} 
                        tickLine={false} 
                        axisLine={false} 
                        stroke="rgba(255,255,255,0.3)"
                        tickFormatter={(val) => val.split('-')[1]}
                      />
                      <YAxis hide />
                      <Tooltip 
                        contentStyle={{ backgroundColor: 'rgba(15,23,42,0.9)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff' }}
                      />
                      <Area type="monotone" dataKey="revenue" name="المبيعات (د.ج)" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorRevenue)" />
                      <Area type="monotone" dataKey="total_orgs" name="إجمالي المؤسسات" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorOrgs)" />
                      <Area type="monotone" dataKey="orders" name="الطلبات" stroke="#f59e0b" strokeWidth={2} fill="transparent" />
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
              <Star className="w-4 h-4 text-yellow-400" /> ترتيب المؤسسات حسب الأداء
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {statsLoading ? (
                Array(4).fill(0).map((_, i) => <Skeleton key={i} className="h-14 w-full rounded-xl" />)
              ) : displayTopPerformers.length === 0 ? (
                <p className="text-center text-muted-foreground py-8 text-sm">لا توجد مؤسسات بعد</p>
              ) : (
                displayTopPerformers.map((org: any, idx: number) => (
                  <div key={org.id} className="flex items-center p-3 rounded-xl hover:bg-white/5 transition-all group">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500/20 to-violet-500/20 flex items-center justify-center font-black text-sm text-blue-400 shrink-0">
                      {idx + 1}
                    </div>
                    <div className="mr-3 flex-1 min-w-0">
                      <p className="font-bold text-sm truncate">{org.first_name || org.username}</p>
                      <p className="text-[11px] text-muted-foreground">{org.university_name}</p>
                    </div>
                    <div className="text-left shrink-0">
                      <p className="font-bold text-sm text-blue-400">{org.performance_score}%</p>
                      <div className="flex items-center gap-1 text-[10px] text-yellow-500 justify-end">
                        <Star className="w-2.5 h-2.5 fill-current" />
                        <span>تقييم الأداء</span>
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
              <ClipboardList className="w-4 h-4 text-amber-400" /> طلبات الانضمام الأخيرة
            </CardTitle>
            <Button variant="ghost" size="sm" className="text-xs rounded-lg" onClick={() => navigate('/join-requests')}>
              عرض الكل
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {requestsLoading ? (
                Array(4).fill(0).map((_, i) => <Skeleton key={i} className="h-14 w-full rounded-xl" />)
              ) : recentRequests?.results?.filter((req: any) => req.status === 'pending').length === 0 ? (
                <p className="text-center text-muted-foreground py-8 text-sm">لا توجد طلبات بعد</p>
              ) : (
                recentRequests?.results?.filter((req: any) => req.status === 'pending').slice(0, 5).map((req: any) => (
                  <div key={req.id} className="flex items-center justify-between p-3 rounded-xl hover:bg-white/5 transition-all">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                        <span className="text-xs font-bold text-amber-400">#{req.id}</span>
                      </div>
                      <div>
                        <p className="font-bold text-sm">{req.name}</p>
                        <p className="text-[11px] text-muted-foreground">{req.sector}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <StatusBadge status={req.status} />
                      <span className="text-[10px] text-muted-foreground">
                        {new Date(req.created_at).toLocaleDateString('ar-DZ')}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

    </div>
  )
}
