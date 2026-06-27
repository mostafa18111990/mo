import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/auth'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import TenantsPage from './pages/TenantsPage'
import TenantDetailPage from './pages/TenantDetailPage'
import NewTenantPage from './pages/NewTenantPage'
import AdminPage from './pages/AdminPage'
import PlansPage from './pages/PlansPage'
import SuspendedPage from './pages/SuspendedPage'

function RequireAuth({ children }) {
  const token = useAuthStore((s) => s.token)
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/suspended" element={<SuspendedPage />} />
        <Route path="/tenants" element={<RequireAuth><TenantsPage /></RequireAuth>} />
        <Route path="/tenants/new" element={<RequireAuth><NewTenantPage /></RequireAuth>} />
        <Route path="/tenants/:id" element={<RequireAuth><TenantDetailPage /></RequireAuth>} />
        <Route path="/admin" element={<RequireAuth><AdminPage /></RequireAuth>} />
        <Route path="/plans" element={<PlansPage />} />
        <Route path="/" element={<Navigate to="/tenants" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
