import { useState, useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'
import { employeeApi } from '../../lib/api'
import { Spinner, EmptyState, StatusBadge, Modal, Input } from '../../components/ui/index'
import { Plus } from 'lucide-react'

function monthAgo() {
  const d = new Date(); d.setMonth(d.getMonth() - 1)
  return d.toISOString().slice(0, 10)
}
function today() {
  return new Date().toISOString().slice(0, 10)
}

const TABS = ['Requests', 'Absences']

export default function EmployeeLeaves() {
  const { user } = useAuth()
  const [tab, setTab] = useState('Requests')

  // ── Leave requests (via tickets) ──────────────────────────────────────────
  const [requests, setRequests] = useState([])
  const [reqLoading, setReqLoading] = useState(true)
  const [showM,  setShowM]  = useState(false)
  const [saving, setSaving] = useState(false)
  const [form,   setForm]   = useState({ reason: '', start_date: '', end_date: '' })

  const loadRequests = () => {
    setReqLoading(true)
    employeeApi.getTickets()
      .then(r => {
        const all = r.data?.data ?? []
        setRequests(all.filter(t =>
          (t.type ?? '').toLowerCase() === 'leave' ||
          (t.title ?? '').toLowerCase().includes('leave request')
        ))
      })
      .finally(() => setReqLoading(false))
  }

  useEffect(() => { loadRequests() }, [])

  const submit = async e => {
    e.preventDefault(); setSaving(true)
    try {
      await employeeApi.createTicket({
        title:       `Leave Request: ${form.start_date} → ${form.end_date}`,
        description: form.reason,
        priority:    'medium',
        type:        'leave',
      })
      setShowM(false)
      setForm({ reason: '', start_date: '', end_date: '' })
      loadRequests()
    } catch {} finally { setSaving(false) }
  }

  // ── Absence history (from attendance data) ────────────────────────────────
  const [absences,    setAbsences]    = useState([])
  const [absLoading,  setAbsLoading]  = useState(false)
  const [startDate,   setStartDate]   = useState(monthAgo)
  const [endDate,     setEndDate]     = useState(today)

  const loadAbsences = () => {
    if (!user?.id) return
    setAbsLoading(true)
    employeeApi.getAbsences({ start_date: startDate, end_date: endDate, employee_id: user.id })
      .then(r => setAbsences(r.data?.data ?? []))
      .finally(() => setAbsLoading(false))
  }

  useEffect(() => {
    if (tab === 'Absences') loadAbsences()
  }, [tab, startDate, endDate]) // eslint-disable-line

  return (
    <>
      <div className="page-header">
        <h1>My Leaves</h1>
        <p>Submit leave requests and view your absence history.</p>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, borderBottom: '1px solid var(--c-border)', marginBottom: 20 }}>
        {TABS.map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              padding: '8px 18px', fontSize: '.875rem', fontWeight: 500,
              color: tab === t ? 'var(--c-primary)' : 'var(--c-muted)',
              borderBottom: tab === t ? '2px solid var(--c-primary)' : '2px solid transparent',
              marginBottom: -1,
            }}
          >{t}</button>
        ))}
      </div>

      {/* ── Requests tab ─────────────────────────────────────────────────── */}
      {tab === 'Requests' && (
        <div className="card">
          <div className="toolbar" style={{ marginBottom: 12 }}>
            <div className="toolbar-right">
              <button className="btn btn-primary" onClick={() => setShowM(true)}><Plus size={15}/>Request Leave</button>
            </div>
          </div>

          {reqLoading
            ? <Spinner/>
            : requests.length === 0
              ? <EmptyState title="No leave requests" desc="Submit a new request to get started."/>
              : (
              <div className="table-wrap">
                <table>
                  <thead><tr><th>Period</th><th>Reason</th><th>Status</th><th>Submitted</th></tr></thead>
                  <tbody>
                    {requests.map(r => (
                      <tr key={r.id}>
                        <td className="font-semibold">{r.title?.replace('Leave Request: ', '') ?? '—'}</td>
                        <td style={{ color: 'var(--c-muted)', fontSize: '.85rem' }}>
                          {(r.description ?? '').slice(0, 60)}{r.description?.length > 60 ? '…' : ''}
                        </td>
                        <td><StatusBadge status={r.status ?? 'open'}/></td>
                        <td style={{ color: 'var(--c-muted)', fontSize: '.8rem' }}>{r.created_at?.slice(0, 10)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
        </div>
      )}

      {/* ── Absences tab ──────────────────────────────────────────────────── */}
      {tab === 'Absences' && (
        <div className="card">
          <div className="toolbar" style={{ marginBottom: 16 }}>
            <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end' }}>
              <div className="field" style={{ marginBottom: 0 }}>
                <label style={{ fontSize: '.8rem', color: 'var(--c-muted)', display: 'block', marginBottom: 4 }}>From</label>
                <input
                  type="date" value={startDate} max={endDate}
                  onChange={e => setStartDate(e.target.value)}
                  style={{ padding: '6px 10px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--c-border)', background: 'var(--c-surface)', color: 'var(--c-text)', fontSize: '.875rem' }}
                />
              </div>
              <div className="field" style={{ marginBottom: 0 }}>
                <label style={{ fontSize: '.8rem', color: 'var(--c-muted)', display: 'block', marginBottom: 4 }}>To</label>
                <input
                  type="date" value={endDate} min={startDate} max={today()}
                  onChange={e => setEndDate(e.target.value)}
                  style={{ padding: '6px 10px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--c-border)', background: 'var(--c-surface)', color: 'var(--c-text)', fontSize: '.875rem' }}
                />
              </div>
            </div>
          </div>

          {absLoading
            ? <Spinner/>
            : absences.length === 0
              ? <EmptyState title="No absences in this period" desc="Great — you were present every day."/>
              : (
              <div className="table-wrap">
                <table>
                  <thead><tr><th>Date</th><th>Status</th></tr></thead>
                  <tbody>
                    {absences.map(a => (
                      <tr key={a.id}>
                        <td>{a.start_date}</td>
                        <td><StatusBadge status={a.status ?? 'absent'}/></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
        </div>
      )}

      {/* Leave request modal */}
      <Modal open={showM} onClose={() => setShowM(false)} title="Request Leave">
        <form onSubmit={submit}>
          <div className="field-row">
            <Input label="Start Date" type="date" value={form.start_date} onChange={e => setForm(f => ({ ...f, start_date: e.target.value }))} required/>
            <Input label="End Date"   type="date" value={form.end_date}   onChange={e => setForm(f => ({ ...f, end_date:   e.target.value }))} required/>
          </div>
          <div className="field">
            <label>Reason</label>
            <textarea
              value={form.reason}
              onChange={e => setForm(f => ({ ...f, reason: e.target.value }))}
              placeholder="Reason for leave…"
              required
            />
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={() => setShowM(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Submitting…' : 'Submit Request'}</button>
          </div>
        </form>
      </Modal>
    </>
  )
}
