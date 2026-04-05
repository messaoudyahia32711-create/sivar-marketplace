import { useQuery } from '@tanstack/react-query'
import { ShoppingBag, ShoppingCart, Clock, CheckCircle } from 'lucide-react'
import { apiClient } from '../../api/client'
import { KpiCard } from '../../components/shared/KpiCard'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { StatusBadge } from '../../components/shared/StatusBadge'
import { Skeleton } from '../../components/ui/skeleton'
import { useAuth } from '../../hooks/useAuth'

export default function DashboardPage() {
  const { getUser } = useAuth()
  const user = getUser()

  const { data: recentOrders, isPending: ordersLoading } = useQuery({
    queryKey: ['my-recent-orders'],
    queryFn: () => apiClient.get('/orders/').then(res => res.data)
  })

  // Calculate simple stats from the first page of orders (or all if unpaginated)
  const ordersList = recentOrders?.orders || recentOrders?.results || recentOrders || []
  const totalOrders = ordersList.length
  const completedOrders = ordersList.filter((o: any) => o.status === 'DELIVERED').length
  const pendingOrders = ordersList.filter((o: any) => ['PENDING', 'PROCESSING', 'SHIPPED'].includes(o.status)).length

  const fmt = (val: string | number) => 
    new Intl.NumberFormat('ar-DZ', { style: 'currency', currency: 'DZD' }).format(Number(val))

  return (
    <div className="space-y-6 relative animate-fade-in" dir="rtl">
      {/* Background Decorations */}
      <div className="absolute -top-24 -right-24 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl animate-blob opacity-50 pointer-events-none" />
      <div className="absolute top-1/2 -left-24 w-72 h-72 bg-violet-500/5 rounded-full blur-3xl animate-blob animation-delay-2000 opacity-50 pointer-events-none" />

      {/* Header */}
      <div className="flex items-center justify-between relative z-10">
        <div>
          <h2 className="text-3xl font-black">
            مرحباً بك، <span className="gradient-text">{(user as any)?.first_name || user?.username}</span> 👋
          </h2>
          <p className="text-muted-foreground mt-1 text-sm">مرحباً بك في لوحة تحكم حسابك الخاص.</p>
        </div>
      </div>

      {/* ── Row 1: KPI Cards ── */}
      <div className="grid gap-4 grid-cols-1 md:grid-cols-3 relative z-10">
        <KpiCard 
          title="إجمالي الطلبات" 
          value={totalOrders} 
          loading={ordersLoading}
          icon={<ShoppingCart className="w-5 h-5 text-violet-400" />}
          glowColor="glow-purple"
        />
        <KpiCard 
          title="طلبات قيد التنفيذ" 
          value={pendingOrders} 
          loading={ordersLoading}
          icon={<Clock className="w-5 h-5 text-cyan-400" />}
          glowColor="glow-cyan"
        />
        <KpiCard 
          title="طلبات مكتملة" 
          value={completedOrders} 
          loading={ordersLoading}
          icon={<CheckCircle className="w-5 h-5 text-emerald-400" />}
          glowColor="glow-emerald"
        />
      </div>

      {/* ── Row 2: Recent Orders ── */}
      <div className="relative z-10">
        <Card className="glass-card border-none">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base font-bold flex items-center gap-2">
              <ShoppingBag className="w-4 h-4 text-amber-400" /> أحدث الطلبات الخاصة بك
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {ordersLoading ? (
                Array(3).fill(0).map((_, i) => <Skeleton key={i} className="h-14 w-full rounded-xl" />)
              ) : ordersList.length === 0 ? (
                <p className="text-center text-muted-foreground py-8 text-sm">لم تقم بأي طلبات بعد</p>
              ) : (
                ordersList.slice(0, 5).map((order: any) => (
                  <div key={order.id} className="flex items-center justify-between p-3 rounded-xl hover:bg-white/5 transition-all">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                        <span className="text-xs font-bold text-amber-400">#{order.id}</span>
                      </div>
                      <div>
                        <p className="font-bold text-sm">إجمالي الطلب: {fmt(order.total_amount)}</p>
                        <p className="text-[11px] text-muted-foreground">
                          {new Date(order.created_at).toLocaleDateString('ar-DZ', { day: 'numeric', month: 'long', year: 'numeric' })}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <StatusBadge status={order.status} />
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
