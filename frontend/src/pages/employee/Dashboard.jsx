import { useEffect, useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import { employeeApi } from '../../lib/api'
import { Spinner } from '../../components/ui/index'
import { useNavigate } from 'react-router-dom'
import { User, CreditCard, Ticket, CalendarDays, ArrowRight } from 'lucide-react'

export default function EmployeeDashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [payslips, setPayslips] = useState([])
  const [tickets,  setTickets]  = useState([])
  const [loading,  setLoading]  = useState(true)

  useEffect(() => {
    Promise.all([employeeApi.getPayslips(), employeeApi.getTickets()])
      .then(([p, t]) => {
        setPayslips(p.data?.data ?? [])
        setTickets(t.data?.data  ?? [])
      }).finally(() => setLoading(false))
  }, [])

  const name = `${user?.firstname ?? user?.name ?? ''} ${user?.lastname ?? ''}`.trim()

  const quickActions = [
    { label:'My Profile',  icon:User,        path:'/employee/profile',  color:'purple' },
    { label:'Payslips',    icon:CreditCard,   path:'/employee/payslips', color:'green'  },
    { label:'Leaves',      icon:CalendarDays, path:'/employee/leaves',   color:'yellow' },
    { label:'Tickets',     icon:Ticket,       path:'/employee/tickets',  color:'blue'   },
  ]

  if (loading) return <Spinner/>

  return (
    <>
      <div className="page-header">
        <h1>Hello, {name} 👋</h1>
        <p>Here's your personal dashboard overview.</p>
      </div>

      {/* Quick stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon purple"><CreditCard size={22}/></div>
          <div><div className="stat-value">{payslips.length}</div><div className="stat-label">Payslips</div></div>
        </div>
        <div className="stat-card">
          <div className="stat-icon blue"><Ticket size={22}/></div>
          <div>
            <div className="stat-value">{tickets.filter(t=>(t.status??'').toLowerCase()==='open').length}</div>
            <div className="stat-label">Open Tickets</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon green"><CreditCard size={22}/></div>
          <div>
            <div className="stat-value">
              ${payslips.reduce((s,p)=>s+Number(p.net_salary??0),0).toLocaleString()}
            </div>
            <div className="stat-label">Total Net Pay</div>
          </div>
        </div>
      </div>

      {/* Quick actions */}
      <div className="card" style={{marginBottom:20}}>
        <div className="card-title">Quick Actions</div>
        <div className="grid-2">
          {quickActions.map(qa => (
            <button
              key={qa.path}
              onClick={()=>navigate(qa.path)}
              style={{
                display:'flex',alignItems:'center',gap:14,padding:'16px',
                background:'var(--c-surface2)',border:'1px solid var(--c-border)',
                borderRadius:'var(--radius)',cursor:'pointer',transition:'all var(--transition)',
                textAlign:'left',
              }}
              onMouseOver={e=>e.currentTarget.style.borderColor='var(--c-primary)'}
              onMouseOut={e=>e.currentTarget.style.borderColor='var(--c-border)'}
            >
              <div className={`stat-icon ${qa.color}`}><qa.icon size={20}/></div>
              <span className="font-semibold" style={{flex:1,color:'var(--c-text)'}}>{qa.label}</span>
              <ArrowRight size={16} color="var(--c-muted)"/>
            </button>
          ))}
        </div>
      </div>

      {/* Recent payslips */}
      {payslips.length > 0 && (
        <div className="card">
          <div className="card-title">Recent Payslips</div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Date</th><th>Type</th><th>Net Salary</th></tr></thead>
              <tbody>
                {payslips.slice(0,5).map(p=>(
                  <tr key={p.id}>
                    <td>{p.payslip_date ?? p.created_at?.slice(0,10)}</td>
                    <td>{p.type}</td>
                    <td className="font-semibold">${Number(p.net_salary??0).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  )
}
