import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  Search, ShoppingCart, Clock, 
  Truck, CheckCircle, Package
} from 'lucide-react'
import { apiClient } from '../../api/client'
import { useDebounce } from '../../hooks/useDebounce'
import { Input } from '../../components/ui/input'
import { Card, CardContent } from '../../components/ui/card'
import { 
  Table, TableBody, TableCell, 
  TableHead, TableHeader, TableRow 
} from '../../components/ui/table'
import { Tabs, TabsList, TabsTrigger } from '../../components/ui/tabs'
import { StatusBadge } from '../../components/shared/StatusBadge'
import { Skeleton } from '../../components/ui/skeleton'

export default function OrdersPage() {
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<string>('all')
  const debouncedSearch = useDebounce(search, 500)

  const { data: ordersData, isPending: isLoading } = useQuery({
    queryKey: ['my-orders', status, debouncedSearch],
    queryFn: () => apiClient.get('/orders/', {
      params: { status: status === 'all' ? undefined : status, search: debouncedSearch || undefined }
    }).then(res => res.data)
  })

  const fmt = (val: string | number) => new Intl.NumberFormat('ar-DZ', { style: 'currency', currency: 'DZD' }).format(Number(val))

  const orders = ordersData?.orders || ordersData?.results || ordersData || []
  const stats = {
    total: orders.length,
    pending: orders.filter((o: any) => o.status === 'PENDING').length,
    shipped: orders.filter((o: any) => o.status === 'SHIPPED').length,
    delivered: orders.filter((o: any) => o.status === 'DELIVERED').length,
  }

  return (
    <div className="space-y-6 animate-fade-in" dir="rtl">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-amber-500/20">
          <ShoppingCart className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-3xl font-black">طلباتي</h2>
          <p className="text-sm text-muted-foreground">تتبع مشترياتك وخدماتك المطلوبة</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'إجمالي الطلبات', value: stats.total, icon: <Package className="w-4 h-4 text-blue-400" />, glow: 'glow-blue' },
          { label: 'قيد الانتظار', value: stats.pending, icon: <Clock className="w-4 h-4 text-amber-400" />, glow: 'glow-orange' },
          { label: 'قيد الشحن', value: stats.shipped, icon: <Truck className="w-4 h-4 text-violet-400" />, glow: 'glow-purple' },
          { label: 'مُسلَّمة', value: stats.delivered, icon: <CheckCircle className="w-4 h-4 text-emerald-400" />, glow: 'glow-emerald' },
        ].map((s, i) => (
          <Card key={i} className={`glass-card border-none ${s.glow}`}>
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-muted-foreground">{s.label}</span>
                <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center">{s.icon}</div>
              </div>
              <p className="text-3xl font-black">{s.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <div className="glass-card border-none p-6">
        <div className="flex flex-col md:flex-row gap-4 justify-between items-center mb-6">
          <Tabs value={status} onValueChange={setStatus} className="w-full md:w-auto">
            <TabsList className="grid grid-cols-3 md:grid-cols-6 h-auto p-1 glass rounded-xl">
              <TabsTrigger value="all" className="rounded-lg text-xs">الكل</TabsTrigger>
              <TabsTrigger value="PENDING" className="rounded-lg text-xs">انتظار</TabsTrigger>
              <TabsTrigger value="PROCESSING" className="rounded-lg text-xs">قيد المعالجة</TabsTrigger>
              <TabsTrigger value="SHIPPED" className="rounded-lg text-xs">شحن</TabsTrigger>
              <TabsTrigger value="DELIVERED" className="rounded-lg text-xs">مُسلّم</TabsTrigger>
              <TabsTrigger value="CANCELLED" className="rounded-lg text-xs">ملغى</TabsTrigger>
            </TabsList>
          </Tabs>
          <div className="relative w-full md:w-64">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input placeholder="ابحث برقم الطلب..." value={search} onChange={e => setSearch(e.target.value)} className="pr-10 rounded-xl bg-white/5 border-white/10 text-right" />
          </div>
        </div>

        <div className="rounded-xl border border-white/10 overflow-hidden bg-white/5">
          <Table>
            <TableHeader className="bg-white/5 border-b border-white/10">
              <TableRow>
                <TableHead className="text-right">رقم الطلب</TableHead>
                <TableHead className="text-right">التاريخ</TableHead>
                <TableHead className="text-right">العنوان</TableHead>
                <TableHead className="text-right">إجمالي الطلب</TableHead>
                <TableHead className="text-right">الحالة</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                [...Array(5)].map((_, i) => (
                  <TableRow key={i}><TableCell colSpan={5}><Skeleton className="h-12 w-full" /></TableCell></TableRow>
                ))
              ) : orders.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="h-32 text-center text-muted-foreground">
                    <ShoppingCart className="w-12 h-12 mx-auto mb-2 opacity-10" /> ليست لديك طلبات مطابقة للبحث
                  </TableCell>
                </TableRow>
              ) : (
                orders.map((order: any) => (
                  <TableRow key={order.id} className="hover:bg-white/5 transition-colors">
                    <TableCell className="font-bold text-blue-400">#{order.id}</TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {new Date(order.created_at).toLocaleDateString('ar-DZ', { day: 'numeric', month: 'short', year: 'numeric' })}
                    </TableCell>
                    <TableCell className="text-sm">
                        {order.address} - {order.commune?.name || order.commune_name}، {order.wilaya?.name || order.wilaya_name}
                    </TableCell>
                    <TableCell className="font-bold text-sm">{fmt(order.total_amount || order.vendor_subtotal || 0)}</TableCell>
                    <TableCell><StatusBadge status={order.status} /></TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  )
}
