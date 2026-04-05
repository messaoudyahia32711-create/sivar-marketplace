import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  Mail, MessageSquare, Search, 
  Send, User, Check
} from 'lucide-react'
import { apiClient } from '../../api/client'
import { Input } from '../../components/ui/input'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { Skeleton } from '../../components/ui/skeleton'

export default function MessagesPage() {
  const [activeChat, setActiveChat] = useState<number | null>(null)
  
  // ── جلب المحادثات الحقيقية من المنصة ──
  const { data: realChats, isLoading } = useQuery({
    queryKey: ['incubator-chats'],
    queryFn: () => apiClient.get('/incubator/chats/').then(res => res.data).catch(() => ({ results: [] }))
  })

  const chats = realChats?.results || []

  const { data: messages, isLoading: msgsLoading } = useQuery({
    queryKey: ['chat-messages', activeChat],
    queryFn: () => activeChat ? apiClient.get(`/incubator/chats/${activeChat}/messages/`).then(res => res.data) : null,
    enabled: !!activeChat
  })

  const displayMessages = messages?.messages || []

  return (
    <div className="h-[calc(100vh-100px)] flex flex-col md:flex-row gap-4 animate-fade-in" dir="rtl">
      {/* Sidebar: Chat List */}
      <div className="w-full md:w-80 flex flex-col gap-4">
        <div className="glass-card p-4 flex flex-col flex-1 border-none min-h-0">
          <div className="relative mb-4">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input 
              placeholder="البحث عن محادثة..." 
              className="pr-10 rounded-xl bg-white/5 border-white/10 text-right h-10" 
            />
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 custom-scrollbar">
            {isLoading ? (
              Array(3).fill(0).map((_, i) => <Skeleton key={i} className="h-16 w-full rounded-xl" />)
            ) : chats.length === 0 ? (
              <p className="text-center text-xs text-muted-foreground py-10">لا توجد محادثات نشطة</p>
            ) : (
              chats.map((chat: any) => (
                <div 
                  key={chat.id}
                  onClick={() => setActiveChat(chat.id)}
                  className={`p-3 rounded-xl cursor-pointer transition-all flex items-center gap-3 border ${
                    activeChat === chat.id 
                      ? 'bg-blue-600/20 border-blue-500/30' 
                      : 'bg-white/5 border-transparent hover:bg-white/10 hover:border-white/10'
                  }`}
                >
                  <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center shrink-0 border border-white/10">
                    <User className="w-5 h-5 text-blue-400" />
                  </div>
                  <div className="flex-1 min-w-0 text-right">
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-bold text-sm truncate">{chat.partner?.full_name}</span>
                      <span className="text-[10px] text-muted-foreground shrink-0">
                        {chat.updated_at ? new Date(chat.updated_at).toLocaleTimeString('ar-DZ', { hour: '2-digit', minute: '2-digit' }) : ''}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground truncate">{chat.last_message?.content || 'لا توجد رسائل'}</p>
                  </div>
                  {chat.unread_count > 0 && (
                    <Badge variant="destructive" className="h-5 w-5 flex items-center justify-center p-0 rounded-full text-[10px]">
                      {chat.unread_count}
                    </Badge>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Main: Chat View */}
      <div className="flex-1 flex flex-col min-h-0 min-w-0">
        {activeChat ? (
          <div className="glass-card flex-1 flex flex-col border-none overflow-hidden h-full relative">
            {/* Header */}
            <div className="p-4 border-b border-white/10 flex items-center justify-between bg-white/5">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-blue-600/20 flex items-center justify-center border border-blue-500/30">
                  <MessageSquare className="w-5 h-5 text-blue-400" />
                </div>
                <div className="text-right">
                  <h4 className="font-bold text-sm">{chats.find((c: any) => c.id === activeChat)?.partner?.full_name}</h4>
                  <p className="text-[10px] text-emerald-400">نشط الآن</p>
                </div>
              </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar bg-slate-900/10">
              {msgsLoading ? (
                 <Skeleton className="h-20 w-1/2 float-left rounded-xl" />
              ) : displayMessages.length === 0 ? (
                <div className="h-full flex items-center justify-center text-muted-foreground text-sm">
                  لا توجد رسائل في هذه المحادثة بعد...
                </div>
              ) : (
                displayMessages.map((msg: any) => (
                  <div key={msg.id} className={`flex ${msg.is_me ? 'justify-start' : 'justify-end'}`}>
                    <div className={`max-w-[80%] rounded-2xl p-4 shadow-sm ${
                      msg.is_me 
                        ? 'bg-blue-600 text-white rounded-tr-none' 
                        : 'bg-white/10 text-white rounded-tl-none border border-white/5'
                    }`}>
                      <p className="text-sm leading-relaxed text-right">{msg.content}</p>
                      <div className={`flex items-center gap-1 mt-2 ${msg.is_me ? 'justify-end' : 'justify-start'}`}>
                        <span className="text-[10px] opacity-70 italic">
                          {new Date(msg.created_at).toLocaleTimeString('ar-DZ', { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        {msg.is_me && <Check className="w-3 h-3 opacity-70" />}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white/5 border-t border-white/10">
              <div className="flex gap-3 items-center">
                <Input 
                  placeholder="اكتب رسالتك هنا..." 
                  className="rounded-xl bg-slate-800 border-white/10 text-right flex-1 h-11" 
                />
                <Button className="rounded-xl bg-blue-600 hover:bg-blue-700 h-11 px-5 shadow-lg shadow-blue-500/20">
                  <Send className="w-4 h-4 ml-2" /> إرسال
                </Button>
              </div>
            </div>
          </div>
        ) : (
          <div className="glass-card flex-1 flex flex-col items-center justify-center border-none h-full">
             <div className="w-20 h-20 rounded-3xl bg-indigo-500/5 flex items-center justify-center mb-6">
                <Mail className="w-10 h-10 text-indigo-400 opacity-30" />
             </div>
             <h3 className="text-xl font-bold mb-2">مرحباً بك في مركز الرسائل</h3>
             <p className="text-muted-foreground text-center max-w-sm px-4">
               اختر مؤسسة من القائمة الجانبية لبدء المحادثة المباشرة وتتبع الطلبات والاستفسارات.
             </p>
          </div>
        )}
      </div>
    </div>
  )
}
