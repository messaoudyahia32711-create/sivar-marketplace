import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { 
  Plus, Search, Edit2, Trash2, 
  Eye, EyeOff, Star, Briefcase, 
  MapPin, MoreHorizontal
} from 'lucide-react'
import { toast } from 'sonner'
import { apiClient, generalClient } from '../../api/client'
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

export default function ServicesPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebounce(search, 500)

  const { data, isLoading } = useQuery({
    queryKey: ['services', debouncedSearch],
    queryFn: () => apiClient.get('/services/', {
      params: { search: debouncedSearch || undefined }
    }).then(res => res.data)
  })

  const toggleStatus = useMutation({
    mutationFn: (id: number) => apiClient.patch(`/services/${id}/toggle-status/`),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ['services'] })
      toast.success(res.data.message)
    }
  })

  const deleteService = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/services/${id}/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['services'] })
      toast.success('تم حذف الخدمة بنجاح')
    }
  })

  const fmt = (val: string | number) => 
    new Intl.NumberFormat('ar-DZ', { style: 'currency', currency: 'DZD' }).format(Number(val))

  return (
    <div className="space-y-6 relative animate-fade-in" dir="rtl">
      <div className="absolute -top-20 -left-20 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />

      <div className="flex items-center justify-between relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <Briefcase className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-3xl font-black">إدارة الخدمات</h2>
            <p className="text-muted-foreground text-sm">أضف وتحكم في الخدمات التي تقدمها عبر المنصة</p>
          </div>
        </div>
        
        <Button className="gap-2 rounded-xl shadow-lg shadow-emerald-500/20 bg-emerald-600 hover:bg-emerald-700"
          onClick={() => navigate('/services/new')}
        >
          <Plus className="w-4 h-4" />
          <span>إضافة خدمة جديدة</span>
        </Button>
      </div>

      <div className="glass-card p-6 relative z-10 border-none">
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1 md:w-64 md:flex-initial">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input placeholder="ابحث باسم الخدمة..." value={search} onChange={e => setSearch(e.target.value)}
              className="pr-10 rounded-xl bg-white/5 border-white/10 text-right" />
          </div>
        </div>

        <div className="rounded-xl border border-white/10 overflow-hidden bg-white/5">
          <Table>
            <TableHeader className="bg-white/5 border-b border-white/10">
              <TableRow>
                <TableHead className="text-right">الخدمة</TableHead>
                <TableHead className="text-right">التصنيف</TableHead>
                <TableHead className="text-right">السعر</TableHead>
                <TableHead className="text-right">التغطية</TableHead>
                <TableHead className="text-right">الحالة</TableHead>
                <TableHead className="text-left w-10"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array(5).fill(0).map((_, i) => (
                  <TableRow key={i}>{Array(6).fill(0).map((_, j) => (<TableCell key={j}><Skeleton className="h-6 w-full" /></TableCell>))}</TableRow>
                ))
              ) : data?.results?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="h-48 text-center text-muted-foreground">
                    <Briefcase className="w-16 h-16 mx-auto opacity-10 mb-3" />
                    <p className="text-lg">لا توجد خدمات</p>
                    <p className="text-sm mt-1">أنشئ أول خدمة لمتجرك الآن!</p>
                  </TableCell>
                </TableRow>
              ) : (
                data?.results?.map((service: any) => (
                  <TableRow key={service.id} className="hover:bg-white/5 transition-colors group">
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center overflow-hidden group-hover:scale-105 transition-transform">
                          {service.images?.[0]?.image ? (
                            <img src={service.images[0].image} alt={service.name} className="w-full h-full object-cover" />
                          ) : (
                            <Briefcase className="w-5 h-5 text-muted-foreground opacity-30" />
                          )}
                        </div>
                        <div className="flex flex-col text-right">
                          <span className="font-bold text-sm">{service.name}</span>
                          <div className="flex items-center gap-1 text-[10px] text-yellow-500">
                            <Star className="w-2.5 h-2.5 fill-current" />
                            <span>{service.avg_rating || '—'}</span>
                          </div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <Badge variant="outline" className="bg-white/5 border-white/10 rounded-lg text-[11px]">{service.category?.name}</Badge>
                    </TableCell>
                    <TableCell>
                      <span className="font-bold text-emerald-400 text-sm">{fmt(service.price)}</span>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1 justify-end text-muted-foreground">
                        <MapPin className="w-3 h-3" />
                        <span className="text-xs">{service.wilayas?.length || 0} ولاية</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={service.is_active ? 'default' : 'secondary'} 
                        className={cn("rounded-lg text-[10px]", service.is_active ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : "")}>
                        {service.is_active ? 'نشط' : 'متوقف'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8 rounded-lg"><MoreHorizontal className="w-4 h-4" /></Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="glass rounded-xl">
                          <DropdownMenuItem className="gap-2 cursor-pointer text-right justify-end"><Edit2 className="w-4 h-4" /> تعديل</DropdownMenuItem>
                          <DropdownMenuItem className="gap-2 cursor-pointer text-right justify-end" onClick={() => toggleStatus.mutate(service.id)}>
                            {service.is_active ? <><EyeOff className="w-4 h-4" /> إيقاف</> : <><Eye className="w-4 h-4" /> تفعيل</>}
                          </DropdownMenuItem>
                          <DropdownMenuItem className="gap-2 text-red-400 cursor-pointer text-right justify-end"
                            onClick={() => { if(window.confirm('هل أنت متأكد؟')) deleteService.mutate(service.id) }}>
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
