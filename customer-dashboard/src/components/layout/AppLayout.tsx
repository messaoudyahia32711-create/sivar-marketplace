import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, ShoppingCart, Settings, LogOut, Menu, X, User,
  Bell, Sun, Moon, Search, Mail, Home
} from 'lucide-react'
import { cn } from '../../lib/utils'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { useAuth } from '../../hooks/useAuth'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../api/client'

const menuItems = [
  { icon: LayoutDashboard, label: 'لوحة التحكم', path: '/dashboard', color: 'text-blue-400' },
  { icon: ShoppingCart,    label: 'الطلبات',      path: '/orders',    color: 'text-amber-400' },
  { icon: Mail,            label: 'الرسائل',      path: '/messages',  color: 'text-indigo-400' },
  { icon: Settings,        label: 'الإعدادات',    path: '/settings',  color: 'text-gray-400' },
]

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isLight, setIsLight] = useState(() => localStorage.getItem('theme') === 'light')
  const { pathname } = useLocation()
  const { logout, getUser } = useAuth()
  const user = getUser()

  // Fetch orders once to compute pending count (no separate endpoint needed)
  const { data: ordersData } = useQuery({
    queryKey: ['customer-orders-for-badge'],
    queryFn: () => apiClient.get('/orders/').then(r => r.data),
    refetchInterval: 30000,
    retry: 1,
  })
  const ordersList = ordersData?.orders || ordersData?.results || ordersData || []
  const pendingCount = ordersList.filter((o: any) => ['PENDING', 'PROCESSING', 'SHIPPED'].includes(o.status)).length

  // Theme toggle
  useEffect(() => {
    document.documentElement.classList.toggle('light', isLight)
    localStorage.setItem('theme', isLight ? 'light' : 'dark')
  }, [isLight])

  // Today's date in Arabic
  const todayAr = new Date().toLocaleDateString('ar-DZ', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  })

  return (
    <div className="min-h-screen bg-background flex bg-grid" dir="rtl">
      {/* ════ Sidebar Desktop ════ */}
      <aside className="hidden lg:flex flex-col w-72 glass-sidebar sticky top-0 h-screen z-50">
        {/* Logo */}
        <div className="p-6 border-b border-white/5 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <User className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold">لوحة الزبون</h1>
            <p className="text-[10px] text-muted-foreground">Algerian Marketplace</p>
          </div>
        </div>
        
        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {menuItems.map((item) => {
            const isActive = pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group relative",
                  isActive 
                    ? "bg-white/10 text-white shadow-lg" 
                    : "hover:bg-white/5 text-muted-foreground hover:text-white"
                )}
              >
                {isActive && (
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-blue-500 rounded-l-full" />
                )}
                <item.icon className={cn("w-5 h-5 transition-colors", isActive ? item.color : "group-hover:" + item.color)} />
                <span className="font-medium text-sm">{item.label}</span>
                {/* Badge for orders */}
                {item.path === '/orders' && pendingCount > 0 && (
                  <span className="mr-auto bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[20px] text-center animate-pulse">
                    {pendingCount}
                  </span>
                )}
              </Link>
            )
          })}
        </nav>

        {/* ════ Return to Main Platform (Desktop) ════ */}
        <div className="px-4 pb-4">
          <a
            href="http://localhost:8000/"
            className="group relative flex items-center justify-center gap-2 w-full py-3 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#b38b22] text-[#0F0F0F] font-extrabold text-sm transition-all duration-300 shadow-[0_0_20px_rgba(212,175,55,0.3)] hover:shadow-[0_0_30px_rgba(212,175,55,0.6)] hover:-translate-y-1 overflow-hidden"
          >
            {/* Golden Shimmer Animation */}
            <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/60 to-transparent group-hover:translate-x-full transition-transform duration-[1200ms] ease-in-out" />
            <Home className="w-5 h-5 drop-shadow-sm" />
            <span className="drop-shadow-sm">الصفحة الرئيسية</span>
          </a>
        </div>

        {/* User Section */}
        <div className="p-4 border-t border-white/5 space-y-3">
          <div className="flex items-center gap-3 px-3 py-2 rounded-xl bg-white/5">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center font-bold text-white text-sm shadow-md">
              {user?.username?.[0]?.toUpperCase() || 'م'}
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="text-sm font-medium truncate">{user?.username}</p>
              <p className="text-[10px] text-muted-foreground">حساب زبون</p>
            </div>
          </div>
          <Button 
            variant="ghost" 
            className="w-full justify-start text-red-400 hover:text-red-300 hover:bg-red-500/10 gap-3 rounded-xl"
            onClick={logout}
          >
            <LogOut className="w-4 h-4" />
            <span className="text-sm">تسجيل الخروج</span>
          </Button>
        </div>
      </aside>

      {/* ════ Mobile Sidebar Overlay ════ */}
      <div className={cn(
        "lg:hidden fixed inset-0 z-50 bg-black/60 backdrop-blur-sm transition-opacity duration-300",
        sidebarOpen ? "opacity-100" : "opacity-0 pointer-events-none"
      )} onClick={() => setSidebarOpen(false)} />
      
      <aside className={cn(
        "lg:hidden fixed inset-y-0 right-0 z-50 w-72 glass-sidebar transition-transform duration-300 transform",
        sidebarOpen ? "translate-x-0" : "translate-x-full"
      )}>
        <div className="p-6 border-b border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold">لوحة الزبون</span>
          </div>
          <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(false)} className="rounded-xl">
            <X className="w-5 h-5" />
          </Button>
        </div>
        <nav className="p-4 space-y-1">
          {menuItems.map((item) => {
            const isActive = pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={cn(
                  "flex items-center gap-3 px-4 py-3 rounded-xl transition-all",
                  isActive 
                    ? "bg-white/10 text-white" 
                    : "hover:bg-white/5 text-muted-foreground"
                )}
              >
                <item.icon className={cn("w-5 h-5", isActive && item.color)} />
                <span className="font-medium text-sm">{item.label}</span>
              </Link>
            )
          })}
        </nav>

        {/* ════ Return to Main Platform (Mobile) ════ */}
        <div className="p-4 mt-auto border-t border-white/5">
          <a
            href="http://localhost:8000/"
            className="group relative flex items-center justify-center gap-2 w-full py-3 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#b38b22] text-[#0F0F0F] font-extrabold text-sm transition-all duration-300 shadow-[0_0_20px_rgba(212,175,55,0.3)] hover:shadow-[0_0_30px_rgba(212,175,55,0.6)] overflow-hidden"
          >
            <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/60 to-transparent group-hover:translate-x-full transition-transform duration-[1200ms] ease-in-out" />
            <Home className="w-5 h-5 drop-shadow-sm" />
            <span className="drop-shadow-sm">الصفحة الرئيسية</span>
          </a>
        </div>
      </aside>

      {/* ════ Main Content ════ */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-16 glass-header flex items-center justify-between px-6 sticky top-0 z-40">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" className="lg:hidden rounded-xl" onClick={() => setSidebarOpen(true)}>
              <Menu className="w-5 h-5" />
            </Button>
            
            {/* Search */}
            <div className="hidden md:flex items-center gap-2 relative">
              <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input 
                placeholder="بحث سريع..." 
                className="w-64 pr-10 h-9 text-sm rounded-xl bg-white/5 border-white/10 focus:border-blue-500/50 focus:ring-blue-500/20"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Today's date */}
            <span className="hidden lg:block text-xs text-muted-foreground ml-4">{todayAr}</span>

            {/* Theme Toggle */}
            <Button 
              variant="ghost" 
              size="icon" 
              className="rounded-xl h-9 w-9 hover:bg-white/10"
              onClick={() => setIsLight(!isLight)}
            >
              {isLight ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4 text-yellow-400" />}
            </Button>
            
            {/* Notifications */}
            <Button variant="ghost" size="icon" className="rounded-xl h-9 w-9 hover:bg-white/10 relative">
              <Bell className="w-4 h-4" />
              {pendingCount > 0 && (
                <span className="absolute -top-1 -left-1 w-5 h-5 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center animate-pulse">
                  {pendingCount > 9 ? '9+' : pendingCount}
                </span>
              )}
            </Button>
          </div>
        </header>

        {/* Page Content */}
        <div className="p-6 overflow-y-auto flex-1">
          {children}
        </div>
      </main>
    </div>
  )
}
