export type StockStatus = 'ok' | 'low' | 'critical' | 'out'

export interface VendorProduct {
  id: number
  name: string
  slug: string
  price: string
  discount_price: string | null
  stock: number
  stock_status: StockStatus
  is_active: boolean
  is_featured: boolean
  category: number
  category_name: string
  total_sold: number
  total_revenue: string
  avg_rating: number | null
  reviews_count: number
  image_main: string | null
  created_at: string
  updated_at: string
}

export const STOCK_STATUS_COLORS: Record<StockStatus, string> = {
  ok:       'text-green-600',
  low:      'text-yellow-600',
  critical: 'text-red-600 font-bold',
  out:      'text-red-800 bg-red-50',
}
