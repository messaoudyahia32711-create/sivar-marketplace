import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { 
  Plus, Search, Edit2, Trash2, 
  Eye, EyeOff, Star, Package, 
  TrendingUp, AlertTriangle, MoreHorizontal
} from 'lucide-react'
import { toast } from 'sonner'
import { apiClient, generalClient } from '../../api/client'
import type { VendorProduct } from '../../types/product'
import { STOCK_STATUS_COLORS } from '../../types/product'
import { useDebounce } from '../../hooks/useDebounce'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { 
  Table, TableBody, TableCell, 
  TableHead, TableHeader, TableRow 
} from '../../components/ui/table'
import { 
  DropdownMenu, DropdownMenuContent, 
  DropdownMenuItem, DropdownMenuTrigger 
} from '../../components/ui/dropdown-menu'
import { Badge } from '../../components/ui/badge'
import { Skeleton } from '../../components/ui/skeleton'
import { cn } from '../../lib/utils'

export default function ProductsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [activeFilter, setActiveFilter] = useState<'all' | 'active' | 'inactive'>('all')
  const [lowStockOnly, setLowStockOnly] = useState(false)
  const debouncedSearch = useDebounce(search, 500)

  const { data, isLoading } = useQuery({
    queryKey: ['products', activeFilter, lowStockOnly, debouncedSearch],
    queryFn: () => apiClient.get('/products/', {
      params: {
        is_active: activeFilter === 'all' ? undefined : activeFilter === 'active',
        low_stock: lowStockOnly || undefined,
        search: debouncedSearch || undefined,
      }
    }).then(res => res.data)
  })

  const toggleStatus = useMutation({
    mutationFn: (id: number) => apiClient.patch(`/products/${id}/toggle-status/`),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
      toast.success(res.data.message)
    }
  })

  const deleteProduct = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/products/${id}/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
      toast.success('تم حذف المنتج بنجاح')
    }
  })

  const fmt = (val: string | number) => 
    new Intl.NumberFormat('ar-DZ', { style: 'currency', currency: 'DZD' }).format(Number(val))

  return (
    <div className="space-y-6 relative animate-fade-in" dir="rtl">
      <div className="absolute -top-20 -left-20 w-64 h-64 bg-violet-500/5 rounded-full blur-3xl pointer-events-none" />

      <div className="flex items-center justify-between relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg shadow-violet-500/20">
            <Package className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-3xl font-black">إدارة المنتجات</h2>
            <p className="text-muted-foreground text-sm">أضف وتحكم في منتجاتك المعروضة في المتجر</p>
          </div>
        </div>
        
        <Button className="gap-2 rounded-xl shadow-lg shadow-blue-500/20 bg-blue-600 hover:bg-blue-700"
          onClick={() => navigate('/products/new')}
        >
          <Plus className="w-4 h-4" />
          <span>إضافة منتج جديد</span>
        </Button>
      </div>

      <div className="glass-card p-6 relative z-10 border-none">
        <div className="flex flex-col md:flex-row gap-4 justify-between items-center mb-6">
          <div className="flex items-center gap-4 w-full md:w-auto">
            <div className="relative flex-1 md:w-64">
              <Search className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input placeholder="ابحث باسم المنتج..." value={search} onChange={e => setSearch(e.target.value)}
                className="pr-10 rounded-xl bg-white/5 border-white/10 text-right" />
            </div>
            <button onClick={() => setLowStockOnly(!lowStockOnly)}
              className={cn(
                "flex items-center gap-2 px-3 py-2 rounded-xl border border-dashed transition-all text-sm",
                lowStockOnly ? "bg-orange-500/10 border-orange-500 text-orange-400" : "bg-white/5 border-white/10 text-muted-foreground"
              )}
            >
              <AlertTriangle className="w-4 h-4" />
              <span className="font-medium">مخزون حرج</span>
            </button>
          </div>
          <div className="flex items-center gap-1 p-1 glass rounded-xl">
            {(['all', 'active', 'inactive'] as const).map(f => (
              <Button key={f} variant={activeFilter === f ? 'default' : 'ghost'} size="sm" className="rounded-lg h-8 px-4 text-xs"
                onClick={() => setActiveFilter(f)}>
                {f === 'all' ? 'الكل' : f === 'active' ? 'نشط' : 'غير نشط'}
              </Button>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-white/10 overflow-hidden bg-white/5">
          <Table>
            <TableHeader className="bg-white/5 border-b border-white/10">
              <TableRow>
                <TableHead className="text-right">المنتج</TableHead>
                <TableHead className="text-right">السعر</TableHead>
                <TableHead className="text-right">المخزون</TableHead>
                <TableHead className="text-right">المبيعات</TableHead>
                <TableHead className="text-right">التقييم</TableHead>
                <TableHead className="text-right">الحالة</TableHead>
                <TableHead className="text-left w-10"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array(5).fill(0).map((_, i) => (
                  <TableRow key={i}>{Array(7).fill(0).map((_, j) => (<TableCell key={j}><Skeleton className="h-6 w-full" /></TableCell>))}</TableRow>
                ))
              ) : data?.results?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="h-48 text-center text-muted-foreground">
                    <Package className="w-16 h-16 mx-auto opacity-10 mb-3" />
                    <p className="text-lg">لا توجد منتجات</p>
                    <p className="text-sm mt-1">أنشئ أول منتج لمتجرك الآن!</p>
                  </TableCell>
                </TableRow>
              ) : (
                data?.results?.map((product: VendorProduct) => (
                  <TableRow key={product.id} className="hover:bg-white/5 transition-colors group">
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center overflow-hidden group-hover:scale-105 transition-transform">
                          {product.image_main ? (
                            <img src={product.image_main} alt={product.name} className="w-full h-full object-cover" />
                          ) : (
                            <Package className="w-5 h-5 text-muted-foreground opacity-30" />
                          )}
                        </div>
                        <div className="flex flex-col text-right">
                          <span className="font-bold text-sm">{product.name}</span>
                          <span className="text-[11px] text-muted-foreground">{product.category_name}</span>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-col text-right">
                        <span className="font-bold text-blue-400 text-sm">{fmt(product.price)}</span>
                        {product.discount_price && <span className="text-[10px] line-through text-muted-foreground">{fmt(product.discount_price)}</span>}
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className={cn('px-2 py-1 rounded-lg text-xs font-bold bg-white/5', STOCK_STATUS_COLORS[product.stock_status])}>
                        {product.stock} قطعة
                      </span>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1 justify-end">
                        <TrendingUp className="w-3 h-3 text-emerald-400" />
                        <span className="font-medium text-sm">{product.total_sold}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1 text-yellow-500 justify-end">
                        <Star className="w-3 h-3 fill-current" />
                        <span className="font-medium text-sm">{product.avg_rating || '—'}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={product.is_active ? 'default' : 'secondary'} 
                        className={cn("rounded-lg text-[10px]", product.is_active ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : "")}>
                        {product.is_active ? 'نشط' : 'متوقف'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8 rounded-lg"><MoreHorizontal className="w-4 h-4" /></Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="glass rounded-xl">
                          <DropdownMenuItem className="gap-2 cursor-pointer text-right justify-end"><Edit2 className="w-4 h-4" /> تعديل</DropdownMenuItem>
                          <DropdownMenuItem className="gap-2 cursor-pointer text-right justify-end" onClick={() => toggleStatus.mutate(product.id)}>
                            {product.is_active ? <><EyeOff className="w-4 h-4" /> إيقاف</> : <><Eye className="w-4 h-4" /> تفعيل</>}
                          </DropdownMenuItem>
                          <DropdownMenuItem className="gap-2 text-red-400 cursor-pointer text-right justify-end"
                            onClick={() => { if(window.confirm('هل أنت متأكد؟')) deleteProduct.mutate(product.id) }}>
                            <Trash2 className="w-4 h-4" /> حذف
                          </DropdownMenuItem>
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
