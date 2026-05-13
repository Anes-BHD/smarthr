import { useState, useEffect } from 'react'
import { employeeApi } from '../../lib/api'
import { Spinner, EmptyState, StatusBadge } from '../../components/ui/index'
import { Plus } from 'lucide-react'

export default function EmployeeLeaves() {
  const [leaves,  setLeaves]  = useState([])
  const [loading, setLoading] = useState(true)
  const [showM,   setShowM]   = useState(false)
  const [form,    setForm]    = useState({ reason:'', start_date:'', end_date:'' })
  const [saving,  setSaving]  = useState(false)

  useEffect(() => {
    employeeApi.getTickets()
      .then(r => setLeaves(r.data?.data ?? []))
      .finally(() => setLoading(false))
  }, [])

  const submit = async e => {
    e.preventDefault(); setSaving(true)
    try {
      await employeeApi.createTicket({ ...form, title:`Leave Request: ${form.start_date}`, type:'leave' })
      setShowM(false)
    } catch {} finally { setSaving(false) }
  }

  return (
    <>
      <div className="page-header">
        <h1>My Leaves</h1>
        <p>Track your leave history and submit new requests.</p>
      </div>

      <div className="card">
        <div className="toolbar">
          <div className="toolbar-right">
            <button className="btn btn-primary" onClick={()=>setShowM(true)}><Plus size={15}/>Request Leave</button>
          </div>
        </div>

        {loading
          ? <Spinner/>
          : leaves.length === 0
            ? <EmptyState title="No leave history" desc="Submit a leave request to get started."/>
            : (
            <div className="table-wrap">
              <table>
                <thead><tr>
                  <th>Title</th><th>Status</th><th>Submitted</th>
                </tr></thead>
                <tbody>
                  {leaves.filter(l=>(l.type??'').toLowerCase()==='leave' || (l.title??'').toLowerCase().includes('leave')).map(l=>(
                    <tr key={l.id}>
                      <td>{l.title}</td>
                      <td><StatusBadge status={l.status ?? 'pending'}/></td>
                      <td style={{color:'var(--c-muted)',fontSize:'.8rem'}}>{l.created_at?.slice(0,10)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
      </div>

      {showM && (
        <div className="modal-overlay" onClick={e=>e.target===e.currentTarget&&setShowM(false)}>
          <div className="modal">
            <div className="modal-header"><h2>Request Leave</h2><button className="btn-icon" onClick={()=>setShowM(false)}>✕</button></div>
            <form onSubmit={submit}>
              <div className="field-row">
                <div className="field"><label>Start Date</label><input type="date" value={form.start_date} onChange={e=>setForm(f=>({...f,start_date:e.target.value}))} required/></div>
                <div className="field"><label>End Date</label><input type="date" value={form.end_date} onChange={e=>setForm(f=>({...f,end_date:e.target.value}))} required/></div>
              </div>
              <div className="field"><label>Reason</label><textarea value={form.reason} onChange={e=>setForm(f=>({...f,reason:e.target.value}))} placeholder="Reason for leave…" required/></div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={()=>setShowM(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>{saving?'Submitting…':'Submit Request'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  )
}
