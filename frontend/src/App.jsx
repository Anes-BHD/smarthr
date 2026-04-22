import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { Spinner } from './components/ui/index'

import AppShell from './components/layout/AppShell'
import Login from './pages/Login'

// Admin Pages
import AdminDashboard from './pages/admin/Dashboard'
import AdminEmployees from './pages/admin/Employees'
import AdminLeaves from './pages/admin/Leaves'
import AdminPayroll from './pages/admin/Payroll'
import AdminTickets from './pages/admin/Tickets'
import AdminUsers from './pages/admin/Users'
import AdminClients from './pages/admin/Clients'
import AdminProjects from './pages/admin/Projects'
import AdminSales from './pages/admin/Sales'
import AdminAccounting from './pages/admin/Accounting'
import AdminChatbot from './pages/admin/Chatbot'

// Employee Pages
import EmployeeDashboard from './pages/employee/Dashboard'
import EmployeeProfile from './pages/employee/Profile'
import EmployeeLeaves from './pages/employee/Leaves'
import EmployeePayslips from './pages/employee/Payslips'
import EmployeeTickets from './pages/employee/Tickets'

// Client Pages
import ClientDashboard from './pages/client/Dashboard'
import ClientProjects from './pages/client/Projects'
import ClientInvoices from './pages/client/Invoices'
import ClientTickets from './pages/client/Tickets'
import ClientProfile from './pages/client/Profile'

function RequireAuth({ children, allowedRoles }) {
  const { user, token, loading } = useAuth()
  const location = useLocation()

  if (loading) return <Spinner />
  if (!token || !user) return <Navigate to="/login" state={{ from: location }} replace />

  const role = (user.type ?? user.roles?.[0] ?? 'employee').toLowerCase()
  const isSuperadmin = role === 'superadmin'

  if (!isSuperadmin && allowedRoles && !allowedRoles.includes(role)) {
    // Redirect to default dashboard based on their role
    if (role === 'admin') return <Navigate to="/admin" replace />
    if (role === 'client') return <Navigate to="/client" replace />
    return <Navigate to="/employee" replace />
  }

  return children
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />

          {/* ── Admin Routes ── */}
          <Route path="/admin/*" element={
            <RequireAuth allowedRoles={['admin', 'superadmin']}>
              <AppShell>
                <Routes>
                  <Route path="/" element={<AdminDashboard />} />
                  <Route path="/chatbot" element={<AdminChatbot />} />
                  <Route path="/employees" element={<AdminEmployees />} />
                  <Route path="/clients" element={<AdminClients />} />
                  <Route path="/projects" element={<AdminProjects />} />
                  <Route path="/sales" element={<AdminSales />} />
                  <Route path="/accounting" element={<AdminAccounting />} />
                  <Route path="/leaves" element={<AdminLeaves />} />
                  <Route path="/payroll" element={<AdminPayroll />} />
                  <Route path="/tickets" element={<AdminTickets />} />
                  <Route path="/users" element={<AdminUsers />} />
                </Routes>
              </AppShell>
            </RequireAuth>
          } />

          {/* ── Employee Routes ── */}
          <Route path="/employee/*" element={
            <RequireAuth allowedRoles={['employee']}>
              <AppShell>
                <Routes>
                  <Route path="/" element={<EmployeeDashboard />} />
                  <Route path="/profile" element={<EmployeeProfile />} />
                  <Route path="/leaves" element={<EmployeeLeaves />} />
                  <Route path="/payslips" element={<EmployeePayslips />} />
                  <Route path="/tickets" element={<EmployeeTickets />} />
                </Routes>
              </AppShell>
            </RequireAuth>
          } />

          {/* ── Client Routes ── */}
          <Route path="/client/*" element={
            <RequireAuth allowedRoles={['client']}>
              <AppShell>
                <Routes>
                  <Route path="/" element={<ClientDashboard />} />
                  <Route path="/projects" element={<ClientProjects />} />
                  <Route path="/invoices" element={<ClientInvoices />} />
                  <Route path="/tickets" element={<ClientTickets />} />
                  <Route path="/profile" element={<ClientProfile />} />
                </Routes>
              </AppShell>
            </RequireAuth>
          } />

          {/* Default Redirect based on role */}
          <Route path="*" element={<RequireAuth><Navigate to="/employee" replace /></RequireAuth>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
