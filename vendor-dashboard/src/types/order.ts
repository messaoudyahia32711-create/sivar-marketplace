export type OrderStatus = 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled'
export type PaymentMethod = 'cod' | 'cib' | 'edahabia'

export interface OrderItem {
  id: number
  product_name: string | null
  service_name: string | null
  price: string
  quantity: number
  subtotal: string
}

export interface VendorOrder {
  id: number
  customer_name: string
  phone_number: string
  email: string
  wilaya_name: string
  commune_name: string
  address: string
  status: OrderStatus
  status_display: string
  payment_method: PaymentMethod
  payment_display: string
  total_price: string
  vendor_subtotal: string
  vendor_items: OrderItem[]
  created_at: string
}

export const STATUS_FLOW: Partial<Record<OrderStatus, OrderStatus>> = {
  pending:   'confirmed',
  confirmed: 'shipped',
  shipped:   'delivered',
}

export const STATUS_LABELS: Record<OrderStatus, string> = {
  pending:   'قيد الانتظار',
  confirmed: 'مؤكد',
  shipped:   'تم الشحن',
  delivered: 'تم التوصيل',
  cancelled: 'ملغى',
}

export const STATUS_COLORS: Record<OrderStatus, string> = {
  pending:   'bg-yellow-100 text-yellow-800',
  confirmed: 'bg-blue-100 text-blue-800',
  shipped:   'bg-orange-100 text-orange-800',
  delivered: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
}
