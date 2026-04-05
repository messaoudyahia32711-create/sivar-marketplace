import { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Send, User as UserIcon, Store as StoreIcon, MessageCircle } from 'lucide-react'
import { apiClient } from '../../api/client'
import { Input } from '../../components/ui/input'
import { Button } from '../../components/ui/button'
import { Card } from '../../components/ui/card'
import { Skeleton } from '../../components/ui/skeleton'

export default function MessagesPage() {
  const queryClient = useQueryClient()
  const [activeConvId, setActiveConvId] = useState<number | null>(null)
  const [msgText, setMsgText] = useState('')
  const msgsEndRef = useRef<HTMLDivElement>(null)

  // ── Fetch Conversations ──
  const { data: convData, isPending: convLoading } = useQuery({
    queryKey: ['chat-conversations'],
    queryFn: () => apiClient.get('/chat/conversations/').then(res => res.data),
    refetchInterval: 10000, // Poll every 10 seconds
  })

  // ── Fetch Messages for active conversation ──
  const { data: activeConvDetails, isPending: msgsLoading } = useQuery({
    queryKey: ['chat-conversation-details', activeConvId],
    queryFn: () => apiClient.get(`/chat/conversations/${activeConvId}/`).then(res => res.data),
    enabled: !!activeConvId,
    refetchInterval: 3000, // Poll every 3 seconds for active chat
  })

  // ── Send Message ──
  const sendMsgMutation = useMutation({
    mutationFn: (text: string) => apiClient.post('/chat/messages/send/', {
      content: text,
      conversation_id: activeConvId
    }),
    onSuccess: () => {
      setMsgText('')
      queryClient.invalidateQueries({ queryKey: ['chat-conversation-details', activeConvId] })
      queryClient.invalidateQueries({ queryKey: ['chat-conversations'] })
    }
  })

  const handleSend = (e?: React.FormEvent) => {
    e?.preventDefault()
    if (!msgText.trim() || !activeConvId) return
    sendMsgMutation.mutate(msgText)
  }

  // Scroll to bottom when messages load
  useEffect(() => {
    msgsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [activeConvDetails?.messages])

  const conversations = convData || []

  return (
    <div className="h-[calc(100vh-120px)] flex bg-black/20 border border-white/5 rounded-2xl overflow-hidden animate-fade-in" dir="rtl">
      
      {/* ── Sidebar (Conversations List) ── */}
      <div className="w-1/3 border-l border-white/10 flex flex-col bg-white/5">
        <div className="p-4 border-b border-white/10">
          <h2 className="font-bold text-lg flex items-center gap-2">
            <MessageCircle className="w-5 h-5 text-indigo-400" /> المحادثات
          </h2>
        </div>
        
        <div className="flex-1 overflow-y-auto p-2 space-y-2">
          {convLoading ? (
            Array(5).fill(0).map((_, i) => <Skeleton key={i} className="h-16 w-full rounded-xl bg-white/5" />)
          ) : conversations.length === 0 ? (
            <p className="text-center text-muted-foreground p-4 text-sm mt-10">لا توجد محادثات سابقة</p>
          ) : (
            conversations.map((conv: any) => {
              const partner = conv.partner
              const isActive = activeConvId === conv.id
              return (
                <div 
                  key={conv.id}
                  onClick={() => setActiveConvId(conv.id)}
                  className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-colors ${isActive ? 'bg-indigo-500/20 border border-indigo-500/30' : 'hover:bg-white/5 border border-transparent'}`}
                >
                  <div className="w-10 h-10 rounded-full bg-indigo-500/20 flex items-center justify-center shrink-0">
                    <UserIcon className="w-5 h-5 text-indigo-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-center">
                      <p className="font-bold text-sm truncate">{partner?.store_name || partner?.full_name}</p>
                      {conv.unread_count > 0 && !isActive && (
                        <span className="w-5 h-5 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center">{conv.unread_count}</span>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground truncate font-normal">
                      {conv.last_message?.content || 'صورة/مرفق'}
                    </p>
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>

      {/* ── Chat Area ── */}
      <div className="flex-1 flex flex-col bg-black/40 relative">
        {!activeConvId ? (
          <div className="flex-1 flex flex-col items-center justify-center opacity-50">
            <MessageCircle className="w-16 h-16 text-indigo-400 mb-4" />
            <p className="text-lg font-bold">اختر محادثة للبدء في المراسلة</p>
          </div>
        ) : (
          <>
            {/* Chat Header */}
            <div className="p-4 border-b border-white/10 flex items-center gap-3 bg-white/5">
              <div className="w-10 h-10 rounded-full bg-indigo-500/20 flex items-center justify-center">
                <StoreIcon className="w-5 h-5 text-indigo-400" />
              </div>
              <div>
                <p className="font-bold">{activeConvDetails?.partner?.store_name || activeConvDetails?.partner?.full_name}</p>
              </div>
            </div>

            {/* Chat History */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {msgsLoading && !activeConvDetails ? (
                 <div className="flex flex-col gap-4">
                   <Skeleton className="h-12 w-2/3 rounded-xl bg-white/5" />
                   <Skeleton className="h-12 w-1/2 rounded-xl bg-white/5 self-end" />
                 </div>
              ) : activeConvDetails?.messages?.length === 0 ? (
                <p className="text-center text-muted-foreground my-8">لا يوجد رسائل بعد، أرسل أول رسالة.</p>
              ) : (
                activeConvDetails?.messages.map((msg: any) => (
                  <div key={msg.id} className={`flex flex-col max-w-[75%] ${msg.is_me ? 'self-end mr-auto items-end' : 'self-start ml-auto items-start'}`}>
                    <div className={`p-3 rounded-2xl ${msg.is_me ? 'bg-indigo-600 text-white rounded-tl-none' : 'bg-white/10 text-white rounded-tr-none'}`}>
                      {msg.content}
                    </div>
                    <span className="text-[10px] text-muted-foreground mt-1 px-1">
                      {new Date(msg.created_at).toLocaleTimeString('ar-DZ', { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                ))
              )}
              <div ref={msgsEndRef} />
            </div>

            {/* Message Input */}
            <div className="p-4 bg-white/5 border-t border-white/10">
              <form onSubmit={handleSend} className="flex items-center gap-3">
                <Input 
                  placeholder="اكتب رسالتك..." 
                  className="rounded-full bg-white/5 border-white/10 focus:border-indigo-500 h-12 px-6"
                  value={msgText}
                  onChange={e => setMsgText(e.target.value)}
                  disabled={sendMsgMutation.isPending}
                />
                <Button 
                  type="submit" 
                  disabled={!msgText.trim() || sendMsgMutation.isPending}
                  className="rounded-full w-12 h-12 bg-indigo-600 hover:bg-indigo-700 p-0 flex items-center justify-center shrink-0 shadow-lg shadow-indigo-500/20"
                >
                  <Send className="w-5 h-5 text-white mr-1" />
                </Button>
              </form>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
