import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { Toaster } from 'sonner'
import AppLayout from './components/layout/AppLayout'
import LoginPage from './pages/Login/LoginPage'
import DashboardPage from './pages/Dashboard/DashboardPage'
import OrganizationsPage from './pages/Organizations/OrganizationsPage'
import JoinRequestsPage from './pages/JoinRequests/JoinRequestsPage'
import AnalyticsPage from './pages/Analytics/AnalyticsPage'
import MessagesPage from './pages/Messages/MessagesPage'
import SettingsPage from './pages/Settings/SettingsPage'
import TeamPage from './pages/Team/TeamPage'
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
        
        <Route path="/organizations" element={
          <ProtectedRoute><OrganizationsPage /></ProtectedRoute>
        } />
        
        <Route path="/join-requests" element={
          <ProtectedRoute><JoinRequestsPage /></ProtectedRoute>
        } />

        <Route path="/analytics" element={
          <ProtectedRoute><AnalyticsPage /></ProtectedRoute>
        } />

        <Route path="/messages" element={
          <ProtectedRoute><MessagesPage /></ProtectedRoute>
        } />

        <Route path="/team" element={
          <ProtectedRoute><TeamPage /></ProtectedRoute>
        } />

        <Route path="/settings" element={
          <ProtectedRoute><SettingsPage /></ProtectedRoute>
        } />

        {/* Redirects: الحفاظ على المعاملات عند التحويل التلقائي */}
        <Route path="/" element={<NavigateWithParams to="/dashboard" />} />
        <Route path="*" element={<NavigateWithParams to="/dashboard" />} />
      </Routes>
      <Toaster position="top-center" richColors theme="dark" />
    </BrowserRouter>
  )
}

export default App
