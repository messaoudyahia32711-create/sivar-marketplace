import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { 
  Search, Building2, 
  AlertTriangle, MoreHorizontal,
  ExternalLink
} from 'lucide-react'
import { apiClient } from '../../api/client'
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

export default function OrganizationsPage() {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState<'all' | 'active' | 'weak' | 'review'>('all')

  const { data: orgs, isLoading } = useQuery({
    queryKey: ['organizations', filter, search],
    queryFn: () => apiClient.get('/organizations/', {
      params: { status: filter === 'all' ? undefined : filter, search }
    }).then(res => res.data)
  })

  // ── الاعتماد فقط على البيانات الحقيقية ──
  const displayOrgs = (orgs?.results || []).filter((org: any) => {
    if (filter === 'all') return true
    if (filter === 'active') return org.is_verified || org.performance_score >= 70
    if (filter === 'weak') return org.performance_score < 50
    if (filter === 'review') return !org.is_verified
    return true
  }).filter((org: any) => 
    (org.first_name || org.username).toLowerCase().includes(search.toLowerCase()) || 
    (org.university_name || '').toLowerCase().includes(search.toLowerCase())
  )


  const getStatusBadge = (status: string) => {
    switch(status) {
      case 'active': return <Badge className="bg-emerald-500/10 text-emerald-500 border-none">نشطة</Badge>
      case 'weak': return <Badge className="bg-red-500/10 text-red-500 border-none">ضعيفة</Badge>
      case 'review': return <Badge className="bg-amber-500/10 text-amber-500 border-none">قيد المراجعة</Badge>
      default: return <Badge>{status}</Badge>
    }
  }

  // ── الأوامر ──
  const alertMutation = useMutation({
    mutationFn: (id: number) => apiClient.post(`/incubator/org-action/${id}/`, { action: 'alert' }),
    onSuccess: () => toast.success('تم إرسال إشعار التنبيه بضرورة تحسين الأداء للمؤسسة 🔔'),
    onError: () => toast.error('فشل إرسال التنبيه')
  })

  const _openInstitutionDashboard = (id: number) => {
    // Navigate to the public storefront/catalog of the institution
    window.open(`http://localhost:8000/catalog/?vendor_id=${id}`, '_blank')
  }

  return (
    <div className="space-y-6 relative animate-fade-in" dir="rtl">
      <div className="flex items-center justify-between relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-blue-700 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Building2 className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-3xl font-black">إدارة المؤسسات</h2>
            <p className="text-muted-foreground text-sm">متابعة أداء ونشاط المؤسسات المحتضنة في جامعتك.</p>
          </div>
        </div>
      </div>

      <div className="glass-card p-6 relative z-10 border-none">
        <div className="flex flex-col md:flex-row gap-4 justify-between items-center mb-6">
          <div className="relative flex-1 md:w-64 w-full">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input 
              placeholder="البحث عن مؤسسة..." 
              value={search} 
              onChange={e => setSearch(e.target.value)}
              className="pr-10 rounded-xl bg-white/5 border-white/10 text-right" 
            />
          </div>
          <div className="flex items-center gap-1 p-1 glass rounded-xl">
            {(['all', 'active', 'weak', 'review'] as const).map(f => (
              <Button 
                key={f} 
                variant={filter === f ? 'default' : 'ghost'} 
                size="sm" 
                className="rounded-lg h-8 px-4 text-xs"
                onClick={() => setFilter(f)}
              >
                {f === 'all' ? 'الكل' : f === 'active' ? 'نشطة' : f === 'weak' ? 'ضعيفة' : 'مراجعة'}
              </Button>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-white/10 overflow-hidden bg-white/5">
          <Table>
            <TableHeader className="bg-white/5 border-b border-white/10">
              <TableRow>
                <TableHead className="text-right">المؤسسة</TableHead>
                <TableHead className="text-right">المجال</TableHead>
                <TableHead className="text-right">الأداء</TableHead>
                <TableHead className="text-right">الحالة</TableHead>
                <TableHead className="text-left w-10"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array(5).fill(0).map((_, i) => (
                  <TableRow key={i}>{Array(5).fill(0).map((_, j) => (<TableCell key={j}><Skeleton className="h-6 w-full" /></TableCell>))}</TableRow>
                ))
              ) : (
                displayOrgs.map((org: any) => (
                  <TableRow key={org.id} className="hover:bg-white/5 transition-colors group">
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center">
                          <Building2 className="w-5 h-5 text-indigo-400" />
                        </div>
                        <span className="font-bold text-sm">{org.first_name || org.username}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className="text-xs text-muted-foreground">{org.university_name || 'غير محدد'}</span>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 max-w-[100px] h-1.5 bg-white/10 rounded-full overflow-hidden">
                          <div 
                            className={cn(
                              "h-full rounded-full transition-all",
                              org.performance_score > 70 ? "bg-emerald-500" : org.performance_score > 40 ? "bg-amber-500" : "bg-red-500"
                            )}
                            style={{ width: `${org.performance_score}%` }}
                          />
                        </div>
                        <span className="text-xs font-bold">{org.performance_score}%</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      {getStatusBadge(org.status)}
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8 rounded-lg">
                            <MoreHorizontal className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="glass rounded-xl space-y-1">
                          <DropdownMenuItem 
                            className="gap-3 cursor-pointer text-right justify-end hover:bg-white/10"
                            onClick={() => _openInstitutionDashboard(org.id)}
                          >
                            <ExternalLink className="w-4 h-4 text-blue-400" /> عرض معرض المؤسسة
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            className="gap-3 cursor-pointer text-right justify-end hover:bg-white/10"
                            onClick={() => alertMutation.mutate(org.id)}
                            disabled={alertMutation.isPending}
                          >
                            <AlertTriangle className="w-4 h-4 text-amber-400" /> إرسال تنبيه أداء
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
