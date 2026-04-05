import { Card, CardContent } from '../ui/card'
import { Skeleton } from '../ui/skeleton'
import { cn } from '../../lib/utils'

interface KpiCardProps {
  title:       string
  value:       string | number
  subtitle?:   string
  description?: string
  change_pct?: number
  icon:        React.ReactNode
  loading?:    boolean
  variant?:    'default' | 'warning' | 'danger' | 'secondary'
  className?:  string
  glowColor?:  string
}

export function KpiCard({ 
  title, value, subtitle, description, change_pct, icon, loading, 
  variant = 'default', className, glowColor 
}: KpiCardProps) {
  if (loading) {
    return (
      <Card className={cn("glass-card border-none", className)}>
        <CardContent className="p-6">
          <Skeleton className="h-4 w-24 mb-4" />
          <Skeleton className="h-8 w-32 mb-2" />
          <Skeleton className="h-3 w-20" />
        </CardContent>
      </Card>
    )
  }

  const isPositive = (change_pct ?? 0) >= 0

  return (
    <Card className={cn(
      "glass-card border-none overflow-hidden group hover:scale-[1.02] transition-all duration-300 animate-fade-in",
      variant === 'warning' && 'border-yellow-500/30',
      variant === 'danger'  && 'border-red-500/30',
      variant === 'secondary' && 'bg-white/5 backdrop-blur-sm',
      glowColor,
      className
    )}>
      <CardContent className={cn("relative", variant === 'secondary' ? "p-4" : "p-6")}>
        {/* Decorative gradient */}
        {variant !== 'secondary' && (
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-l from-transparent via-blue-500/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        )}
        
        <div className={cn("flex items-center justify-between", variant === 'secondary' ? "mb-2" : "mb-3")}>
          <p className={cn("text-muted-foreground font-medium", variant === 'secondary' ? "text-xs" : "text-sm")}>{title}</p>
          <div className={cn(
            "rounded-xl bg-white/5 flex items-center justify-center group-hover:scale-110 transition-transform",
            variant === 'secondary' ? "w-8 h-8" : "w-10 h-10"
          )}>
            {icon}
          </div>
        </div>
        
        <p className={cn("font-black tracking-tight", variant === 'secondary' ? "text-xl" : "text-3xl")}>{value}</p>
        
        {description && (
          <p className="text-[10px] text-muted-foreground mt-2 leading-relaxed opacity-70">{description}</p>
        )}

        {subtitle && (
          <p className="text-xs text-muted-foreground mt-2">{subtitle}</p>
        )}
        
        {change_pct !== undefined && (
          <div className={cn(
            'flex items-center gap-1 mt-3 text-xs font-semibold px-2 py-1 rounded-lg w-fit',
            isPositive ? 'text-emerald-400 bg-emerald-500/10' : 'text-red-400 bg-red-500/10'
          )}>
            <span>{isPositive ? '↑' : '↓'}</span>
            <span>{Math.abs(change_pct)}%</span>
            <span className="text-muted-foreground font-normal mr-1">من الشهر الماضي</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
