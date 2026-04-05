import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  Users, UserPlus, Mail, Phone, 
  MoreVertical, Trash2, Edit2, 
  ShieldCheck, GraduationCap
} from 'lucide-react'
import { toast } from 'sonner'
import { apiClient } from '../../api/client'
import { Button } from '../../components/ui/button'
import { Card, CardContent } from '../../components/ui/card'
import { Skeleton } from '../../components/ui/skeleton'
import { 
  DropdownMenu, DropdownMenuContent, 
  DropdownMenuItem, DropdownMenuTrigger 
} from '../../components/ui/dropdown-menu'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "../../components/ui/dialog"
import { Input } from '../../components/ui/input'
import { Label } from '../../components/ui/label'


export default function TeamPage() {
  const queryClient = useQueryClient()
  const { data: team, isLoading } = useQuery({
    queryKey: ['incubator-team'],
    queryFn: () => apiClient.get('/incubator/team/').then(res => res.data)
  })

  const displayTeam = team?.results || []

  const [isAddOpen, setIsAddOpen] = useState(false)
  const [newMember, setNewMember] = useState({ name: '', position: '', email: '', phone: '', bio: '' })

  const [isEditOpen, setIsEditOpen] = useState(false)
  const [editMemberData, setEditMemberData] = useState<any>(null)


  const deleteMember = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/incubator/team/${id}/`),
    onSuccess: () => {
      toast.success('تم حذف العضو بنجاح')
      queryClient.invalidateQueries({ queryKey: ['incubator-team'] })
    }
  })

  const addMember = useMutation({
    mutationFn: (data: typeof newMember) => apiClient.post('/incubator/team/', data),
    onSuccess: () => {
      toast.success('تم إضافة العضو بنجاح ✅')
      setIsAddOpen(false)
      setNewMember({ name: '', position: '', email: '', phone: '', bio: '' })
      queryClient.invalidateQueries({ queryKey: ['incubator-team'] })
    },
    onError: () => toast.error('فشل إضافة العضو')
  })

  const updateMember = useMutation({
    mutationFn: (data: any) => apiClient.patch(`/incubator/team/${data.id}/`, data),
    onSuccess: () => {
      toast.success('تم تحديث بيانات العضو بنجاح 🔄')
      setIsEditOpen(false)
      queryClient.invalidateQueries({ queryKey: ['incubator-team'] })
    },
    onError: () => toast.error('فشل تحديث بيانات العضو')
  })

  const handleAddSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newMember.name || !newMember.position) return toast.error('يرجى ملء كافة الحقول')
    addMember.mutate(newMember)
  }

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!editMemberData.name || !editMemberData.position) return toast.error('يرجى ملء كافة الحقول الأساسية')
    updateMember.mutate(editMemberData)
  }

  const openEditDialog = (member: any) => {
    setEditMemberData(member)
    setIsEditOpen(true)
  }

  return (
    <div className="space-y-6 animate-fade-in" dir="rtl">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-black flex items-center gap-3">
            <Users className="w-8 h-8 text-emerald-400" />
            أعضاء الفريق
          </h2>
          <p className="text-muted-foreground mt-1 text-sm">إدارة الكادر الإداري والمرافقين التابعين للحاضنة.</p>
        </div>
        <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
          <DialogTrigger asChild>
            <Button className="rounded-xl bg-blue-600 hover:bg-blue-700 gap-2 shadow-lg shadow-blue-500/20">
              <UserPlus className="w-4 h-4" /> إضافة عضو جديد
            </Button>
          </DialogTrigger>
          <DialogContent className="glass border-white/10 text-right" dir="rtl">
            <DialogHeader>
              <DialogTitle className="text-right text-xl font-bold">إضافة عضو جديد للفريق</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleAddSubmit} className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="name">الاسم الكامل</Label>
                <Input 
                  id="name" 
                  placeholder="مثال: د. سمير علي" 
                  className="rounded-xl bg-white/5 border-white/10 text-right"
                  value={newMember.name}
                  onChange={e => setNewMember({ ...newMember, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="pos">المنصب / التخصص</Label>
                <Input 
                  id="pos" 
                  placeholder="مثال: مستشار تقني" 
                  className="rounded-xl bg-white/5 border-white/10 text-right"
                  value={newMember.position}
                  onChange={e => setNewMember({ ...newMember, position: e.target.value })}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="email">البريد الإلكتروني</Label>
                  <Input 
                    id="email" 
                    type="email"
                    placeholder="mail@example.com" 
                    className="rounded-xl bg-white/5 border-white/10 text-right"
                    value={newMember.email}
                    onChange={e => setNewMember({ ...newMember, email: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">رقم الهاتف</Label>
                  <Input 
                    id="phone" 
                    placeholder="0661234567" 
                    className="rounded-xl bg-white/5 border-white/10 text-right"
                    value={newMember.phone}
                    onChange={e => setNewMember({ ...newMember, phone: e.target.value })}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="bio">نبذة مختصرة (اختياري)</Label>
                <textarea 
                  id="bio" 
                  rows={3}
                  placeholder="وصف لخبرات العضو أو دوره في الحاضنة..." 
                  className="w-full rounded-xl bg-white/5 border border-white/10 text-right p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                  value={newMember.bio}
                  onChange={e => setNewMember({ ...newMember, bio: e.target.value })}
                />
              </div>
              <DialogFooter className="mt-6 flex-row-reverse gap-2">
                <Button type="submit" className="rounded-xl bg-blue-600 hover:bg-blue-700 flex-1" disabled={addMember.isPending}>
                  {addMember.isPending ? 'جاري الحفظ...' : 'حفظ العضو'}
                </Button>
                <Button type="button" variant="ghost" className="rounded-xl" onClick={() => setIsAddOpen(false)}>إلغاء</Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* Edit Member Dialog */}
        <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
          <DialogContent className="glass border-white/10 text-right" dir="rtl">
            <DialogHeader>
              <DialogTitle className="text-right text-xl font-bold">تعديل بيانات العضو</DialogTitle>
            </DialogHeader>
            {editMemberData && (
              <form onSubmit={handleEditSubmit} className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="edit-name">الاسم الكامل</Label>
                  <Input 
                    id="edit-name" 
                    className="rounded-xl bg-white/5 border-white/10 text-right"
                    value={editMemberData.name}
                    onChange={e => setEditMemberData({ ...editMemberData, name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit-pos">المنصب / التخصص</Label>
                  <Input 
                    id="edit-pos" 
                    className="rounded-xl bg-white/5 border-white/10 text-right"
                    value={editMemberData.position}
                    onChange={e => setEditMemberData({ ...editMemberData, position: e.target.value })}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="edit-email">البريد الإلكتروني</Label>
                    <Input 
                      id="edit-email" 
                      type="email"
                      className="rounded-xl bg-white/5 border-white/10 text-right"
                      value={editMemberData.email || ''}
                      onChange={e => setEditMemberData({ ...editMemberData, email: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="edit-phone">رقم الهاتف</Label>
                    <Input 
                      id="edit-phone" 
                      className="rounded-xl bg-white/5 border-white/10 text-right"
                      value={editMemberData.phone || ''}
                      onChange={e => setEditMemberData({ ...editMemberData, phone: e.target.value })}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit-bio">نبذة مختصرة</Label>
                  <textarea 
                    id="edit-bio" 
                    rows={3}
                    className="w-full rounded-xl bg-white/5 border border-white/10 text-right p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                    value={editMemberData.bio || ''}
                    onChange={e => setEditMemberData({ ...editMemberData, bio: e.target.value })}
                  />
                </div>
                <DialogFooter className="mt-6 flex-row-reverse gap-2">
                  <Button type="submit" className="rounded-xl bg-emerald-600 hover:bg-emerald-700 flex-1" disabled={updateMember.isPending}>
                    {updateMember.isPending ? 'جاري التحديث...' : 'تحديث البيانات'}
                  </Button>
                  <Button type="button" variant="ghost" className="rounded-xl" onClick={() => setIsEditOpen(false)}>إلغاء</Button>
                </DialogFooter>
              </form>
            )}
          </DialogContent>
        </Dialog>
      </div>

      {/* Team Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {isLoading ? (
          Array(3).fill(0).map((_, i) => <Skeleton key={i} className="h-64 w-full rounded-2xl" />)
        ) : (
          displayTeam.length === 0 ? (
            <div className="col-span-full py-20 text-center glass-card rounded-2xl border-none">
              <Users className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-20" />
              <p className="text-muted-foreground">لا يوجد أعضاء في الفريق حالياً.</p>
            </div>
          ) : (
            displayTeam.map((member: any) => (
              <Card key={member.id} className="glass-card border-none overflow-hidden group hover:scale-[1.02] transition-all">
                <CardContent className="p-0">
                  <div className="h-24 bg-gradient-to-br from-indigo-600/20 to-blue-700/20 relative">
                    <div className="absolute top-4 left-4">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8 rounded-lg bg-black/20 text-white hover:bg-black/40">
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="glass rounded-xl">
                          <DropdownMenuItem 
                            className="gap-2 cursor-pointer text-right justify-end hover:bg-white/10"
                            onClick={() => openEditDialog(member)}
                          >
                            تعديل البيانات <Edit2 className="w-4 h-4 text-blue-400" />
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            className="gap-2 cursor-pointer text-red-400 text-right justify-end hover:bg-red-500/10"
                            onClick={() => deleteMember.mutate(member.id)}
                          >
                            حذف العضو <Trash2 className="w-4 h-4" />
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                  
                  <div className="px-6 pb-6 text-center">
                    <div className="relative -mt-12 mb-4 inline-block">
                      <div className="w-24 h-24 rounded-2xl border-4 border-background bg-slate-800 flex items-center justify-center shadow-xl overflow-hidden group-hover:border-blue-500/50 transition-colors">
                        {member.image ? (
                          <img src={member.image} alt={member.name} className="w-full h-full object-cover" />
                        ) : (
                          <GraduationCap className="w-10 h-10 text-blue-400 opacity-50" />
                        )}
                      </div>
                      <div className="absolute -bottom-1 -left-1 w-7 h-7 bg-emerald-500 rounded-lg border-2 border-background flex items-center justify-center">
                        <ShieldCheck className="w-4 h-4 text-white" />
                      </div>
                    </div>

                    <h3 className="text-lg font-bold">{member.name}</h3>
                    <p className="text-sm text-blue-400 font-medium mb-2">{member.position}</p>
                    
                    {member.bio && (
                      <p className="text-[11px] text-muted-foreground line-clamp-2 px-4 mb-4 mb-4 h-8 overflow-hidden">
                        {member.bio}
                      </p>
                    )}
                    
                    <div className="mt-4 flex items-center justify-center gap-2">
                      {member.email && (
                        <Button variant="ghost" size="icon" className="h-9 w-9 rounded-xl bg-white/5 hover:bg-white/10" 
                          onClick={() => window.location.href = `mailto:${member.email}`}>
                          <Mail className="w-4 h-4 text-blue-400" />
                        </Button>
                      )}
                      {member.phone && (
                        <Button variant="ghost" size="icon" className="h-9 w-9 rounded-xl bg-white/5 hover:bg-white/10"
                          onClick={() => window.location.href = `tel:${member.phone}`}>
                          <Phone className="w-4 h-4 text-emerald-400" />
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )
        )}
      </div>
    </div>
  )
}
