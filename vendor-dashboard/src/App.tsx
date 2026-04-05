import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { Toaster } from 'sonner'
import AppLayout from './components/layout/AppLayout'
import LoginPage from './pages/Login/LoginPage'
import DashboardPage from './pages/Dashboard/DashboardPage'
import OrdersPage from './pages/Orders/OrdersPage'
import ProductsPage from './pages/Products/ProductsPage'
import AddProductPage from './pages/Products/AddProductPage'
import ServicesPage from './pages/Services/ServicesPage'
import AddServicePage from './pages/Services/AddServicePage'
import CouponsPage from './pages/Coupons/CouponsPage'
import AnalyticsPage from './pages/Analytics/AnalyticsPage'
import ReviewsPage from './pages/Reviews/ReviewsPage'
import MessagesPage from './pages/Messages/MessagesPage'
import SettingsPage from './pages/Settings/SettingsPage'
import StorePage from './pages/StorePage/StorePage'
import { useAuth } from './hooks/useAuth'

// مكون حماية المسارات
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  
  if (!isAuthenticated()) {
    // التحويل فوراً إلى البوابة الرئيسية عند غياب المصادقة
    window.location.href = 'http://localhost:8000/login/'
    return null
  }
  return <AppLayout>{children}</AppLayout>
}

function NavigateWithParams({ to }: { to: string }) {
  const { search } = useLocation()
  return <Navigate to={`${to}${search}`} replace />
}

function App() {
  return (
    <BrowserRouter basename="/">
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        <Route path="/dashboard" element={
          <ProtectedRoute><DashboardPage /></ProtectedRoute>
        } />
        
        <Route path="/orders" element={
          <ProtectedRoute><OrdersPage /></ProtectedRoute>
        } />
        
        <Route path="/products" element={
          <ProtectedRoute><ProductsPage /></ProtectedRoute>
        } />
        <Route path="/products/new" element={
          <ProtectedRoute><AddProductPage /></ProtectedRoute>
        } />

        <Route path="/services" element={
          <ProtectedRoute><ServicesPage /></ProtectedRoute>
        } />
        <Route path="/services/new" element={
          <ProtectedRoute><AddServicePage /></ProtectedRoute>
        } />

        <Route path="/coupons" element={
          <ProtectedRoute><CouponsPage /></ProtectedRoute>
        } />

        <Route path="/analytics" element={
          <ProtectedRoute><AnalyticsPage /></ProtectedRoute>
        } />

        <Route path="/reviews" element={
          <ProtectedRoute><ReviewsPage /></ProtectedRoute>
        } />

        <Route path="/messages" element={
          <ProtectedRoute><MessagesPage /></ProtectedRoute>
        } />

        <Route path="/settings" element={
          <ProtectedRoute><SettingsPage /></ProtectedRoute>
        } />

        {/* ── Public Store Page (بدون مصادقة) ── */}
        <Route path="/store/:username" element={<StorePage />} />

        {/* Redirects: الحفاظ على المعاملات عند التحويل التلقائي */}
        <Route path="/" element={<NavigateWithParams to="/dashboard" />} />
        <Route path="*" element={<NavigateWithParams to="/dashboard" />} />
      </Routes>
      <Toaster position="top-center" richColors theme="dark" />
    </BrowserRouter>
  )
}

export default App
