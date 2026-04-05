import { STATUS_LABELS, STATUS_COLORS, OrderStatus } from '../../types/order'
import { cn } from '../../lib/utils'

export function StatusBadge({ status }: { status: OrderStatus }) {
  return (
    <span className={cn('px-2 py-1 rounded-full text-xs font-medium', STATUS_COLORS[status])}>
      {STATUS_LABELS[status]}
    </span>
  )
}
