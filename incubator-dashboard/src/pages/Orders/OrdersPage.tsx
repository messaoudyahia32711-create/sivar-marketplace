import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  Search, MoreVertical, ShoppingCart, Clock, 
  Truck, CheckCircle, XCircle, Package
} from 'lucide-react'
import { toast } from 'sonner'
import { apiClient } from '../../api/client'
import type { VendorOrder } from '../../types/order'
import { STATUS_LABELS, STATUS_FLOW } from '../../types/order'
import { useDebounce } from '../../hooks/useDebounce'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Card, CardContent } from '../../components/ui/card'
import { 
  Table, TableBody, TableCell, 
  TableHead, TableHeader, TableRow 
} from '../../components/ui/table'
import { 
  DropdownMenu, DropdownMenuContent, 
  DropdownMenuItem, DropdownMenuTrigger 
} from '../../components/ui/dropdown-menu'
import { Tabs, TabsList, TabsTrigger } from '../../components/ui/tabs'
import { StatusBadge } from '../../components/shared/StatusBadge'
import { Skeleton } from '../../components/ui/skeleton'

export default function OrdersPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<string>('all')
  const debouncedSearch = useDebounce(search, 500)

  const { data: ordersData, isPending: isLoading } = useQuery({
    queryKey: ['orders', status, debouncedSearch],
    queryFn: () => apiClient.get('/orders/', {
      params: { status: status === 'all' ? undefined : status, search: debouncedSearch || undefined }
    }).then(res => res.data)
  })

  const updateStatus = useMutation({
    mutationFn: ({ id, nextStatus }: { id: number, nextStatus: string }) => 
      apiClient.patch(`/orders/${id}/status/`, { new_status: nextStatus }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] })
      toast.success('تم تحديث حالة الطلب بنجاح')
    },
    onError: (err: any) => toast.error(err.response?.data?.error || 'فشل تحديث الحالة')
  })

  const fmt = (val: string | number) => new Intl.NumberFormat('ar-DZ', { style: 'currency', currency: 'DZD' }).format(Number(val))

  const orders = ordersData?.results || []
  const stats = {
    total: orders.length,
    pending: orders.filter((o: any) => o.status === 'pending').length,
    shipped: orders.filter((o: any) => o.status === 'shipped').length,
    delivered: orders.filter((o: any) => o.status === 'delivered').length,
  }

  return (
    <div className="space-y-6 animate-fade-in" dir="rtl">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-amber-500/20">
          <ShoppingCart className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-3xl font-black">إدارة الطلبات</h2>
          <p className="text-sm text-muted-foreground">تتبع وإدارة جميع طلبات متجرك</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'الإجمالي', value: stats.total, icon: <Package className="w-4 h-4 text-blue-400" />, glow: 'glow-blue' },
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
              <TabsTrigger value="pending" className="rounded-lg text-xs">انتظار</TabsTrigger>
              <TabsTrigger value="confirmed" className="rounded-lg text-xs">مؤكد</TabsTrigger>
              <TabsTrigger value="shipped" className="rounded-lg text-xs">شحن</TabsTrigger>
              <TabsTrigger value="delivered" className="rounded-lg text-xs">مُسلّم</TabsTrigger>
              <TabsTrigger value="cancelled" className="rounded-lg text-xs">ملغى</TabsTrigger>
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
                <TableHead className="text-right">العميل</TableHead>
                <TableHead className="text-right">الموقع</TableHead>
                <TableHead className="text-right">القيمة</TableHead>
                <TableHead className="text-right">الحالة</TableHead>
                <TableHead className="text-right">التاريخ</TableHead>
                <TableHead className="text-left w-10"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                [...Array(5)].map((_, i) => (
                  <TableRow key={i}><TableCell colSpan={7}><Skeleton className="h-12 w-full" /></TableCell></TableRow>
                ))
              ) : orders.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="h-32 text-center text-muted-foreground">
                    <ShoppingCart className="w-12 h-12 mx-auto mb-2 opacity-10" /> لا توجد طلبات
                  </TableCell>
                </TableRow>
              ) : (
                orders.map((order: VendorOrder) => (
                  <TableRow key={order.id} className="hover:bg-white/5 transition-colors">
                    <TableCell className="font-bold text-blue-400">#{order.id}</TableCell>
                    <TableCell>
                      <p className="font-medium text-sm">{order.customer_name}</p>
                      <p className="text-[10px] text-muted-foreground">{order.phone_number}</p>
                    </TableCell>
                    <TableCell className="text-sm">{order.wilaya_name}، {order.commune_name}</TableCell>
                    <TableCell className="font-bold text-sm">{fmt(order.vendor_subtotal)}</TableCell>
                    <TableCell><StatusBadge status={order.status} /></TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {new Date(order.created_at).toLocaleDateString('ar-DZ', { day: 'numeric', month: 'short' })}
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8 rounded-lg"><MoreVertical className="w-4 h-4" /></Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="glass rounded-xl">
                          {STATUS_FLOW[order.status] && (
                            <DropdownMenuItem className="text-primary font-bold text-right justify-end cursor-pointer"
                              onClick={() => updateStatus.mutate({ id: order.id, nextStatus: STATUS_FLOW[order.status]! })}
                            >
                              نقل إلى "{STATUS_LABELS[STATUS_FLOW[order.status]!]}"
                            </DropdownMenuItem>
                          )}
                          <DropdownMenuItem className="text-right justify-end cursor-pointer">عرض التفاصيل</DropdownMenuItem>
                          <DropdownMenuItem className="text-red-400 text-right justify-end cursor-pointer">إلغاء الطلب</DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
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
