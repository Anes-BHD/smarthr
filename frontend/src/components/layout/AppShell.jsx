import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { Avatar } from '../ui/index'
  LayoutDashboard, Users, CreditCard, Ticket, UserCog, Building2,
  Briefcase, FileText, User, CalendarDays, LogOut, ChevronRight,
  UserCheck, Receipt, Calculator, MessageSquare,
} from 'lucide-react'

const navConfig = {
  superadmin: [
    { label: 'Overview', items: [
      { to: '/admin',             icon: LayoutDashboard, label: 'Dashboard' },
      { to: '/admin/chatbot',     icon: MessageSquare,   label: 'AI Assistant' },
      { to: '/admin/employees',   icon: Users,           label: 'Employees' },
      { to: '/admin/clients',     icon: UserCheck,       label: 'Clients' },
      { to: '/admin/projects',    icon: Briefcase,       label: 'Projects' },
      { to: '/admin/sales',       icon: Receipt,         label: 'Sales' },
      { to: '/admin/accounting',  icon: Calculator,      label: 'Accounting' },
      { to: '/admin/leaves',      icon: CalendarDays,    label: 'Leaves' },
      { to: '/admin/payroll',     icon: CreditCard,      label: 'Payroll' },
      { to: '/admin/tickets',     icon: Ticket,          label: 'Tickets' },
      { to: '/admin/users',       icon: UserCog,         label: 'Users' },
    ]},
  ],
  admin: [
    { label: 'Overview', items: [
      { to: '/admin',             icon: LayoutDashboard, label: 'Dashboard' },
      { to: '/admin/chatbot',     icon: MessageSquare,   label: 'AI Assistant' },
      { to: '/admin/employees',   icon: Users,           label: 'Employees' },
      { to: '/admin/clients',     icon: UserCheck,       label: 'Clients' },
      { to: '/admin/projects',    icon: Briefcase,       label: 'Projects' },
      { to: '/admin/sales',       icon: Receipt,         label: 'Sales' },
      { to: '/admin/accounting',  icon: Calculator,      label: 'Accounting' },
      { to: '/admin/leaves',      icon: CalendarDays,    label: 'Leaves' },
      { to: '/admin/payroll',     icon: CreditCard,      label: 'Payroll' },
      { to: '/admin/tickets',     icon: Ticket,          label: 'Tickets' },
      { to: '/admin/users',       icon: UserCog,         label: 'Users' },
    ]},
  ],
  employee: [
    { label: 'My Space', items: [
      { to: '/employee',          icon: LayoutDashboard, label: 'Dashboard' },
      { to: '/employee/profile',  icon: User,            label: 'My Profile' },
      { to: '/employee/leaves',   icon: CalendarDays,    label: 'Leaves' },
      { to: '/employee/payslips', icon: CreditCard,      label: 'Payslips' },
      { to: '/employee/tickets',  icon: Ticket,          label: 'Tickets' },
    ]},
  ],
  client: [
    { label: 'Client Portal', items: [
      { to: '/client',           icon: Building2,  label: 'Overview' },
      { to: '/client/projects',  icon: Briefcase,  label: 'Projects' },
      { to: '/client/invoices',  icon: FileText,   label: 'Invoices' },
      { to: '/client/tickets',   icon: Ticket,     label: 'Tickets' },
      { to: '/client/profile',   icon: User,       label: 'Profile' },
    ]},
  ],
}

export default function AppShell({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const role = user?.type?.toLowerCase() ?? user?.roles?.[0]?.toLowerCase() ?? 'employee'
  const sections = navConfig[role] ?? navConfig.employee

  const handleLogout = async () => {
    await logout()
    navigate('/login', { replace: true })
  }

  const displayName = user
    ? `${user.firstname ?? user.name ?? ''} ${user.lastname ?? ''}`.trim()
    : 'User'

  return (
    <div className="app-shell">
      {/* ── Sidebar ─────────────────────────────────────────────── */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-brand-logo">S</div>
          <div className="sidebar-brand-name">Smart<span>HR</span></div>
        </div>

        <nav className="sidebar-nav">
          {sections.map(sec => (
            <div key={sec.label}>
              <div className="sidebar-section-label">{sec.label}</div>
              {sec.items.map(item => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/admin' || item.to === '/employee' || item.to === '/client'}
                  className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
                >
                  <item.icon size={16} />
                  {item.label}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user">
            <Avatar name={displayName} size="sm" />
            <div className="sidebar-user-info">
              <div className="sidebar-user-name">{displayName}</div>
              <div className="sidebar-user-role">{role}</div>
            </div>
            <button className="sidebar-logout-btn" onClick={handleLogout} title="Sign out">
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>

      {/* ── Main ────────────────────────────────────────────────── */}
      <main className="main-content">
        <div className="page-body">
          {children}
        </div>
      </main>
    </div>
  )
}
