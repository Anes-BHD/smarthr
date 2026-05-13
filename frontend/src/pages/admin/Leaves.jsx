import { useState, useEffect } from 'react'
import { adminApi } from '../../lib/api'
import { Spinner, EmptyState, StatusBadge, Modal, Confirm } from '../../components/ui/index'
import { CheckCircle, XCircle } from 'lucide-react'

export default function AdminLeaves() {
  const [employees, setEmployees] = useState([])
  const [loading,   setLoading]   = useState(true)
  const [action,    setAction]    = useState(null) // {emp, type:'approve'|'reject'}
  const [reason,    setReason]    = useState('')
  const [saving,    setSaving]    = useState(false)

  useEffect(() => {
    adminApi.getEmployees()
      .then(r => setEmployees(r.data?.data ?? []))
      .finally(() => setLoading(false))
  }, [])

  // Filter employees who have leave requests (status field)
  const leaveRows = employees.map(e => ({
    ...e,
    leave_status: e.leave_status ?? e.status ?? 'pending',
    leave_reason: e.leave_reason ?? e.reason ?? '',
  }))

  const handleAction = async () => {
    setSaving(true)
    try {
      await adminApi.updateEmployee(action.emp.id, {
        leave_status: action.type === 'approve' ? 'approved' : 'rejected',
        leave_reason: reason,
      })
      setEmployees(prev => prev.map(e =>
        e.id === action.emp.id
          ? { ...e, leave_status: action.type === 'approve' ? 'approved' : 'rejected' }
          : e
      ))
      setAction(null); setReason('')
    } catch {} finally { setSaving(false) }
  }

  return (
    <>
      <div className="page-header">
        <h1>Leave Requests</h1>
        <p>Approve or reject employee leave requests.</p>
      </div>

      <div className="card">
        {loading
          ? <Spinner/>
          : leaveRows.length === 0
            ? <EmptyState title="No leave requests"/>
            : (
            <div className="table-wrap">
              <table>
                <thead><tr>
                  <th>Employee</th><th>Email</th><th>Status</th><th>Reason</th><th>Actions</th>
                </tr></thead>
                <tbody>
                  {leaveRows.map(emp => (
                    <tr key={emp.id}>
                      <td className="font-semibold">{emp.firstname} {emp.lastname}</td>
                      <td style={{color:'var(--c-muted)'}}>{emp.email}</td>
                      <td><StatusBadge status={emp.leave_status}/></td>
                      <td style={{color:'var(--c-muted)',fontSize:'.85rem'}}>{emp.leave_reason || '—'}</td>
                      <td>
                        <div style={{display:'flex',gap:6}}>
                          <button className="btn btn-success btn-sm" onClick={()=>setAction({emp,type:'approve'})}>
                            <CheckCircle size={13}/> Approve
                          </button>
                          <button className="btn btn-danger btn-sm" onClick={()=>setAction({emp,type:'reject'})}>
                            <XCircle size={13}/> Reject
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
      </div>

      {/* Reason Modal */}
      <Modal
        open={!!action} onClose={()=>setAction(null)}
        title={action?.type === 'approve' ? 'Approve Leave' : 'Reject Leave'}
      >
        <p style={{color:'var(--c-muted)',marginBottom:14,fontSize:'.875rem'}}>
          {action?.type === 'approve'
            ? `Approving leave for ${action?.emp?.firstname} ${action?.emp?.lastname}`
            : `Rejecting leave for ${action?.emp?.firstname} ${action?.emp?.lastname}`}
        </p>
        <div className="field">
          <label>Reason / Note (optional)</label>
          <textarea value={reason} onChange={e=>setReason(e.target.value)} placeholder="Add a note…"/>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={()=>setAction(null)}>Cancel</button>
          <button
            className={`btn ${action?.type==='approve'?'btn-success':'btn-danger'}`}
            onClick={handleAction} disabled={saving}
          >{saving ? 'Saving…' : action?.type === 'approve' ? 'Approve' : 'Reject'}</button>
        </div>
      </Modal>
    </>
  )
}
