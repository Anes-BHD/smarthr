import { useState, useEffect } from 'react'
import { clientApi } from '../../lib/api'
import { Spinner, EmptyState, StatusBadge, Modal, Input, Textarea, Select } from '../../components/ui/index'
import { Plus } from 'lucide-react'

export default function ClientTickets() {
  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(true)
  const [showM,   setShowM]   = useState(false)
  const [saving,  setSaving]  = useState(false)
  const [form,    setForm]    = useState({ title:'', description:'', priority:'medium' })

  const load = () => {
    setLoading(true)
    clientApi.getTickets()
      .then(r => setTickets(r.data?.data ?? []))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const submit = async e => {
    e.preventDefault(); setSaving(true)
    try {
      await clientApi.createTicket(form)
      setShowM(false); setForm({ title:'', description:'', priority:'medium' })
      load()
    } catch {} finally { setSaving(false) }
  }

  return (
    <>
      <div className="page-header">
        <h1>Support Tickets</h1>
        <p>Submit and track support requests.</p>
      </div>

      <div className="card">
        <div className="toolbar">
          <div className="toolbar-right">
            <button className="btn btn-primary" onClick={() => setShowM(true)}><Plus size={15}/>New Ticket</button>
          </div>
        </div>

        {loading
          ? <Spinner/>
          : tickets.length === 0
            ? <EmptyState title="No tickets" desc="Need help? Create a new support ticket."/>
            : (
            <div className="table-wrap">
              <table>
                <thead><tr>
                  <th>Ticket ID</th><th>Subject</th><th>Priority</th><th>Status</th><th>Created</th>
                </tr></thead>
                <tbody>
                  {tickets.map(t => (
                    <tr key={t.id}>
                      <td style={{color:'var(--c-muted)',fontSize:'.8rem'}}>#{t.id}</td>
                      <td>
                        <div className="font-semibold">{t.title}</div>
                      </td>
                      <td><StatusBadge status={t.priority ?? 'medium'}/></td>
                      <td><StatusBadge status={t.status ?? 'open'}/></td>
                      <td style={{color:'var(--c-muted)',fontSize:'.8rem'}}>{t.created_at?.slice(0,10)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
      </div>

      <Modal open={showM} onClose={() => setShowM(false)} title="Create Ticket">
        <form onSubmit={submit}>
          <Input label="Subject" value={form.title} onChange={e => setForm(f => ({...f, title:e.target.value}))} required/>
          <Select label="Priority" value={form.priority} onChange={e => setForm(f => ({...f, priority:e.target.value}))}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </Select>
          <Textarea label="Description" value={form.description} onChange={e => setForm(f => ({...f, description:e.target.value}))} required/>
          
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={() => setShowM(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Submitting…' : 'Submit'}</button>
          </div>
        </form>
      </Modal>
    </>
  )
}
