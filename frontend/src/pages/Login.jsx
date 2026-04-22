import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Eye, EyeOff, LogIn } from 'lucide-react'

export default function Login() {
  const { login } = useAuth()
  const navigate   = useNavigate()

  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [showPw, setShowPw]     = useState(false)
  const [error, setError]       = useState('')
  const [loading, setLoading]   = useState(false)

  const roleRedirect = user => {
    const r = (user?.type ?? user?.roles?.[0] ?? '').toLowerCase()
    if (r === 'superadmin' || r === 'admin') return '/admin'
    if (r === 'client') return '/client'
    return '/employee'
  }

  const handleSubmit = async e => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const u = await login(email, password)
      navigate(roleRedirect(u), { replace: true })
    } catch (err) {
      setError(err.response?.data?.message ?? 'Invalid credentials. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const quick = role => {
    const map = {
      admin:    ['superadmin@smarthr.com', 'password'],
      employee: ['employee@smarthr.com',   'password'],
      client:   ['client@smarthr.com',     'password'],
    }
    setEmail(map[role][0])
    setPassword(map[role][1])
  }

  return (
    <div className="login-layout">
      {/* Left hero */}
      <div className="login-panel-left">
        <div className="login-hero">
          <div style={{display:'flex',alignItems:'center',gap:12,marginBottom:32}}>
            <div className="sidebar-brand-logo" style={{width:42,height:42,fontSize:'1.2rem'}}>S</div>
            <span style={{fontWeight:800,fontSize:'1.2rem'}}>Smart<span style={{color:'var(--c-primary)'}}>HR</span></span>
          </div>
          <h1>Manage your<br/><span>people &amp; work</span><br/>smarter.</h1>
          <p style={{marginTop:20}}>
            A unified platform for HR, payroll, attendance, client management,
            tickets, and more — all in one place.
          </p>

          {/* Feature pills */}
          <div style={{display:'flex',gap:10,flexWrap:'wrap',marginTop:32}}>
            {['👥 Employee CRUD','💰 Payroll','🎫 Tickets','📊 Analytics','🏢 Client Portal'].map(f=>(
              <span key={f} style={{
                background:'rgba(108,99,255,.12)',border:'1px solid rgba(108,99,255,.25)',
                padding:'5px 14px',borderRadius:20,fontSize:'.8rem',color:'var(--c-primary)',fontWeight:500
              }}>{f}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Right form */}
      <div className="login-panel-right">
        <div className="login-form-box">
          <h2>Welcome back</h2>
          <p>Sign in to your SmartHR account</p>

          {error && (
            <div style={{
              background:'rgba(239,68,68,.1)',border:'1px solid rgba(239,68,68,.25)',
              borderRadius:'var(--radius-sm)',padding:'10px 14px',marginBottom:16,
              fontSize:'.875rem',color:'var(--c-danger)'
            }}>{error}</div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="field">
              <label>Email</label>
              <input
                type="email" required
                value={email} onChange={e=>setEmail(e.target.value)}
                placeholder="you@company.com"
              />
            </div>

            <div className="field">
              <label>Password</label>
              <div style={{position:'relative'}}>
                <input
                  type={showPw?'text':'password'} required
                  value={password} onChange={e=>setPassword(e.target.value)}
                  placeholder="••••••••"
                  style={{paddingRight:40,width:'100%'}}
                />
                <button
                  type="button"
                  onClick={()=>setShowPw(v=>!v)}
                  style={{position:'absolute',right:12,top:'50%',transform:'translateY(-50%)',background:'none',border:'none',color:'var(--c-muted)'}}
                >
                  {showPw ? <EyeOff size={16}/> : <Eye size={16}/>}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
              style={{width:'100%',justifyContent:'center',marginTop:8,padding:'11px'}}
            >
              {loading ? 'Signing in…' : <><LogIn size={16}/>Sign In</>}
            </button>
          </form>

          {/* Quick login shortcuts */}
          <div style={{marginTop:28,paddingTop:20,borderTop:'1px solid var(--c-border)'}}>
            <p style={{fontSize:'.78rem',color:'var(--c-muted)',marginBottom:10,textAlign:'center'}}>Quick demo logins</p>
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:8}}>
              {[['Admin','admin'],['Employee','employee'],['Client','client']].map(([l,r])=>(
                <button
                  key={r}
                  type="button"
                  className="btn btn-secondary"
                  style={{justifyContent:'center',fontSize:'.8rem',padding:'7px 8px'}}
                  onClick={()=>quick(r)}
                >{l}</button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
