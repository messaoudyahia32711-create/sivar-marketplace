import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { UserPlus, Users, Shield, Mail, CheckCircle2, MoreVertical, Trash2 } from 'lucide-react'
import { apiClient } from '../../api/client'
import { Skeleton } from '../../components/ui/skeleton'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Label } from '../../components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { Badge } from '../../components/ui/badge'


export default function TeamPage() {
  const queryClient = useQueryClient()
  const [showModal, setShowModal] = useState(false)
  const [newMember, setNewMember] = useState({ name: '', position: '', email: '' })

  const { data: teamData, isLoading } = useQuery({
    queryKey: ['team'],
    queryFn: () => apiClient.get('/team/').then(res => res.data)
  })

  const team = teamData?.results || []

  const addMemberMutation = useMutation({
    mutationFn: (data: typeof newMember) => apiClient.post('/team/', data),
    onSuccess: () => {
      toast.success('تمت إضافة العضو بنجاح!')
      setShowModal(false)
      setNewMember({ name: '', position: '', email: '' })
      queryClient.invalidateQueries({ queryKey: ['team'] })
    },
    onError: () => toast.error('فشل في إضافة العضو')
  })

  const deleteMemberMutation = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/team/${id}/`),
    onSuccess: () => {
      toast.success('تم حذف العضو')
      queryClient.invalidateQueries({ queryKey: ['team'] })
    }
  })

  const handleAddMember = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newMember.name || !newMember.email) return
    addMemberMutation.mutate(newMember)
  }

  return (
    <div className="space-y-6 animate-fade-in relative" dir="rtl">
      {/* Add Member Modal Overlay */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
           <Card className="w-full max-w-md glass-card border-white/10 shadow-2xl">
             <CardHeader>
               <CardTitle className="flex items-center gap-2">
                 <UserPlus className="w-5 h-5 text-blue-400" /> إضافة عضو للفريق
               </CardTitle>
             </CardHeader>
             <CardContent>
               <form onSubmit={handleAddMember} className="space-y-4">
                 <div className="space-y-1.5">
                   <Label>الاسم الكامل</Label>
                   <Input 
                     placeholder="مثال: محمد علي" 
                     className="bg-white/5 border-white/10" 
                     value={newMember.name}
                     onChange={e => setNewMember({...newMember, name: e.target.value})}
                     required
                   />
                 </div>
                 <div className="space-y-1.5">
                   <Label>البريد الإلكتروني</Label>
                   <Input 
                     type="email" 
                     placeholder="name@company.dz" 
                     className="bg-white/5 border-white/10" 
                     value={newMember.email}
                     onChange={e => setNewMember({...newMember, email: e.target.value})}
                     required
                   />
                 </div>
                 <div className="space-y-1.5">
                    <Label>الدور الوظيفي</Label>
                    <Input 
                      placeholder="مثال: مشرف مبيعات" 
                      className="bg-white/5 border-white/10" 
                      value={newMember.position}
                      onChange={e => setNewMember({...newMember, position: e.target.value})}
                      required
                    />
                 </div>
                 <div className="flex items-center gap-2 pt-4">
                    <Button type="submit" className="flex-1 bg-blue-600 hover:bg-blue-700" disabled={addMemberMutation.isPending}>
                      {addMemberMutation.isPending ? 'جاري الإضافة...' : 'تأكيد الإضافة'}
                    </Button>
                   <Button type="button" variant="ghost" onClick={() => setShowModal(false)} className="flex-1">إلغاء</Button>
                 </div>
               </form>
             </CardContent>
           </Card>
        </div>
      )}

      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-black">إدارة الفريق</h2>
          <p className="text-muted-foreground mt-1">إدارة أعضاء مؤسستك وصلاحياتهم.</p>
        </div>
        <Button 
          onClick={() => setShowModal(true)}
          className="rounded-xl gap-2 shadow-lg shadow-blue-500/20 bg-blue-600 hover:bg-blue-700 active:scale-95 transition-all"
        >
          <UserPlus className="w-4 h-4" /> إضافة عضو جديد
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-4">
        <Card className="glass-card border-none">
          <CardContent className="pt-6 text-center">
            <div className="w-12 h-12 rounded-2xl bg-blue-500/10 flex items-center justify-center mx-auto mb-3">
              <Users className="w-6 h-6 text-blue-400" />
            </div>
            <p className="text-2xl font-black">{team.length}</p>
            <p className="text-xs text-muted-foreground uppercase">إجمالي الفريق</p>
          </CardContent>
        </Card>
        {/* Additional Stats can go here */}
      </div>

      <Card className="glass-card border-none overflow-hidden">
        <CardHeader className="border-b border-white/5 bg-white/5">
          <CardTitle className="text-base font-bold flex items-center gap-2">
            <Shield className="w-4 h-4 text-indigo-400" /> قائمة الأعضاء
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-right border-collapse">
              <thead>
                <tr className="border-b border-white/5 bg-white/5">
                  <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase">العضو</th>
                  <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase">الدور</th>
                  <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase">الحالة</th>
                  <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase">تاريخ الانضمام</th>
                  <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase text-center">إجراءات</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  Array(3).fill(0).map((_, i) => (
                    <tr key={i}><td colSpan={5} className="p-4"><Skeleton className="h-12 w-full" /></td></tr>
                  ))
                ) : team.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-20 text-center text-muted-foreground"> لا يوجد أعضاء حالياً. </td>
                  </tr>
                ) : (
                  team.map((member: any) => (
                    <tr key={member.id} className="border-b border-white/5 hover:bg-white/5 transition-colors group">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500/20 to-blue-500/20 flex items-center justify-center font-bold text-indigo-400">
                            {member.name[0]}
                          </div>
                          <div>
                            <p className="font-bold text-sm tracking-wide">{member.name}</p>
                            <div className="flex items-center gap-1 text-[10px] text-muted-foreground mt-0.5">
                              <Mail className="w-3 h-3" /> {member.email || 'لا يوجد'}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm font-medium">{member.position}</span>
                      </td>
                      <td className="px-6 py-4">
                        <Badge variant="default" className="rounded-lg gap-1">
                          <CheckCircle2 className="w-3 h-3" /> نشط
                        </Badge>
                      </td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">
                        {new Date(member.created_at).toLocaleDateString('ar-DZ')}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex justify-center items-center gap-2">
                          <Button variant="ghost" size="icon" className="w-8 h-8 rounded-lg hover:bg-white/10">
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            className="w-8 h-8 rounded-lg hover:bg-red-500/10 text-red-400"
                            onClick={() => deleteMemberMutation.mutate(member.id)}
                            disabled={deleteMemberMutation.isPending}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
