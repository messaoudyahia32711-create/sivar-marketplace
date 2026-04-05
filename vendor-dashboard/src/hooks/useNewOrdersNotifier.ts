import { useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { toast } from 'sonner'
import { apiClient } from '../api/client'

export function useNewOrdersNotifier() {
  const prevCountRef = useRef<number | null>(null)

  const { data } = useQuery({
    queryKey: ['pending-orders-count'],
    queryFn:  () => apiClient.get('/orders/pending-count/').then(r => r.data),
    refetchInterval: 30_000,  // كل 30 ثانية
    refetchIntervalInBackground: true,
  })

  useEffect(() => {
    const count = data?.pending_count ?? null
    if (count === null) return

    if (prevCountRef.current !== null && count > prevCountRef.current) {
      const newOrders = count - prevCountRef.current
      toast.success(`🛍️ ${newOrders} طلب جديد وصل!`, {
        description: 'تحقق من قسم الطلبات',
        duration: 8000,
        action: {
          label: 'عرض الطلبات',
          onClick: () => window.location.href = '/orders',
        },
      })
    }
    prevCountRef.current = count
  }, [data])
}
