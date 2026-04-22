import { useEffect, useState } from 'react'
import { adminApi } from '../../lib/api'
import { Spinner, EmptyState } from '../../components/ui/index'
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts'
import { Users, CreditCard, Ticket, UserCog } from 'lucide-react'

const TICK  = { fill: '#7b82a0', fontSize: 12 }
const GRID  = { stroke: 'rgba(255,255,255,.05)' }

export default function AdminDashboard() {
  const [employees, setEmployees] = useState([])
  const [payslips,  setPayslips]  = useState([])
  const [tickets,   setTickets]   = useState([])
  const [users,     setUsers]     = useState([])
  const [loading,   setLoading]   = useState(true)

  useEffect(() => {
    Promise.all([
      adminApi.getEmployees(),
      adminApi.getPayslips(),
      adminApi.getTickets(),
      adminApi.getUsers(),
    ]).then(([e, p, t, u]) => {
      setEmployees(e.data?.data ?? [])
      setPayslips(p.data?.data  ?? [])
      setTickets(t.data?.data   ?? [])
      setUsers(u.data?.data     ?? [])
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <Spinner />

  // Build monthly payroll chart data from payslips
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  const payrollByMonth = months.map((m, i) => ({
    name: m,
    total: payslips
      .filter(p => new Date(p.payslip_date ?? p.created_at).getMonth() === i)
      .reduce((s, p) => s + Number(p.net_salary ?? p.total ?? 0), 0),
  }))

  // Tickets by status chart
  const statuses = ['open','pending','closed','resolved']
  const ticketData = statuses.map(s => ({
    name: s.charAt(0).toUpperCase() + s.slice(1),
    count: tickets.filter(t => (t.status ?? '').toLowerCase() === s).length,
  }))

  const stats = [
    { label:'Total Employees', value:employees.length, icon:Users,    color:'purple' },
    { label:'Payslips',        value:payslips.length,  icon:CreditCard,color:'green'  },
    { label:'Open Tickets',    value:tickets.filter(t=>(t.status??'').toLowerCase()==='open').length, icon:Ticket, color:'yellow' },
    { label:'Total Users',     value:users.length,     icon:UserCog,  color:'blue'   },
  ]

  return (
    <>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Welcome back — here's what's happening in your organisation.</p>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        {stats.map(s => (
          <div className="stat-card" key={s.label}>
            <div className={`stat-icon ${s.color}`}><s.icon size={22}/></div>
            <div>
              <div className="stat-value">{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="charts-grid">
        <div className="card">
          <div className="card-title">Monthly Payroll</div>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={payrollByMonth}>
              <defs>
                <linearGradient id="pg" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#6c63ff" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#6c63ff" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" {...GRID}/>
              <XAxis dataKey="name" tick={TICK}/>
              <YAxis tick={TICK}/>
              <Tooltip contentStyle={{background:'#1e2130',border:'1px solid rgba(255,255,255,.1)',borderRadius:8,fontSize:12}}/>
              <Area type="monotone" dataKey="total" stroke="#6c63ff" fill="url(#pg)" strokeWidth={2}/>
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-title">Tickets by Status</div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={ticketData} barSize={32}>
              <CartesianGrid strokeDasharray="3 3" {...GRID}/>
              <XAxis dataKey="name" tick={TICK}/>
              <YAxis tick={TICK}/>
              <Tooltip contentStyle={{background:'#1e2130',border:'1px solid rgba(255,255,255,.1)',borderRadius:8,fontSize:12}}/>
              <Bar dataKey="count" fill="#6c63ff" radius={[4,4,0,0]}/>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent employees table */}
      <div className="card">
        <div className="card-title">Recent Employees</div>
        {employees.length === 0
          ? <EmptyState title="No employees yet"/>
          : (
          <div className="table-wrap">
            <table>
              <thead><tr>
                <th>Name</th><th>Email</th><th>Type</th><th>Joined</th>
              </tr></thead>
              <tbody>
                {employees.slice(0,8).map(emp => (
                  <tr key={emp.id}>
                    <td>{emp.firstname} {emp.lastname}</td>
                    <td style={{color:'var(--c-muted)'}}>{emp.email}</td>
                    <td>{emp.type}</td>
                    <td style={{color:'var(--c-muted)',fontSize:'.8rem'}}>
                      {emp.created_at ? new Date(emp.created_at).toLocaleDateString() : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  )
}
