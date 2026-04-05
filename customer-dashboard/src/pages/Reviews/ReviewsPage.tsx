import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Star, MessageSquare, Filter } from 'lucide-react'
import { apiClient } from '../../api/client'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Skeleton } from '../../components/ui/skeleton'
import { cn } from '../../lib/utils'

export default function ReviewsPage() {
  const [ratingFilter, setRatingFilter] = useState<number | null>(null)

  const { data, isPending: isLoading } = useQuery({
    queryKey: ['reviews', ratingFilter],
    queryFn: () => apiClient.get('/reviews/', {
      params: { rating: ratingFilter || undefined }
    }).then(res => res.data)
  })

  const reviews = data?.results || []

  // Calculate rating distribution
  const ratingDist = [5, 4, 3, 2, 1].map(r => ({
    stars: r,
    count: reviews.filter((rv: any) => rv.rating === r).length,
    pct: reviews.length > 0 ? Math.round((reviews.filter((rv: any) => rv.rating === r).length / reviews.length) * 100) : 0
  }))

  const avgRating = reviews.length > 0 
    ? (reviews.reduce((s: number, r: any) => s + r.rating, 0) / reviews.length).toFixed(1) 
    : '0'

  return (
    <div className="space-y-6 animate-fade-in" dir="rtl">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-yellow-500 to-orange-600 flex items-center justify-center shadow-lg shadow-yellow-500/20">
          <Star className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-3xl font-black">تقييمات العملاء</h2>
          <p className="text-sm text-muted-foreground">اطلع على آراء عملائك وحسّن خدماتك</p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Average Rating */}
        <Card className="glass-card border-none glow-orange">
          <CardContent className="p-6 flex flex-col items-center justify-center text-center">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-yellow-500/20 to-orange-500/20 flex items-center justify-center mb-3">
              <span className="text-4xl font-black text-yellow-400">{avgRating}</span>
            </div>
            <div className="flex items-center gap-1 mb-1">
              {Array(5).fill(0).map((_, i) => (
                <Star key={i} className={cn("w-4 h-4", i < Math.round(Number(avgRating)) ? "text-yellow-400 fill-yellow-400" : "text-gray-600")} />
              ))}
            </div>
            <p className="text-sm text-muted-foreground">{reviews.length} تقييم</p>
          </CardContent>
        </Card>

        {/* Rating Distribution */}
        <Card className="glass-card border-none col-span-2">
          <CardHeader>
            <CardTitle className="text-base">توزيع التقييمات</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {ratingDist.map(r => (
              <div key={r.stars} className="flex items-center gap-3">
                <button 
                  onClick={() => setRatingFilter(ratingFilter === r.stars ? null : r.stars)}
                  className={cn("flex items-center gap-1 w-16 text-sm shrink-0 hover:text-yellow-400 transition-colors", ratingFilter === r.stars && "text-yellow-400 font-bold")}
                >
                  <Star className="w-3 h-3 fill-current text-yellow-400" /> {r.stars}
                </button>
                <div className="flex-1 h-3 bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-l from-yellow-500 to-orange-500 rounded-full transition-all duration-500" style={{ width: `${r.pct}%` }} />
                </div>
                <span className="text-xs text-muted-foreground w-12 text-left">{r.count} ({r.pct}%)</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Filter Bar */}
      {ratingFilter && (
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">فلترة حسب:</span>
          <Button variant="secondary" size="sm" className="rounded-lg gap-1 h-7 text-xs" onClick={() => setRatingFilter(null)}>
            {ratingFilter} نجوم <span className="text-muted-foreground">✕</span>
          </Button>
        </div>
      )}

      {/* Reviews List */}
      <div className="space-y-4">
        {isLoading ? (
          Array(4).fill(0).map((_, i) => <Skeleton key={i} className="h-28 w-full rounded-2xl" />)
        ) : reviews.length === 0 ? (
          <Card className="glass-card border-none">
            <CardContent className="py-16 text-center">
              <MessageSquare className="w-16 h-16 mx-auto text-muted-foreground opacity-20 mb-4" />
              <p className="text-lg font-medium text-muted-foreground">لا توجد تقييمات بعد</p>
              <p className="text-sm text-muted-foreground mt-1">عندما يقيّم العملاء منتجاتك ستظهر هنا</p>
            </CardContent>
          </Card>
        ) : (
          reviews.map((review: any) => (
            <Card key={review.id} className="glass-card border-none hover:scale-[1.005] transition-all">
              <CardContent className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500/20 to-violet-500/20 flex items-center justify-center font-bold text-sm text-blue-400">
                      {review.reviewer_name?.[0]?.toUpperCase() || '?'}
                    </div>
                    <div>
                      <p className="font-bold text-sm">{review.reviewer_name}</p>
                      <p className="text-[11px] text-muted-foreground">{review.product_name}</p>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <div className="flex items-center gap-0.5">
                      {Array(5).fill(0).map((_, i) => (
                        <Star key={i} className={cn("w-3.5 h-3.5", i < review.rating ? "text-yellow-400 fill-yellow-400" : "text-gray-600")} />
                      ))}
                    </div>
                    <p className="text-[10px] text-muted-foreground">{new Date(review.created_at).toLocaleDateString('ar-DZ')}</p>
                  </div>
                </div>
                <p className="text-sm p-3 rounded-xl bg-white/5 border border-white/5">
                  {review.comment || 'لا يوجد تعليق.'}
                </p>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
