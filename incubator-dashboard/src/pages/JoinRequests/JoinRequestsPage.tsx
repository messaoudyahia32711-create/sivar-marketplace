import { useQuery } from '@tanstack/react-query'
import { 
  ClipboardList, Check, X, Building2, 
  Search, Filter, Calendar
} from 'lucide-react'
import { apiClient } from '../../api/client'
import { Button } from '../../components/ui/button'
import { Card, CardContent } from '../../components/ui/card'
import { Badge } from '../../components/ui/badge'
import { Input } from '../../components/ui/input'
import { Skeleton } from '../../components/ui/skeleton'
import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { 
  DropdownMenu, DropdownMenuContent, 
  DropdownMenuCheckboxItem, DropdownMenuTrigger 
} from '../../components/ui/dropdown-menu'

export default function JoinRequestsPage() {
  const [search, setSearch] = useState('')
  const [selectedSector, setSelectedSector] = useState<string | null>(null)

  const { data: requests, isPending } = useQuery({
    queryKey: ['organization-requests'],
    queryFn: () => apiClient.get('/incubator/organization-requests/').then(res => res.data)
  })
  const queryClient = useQueryClient()

  // ── الاعتماد فقط على البيانات الحقيقية من الموديل ──
  const displayRequests = (requests?.results || []).filter((req: any) => 
    req.status === 'pending' &&
    (req.name.toLowerCase().includes(search.toLowerCase()) || 
    req.sector.toLowerCase().includes(search.toLowerCase())) &&
    (selectedSector ? req.sector === selectedSector : true)
  )

  const uniqueSectors = Array.from(new Set((requests?.results || []).map((req: any) => req.sector))).filter(Boolean) as string[]


  const actionMutation = useMutation({
    mutationFn: ({ id, action }: { id: number, action: 'approved' | 'rejected' }) => 
      apiClient.post(`/incubator/org-action/${id}/`, { action }),
    onSuccess: (_, variables) => {
      const msg = variables.action === 'approved' ? 'تم قبول المؤسسة بنجاح ✅' : 'تم رفض الطلب ❌'
      toast.success(msg)
      queryClient.invalidateQueries({ queryKey: ['organization-requests'] })
      queryClient.invalidateQueries({ queryKey: ['incubator-stats'] }) 
      queryClient.invalidateQueries({ queryKey: ['recent-requests'] }) 
      queryClient.invalidateQueries({ queryKey: ['organizations'] }) 
    },
    onError: () => toast.error('حدث خطأ أثناء معالجة الطلب')
  })

  const handleAction = (id: number, action: 'approved' | 'rejected') => {
    actionMutation.mutate({ id, action })
  }

  return (
    <div className="space-y-6 animate-fade-in" dir="rtl">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-black flex items-center gap-3">
            <ClipboardList className="w-8 h-8 text-amber-400" />
            طلبات الانضمام
          </h2>
          <p className="text-muted-foreground mt-1">مراجعة ومعالجة طلبات احتضان المؤسسات الناشئة.</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input 
            placeholder="البحث في الطلبات..." 
            className="pr-10 bg-white/5 border-white/10 rounded-xl"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="rounded-xl border-white/10 gap-2 relative">
              <Filter className="w-4 h-4" /> 
              {selectedSector ? `القطاع: ${selectedSector}` : 'تصفية حسب القطاع'}
              {selectedSector && (
                <div 
                  className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full cursor-pointer hover:bg-blue-600"
                  onClick={(e) => { e.stopPropagation(); setSelectedSector(null); }}
                />
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="glass rounded-xl w-48 text-right border-white/10">
            <DropdownMenuCheckboxItem 
              checked={selectedSector === null}
              onCheckedChange={() => setSelectedSector(null)}
              className="text-right justify-end pr-8"
            >
              الكل
            </DropdownMenuCheckboxItem>
            {uniqueSectors.map((sector) => (
              <DropdownMenuCheckboxItem 
                key={sector}
                checked={selectedSector === sector}
                onCheckedChange={() => setSelectedSector(sector)}
                className="text-right justify-end pr-8"
              >
                {sector}
              </DropdownMenuCheckboxItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Requests List */}
      <div className="grid gap-4">
        {isPending ? (
          Array(3).fill(0).map((_, i) => <Skeleton key={i} className="h-24 w-full rounded-2xl" />)
        ) : (
          displayRequests.map((req: any) => (
            <Card key={req.id} className="glass-card border-none group overflow-hidden transition-all hover:bg-white/5">
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-amber-500/20 to-orange-500/20 flex items-center justify-center">
                      <Building2 className="w-6 h-6 text-amber-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold">{req.name}</h3>
                      <div className="flex items-center gap-3 mt-1">
                        <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-none px-2 rounded-lg text-[10px]">
                          {req.sector}
                        </Badge>
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {req.created_at}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button 
                      className="rounded-xl bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500 hover:text-white border-none gap-2"
                      onClick={() => handleAction(req.id, 'approved')}
                      disabled={actionMutation.isPending}
                    >
                      <Check className="w-4 h-4" /> 
                      {actionMutation.isPending && actionMutation.variables?.id === req.id && actionMutation.variables?.action === 'approved' ? 'جاري القبول...' : 'قبول الطلب'}
                    </Button>
                    <Button 
                      variant="ghost"
                      className="rounded-xl text-red-500 hover:bg-red-500/10 gap-2"
                      onClick={() => handleAction(req.id, 'rejected')}
                    >
                      <X className="w-4 h-4" /> رفض
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
