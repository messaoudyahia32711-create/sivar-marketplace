import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, LineChart, Line,
  AreaChart, Area, Cell
} from 'recharts'
import { BarChart3, TrendingUp, Building2, Activity } from 'lucide-react'
import { apiClient } from '../../api/client'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Skeleton } from '../../components/ui/skeleton'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316']


export default function AnalyticsPage() {
  const [period, setPeriod] = useState('12m')

  const { data: analytics, isLoading } = useQuery({
    queryKey: ['incubator-analytics', period],
    queryFn: () => apiClient.get(`/incubator/analytics/?period=${period}`).then(r => r.data)
  })

  const growthData = analytics?.growth || []
  const performanceLines = analytics?.performance_lines || []

  return (
    <div className="space-y-6 animate-fade-in" dir="rtl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <BarChart3 className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-3xl font-black">تحليلات الاحتضان</h2>
            <p className="text-sm text-muted-foreground">متابعة دقيقة لنمو وأداء المؤسسات الناشئة</p>
          </div>
        </div>
        <div className="flex items-center gap-1 p-1 glass rounded-xl">
          {['30d', '12m'].map(p => (
            <Button key={p} variant={period === p ? 'default' : 'ghost'} size="sm" className="rounded-lg h-8 px-4 text-xs" onClick={() => setPeriod(p)}>
              {p === '30d' ? '30 يوم' : '12 شهر'}
            </Button>
          ))}
        </div>
      </div>

      {/* ── Performance Comparison (Multi-line) ── */}
      <Card className="glass-card border-none">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Activity className="w-4 h-4 text-blue-400" /> مقارنة أداء المؤسسات الكبرى
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px] w-full mt-4">
            {isLoading ? <Skeleton className="h-full w-full rounded-xl" /> : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                  <XAxis 
                    dataKey="month" 
                    allowDuplicatedCategory={false} 
                    fontSize={11} 
                    tickLine={false} 
                    axisLine={false} 
                    stroke="rgba(255,255,255,0.3)"
                    tickFormatter={(val) => val.split('-')[1]}
                  />
                  <YAxis fontSize={11} tickLine={false} axisLine={false} stroke="rgba(255,255,255,0.3)" domain={[0, 100]} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'rgba(15,23,42,0.95)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff' }}
                  />
                  {performanceLines.map((line: any, idx: number) => (
                    <Line 
                      key={line.name}
                      data={line.data}
                      type="monotone"
                      dataKey="score"
                      name={line.name}
                      stroke={COLORS[idx % COLORS.length]}
                      strokeWidth={3}
                      dot={{ r: 4, strokeWidth: 2, fill: '#0f172a' }}
                      activeDot={{ r: 6, strokeWidth: 0 }}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        {/* ── Incubation Growth (Area Chart) ── */}
        <Card className="glass-card border-none">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <TrendingUp className="w-4 h-4 text-emerald-400" /> نمو الاحتضان والمبيعات
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full">
              {isLoading ? <Skeleton className="h-full w-full rounded-xl" /> : (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={growthData}>
                    <defs>
                      <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="label" fontSize={11} tickLine={false} axisLine={false} stroke="rgba(255,255,255,0.3)" tickFormatter={(val) => val.split('-')[1]} />
                    <YAxis fontSize={11} tickLine={false} axisLine={false} stroke="rgba(255,255,255,0.3)" hide />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff' }} />
                    <Area type="monotone" dataKey="total_orgs" stroke="#3b82f6" fillOpacity={0} name="إجمالي المؤسسات" strokeWidth={2} />
                    <Area type="monotone" dataKey="revenue" stroke="#10b981" fillOpacity={1} fill="url(#colorRevenue)" name="المبيعات (د.ج)" strokeWidth={3} />
                    <Area type="monotone" dataKey="orders" stroke="#f59e0b" name="الطلبات" fillOpacity={0} strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              )}
            </div>
          </CardContent>
        </Card>

        {/* ── Key Entities Distribution (Top Orgs) ── */}
        <Card className="glass-card border-none">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Building2 className="w-4 h-4 text-amber-400" /> توزيع أداء المؤسسات الحقيقي
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full">
              {isLoading ? <Skeleton className="h-full w-full rounded-xl" /> : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={performanceLines.map((l: any) => ({ name: l.name, score: l.data[l.data.length - 1].score }))} layout="vertical">
                    <XAxis type="number" domain={[0, 100]} hide />
                    <YAxis dataKey="name" type="category" fontSize={10} width={80} tickLine={false} axisLine={false} stroke="rgba(255,255,255,0.5)" />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff' }} />
                    <Bar dataKey="score" radius={[0, 8, 8, 0]} name="درجة الأداء">
                      {performanceLines.map((_: any, idx: number) => (
                        <Cell key={idx} fill={COLORS[idx % COLORS.length]} fillOpacity={0.8} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
