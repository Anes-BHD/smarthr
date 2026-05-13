import { useEffect, useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import { clientApi } from '../../lib/api'
import { Spinner } from '../../components/ui/index'
import { useNavigate } from 'react-router-dom'
import { Briefcase, FileText, Ticket, User, ArrowRight } from 'lucide-react'

export default function ClientDashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [invoices, setInvoices] = useState([])
  const [tickets,  setTickets]  = useState([])
  const [loading,  setLoading]  = useState(true)

  useEffect(() => {
    Promise.all([clientApi.getInvoices(), clientApi.getTickets()])
      .then(([i, t]) => {
        setInvoices(i.data?.data ?? [])
        setTickets(t.data?.data  ?? [])
      }).finally(() => setLoading(false))
  }, [])

  const name = `${user?.firstname ?? user?.name ?? ''} ${user?.lastname ?? ''}`.trim()

  const quickActions = [
    { label:'My Projects', icon:Briefcase, path:'/client/projects', color:'purple' },
    { label:'Invoices',    icon:FileText,  path:'/client/invoices', color:'green'  },
    { label:'Tickets',     icon:Ticket,    path:'/client/tickets',  color:'blue'   },
    { label:'Profile',     icon:User,      path:'/client/profile',  color:'yellow' },
  ]

  if (loading) return <Spinner/>

  return (
    <>
      <div className="page-header">
        <h1>Welcome, {name} 👋</h1>
        <p>Your client portal overview.</p>
      </div>

      {/* Quick stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon green"><FileText size={22}/></div>
          <div><div className="stat-value">{invoices.length}</div><div className="stat-label">Total Invoices</div></div>
        </div>
        <div className="stat-card">
          <div className="stat-icon blue"><Ticket size={22}/></div>
          <div>
            <div className="stat-value">{tickets.filter(t=>(t.status??'').toLowerCase()==='open').length}</div>
            <div className="stat-label">Open Tickets</div>
          </div>
        </div>
      </div>

      {/* Navigation grid */}
      <div className="card" style={{marginBottom:20}}>
        <div className="card-title">Quick Navigation</div>
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
    </>
  )
}
