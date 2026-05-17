import { useState, useEffect } from 'react'
import { adminApi } from '../../lib/api'
import { Spinner, EmptyState, StatusBadge } from '../../components/ui/index'

function today() {
  return new Date().toISOString().slice(0, 10)
}

function weekAgo() {
  const d = new Date(); d.setDate(d.getDate() - 6)
  return d.toISOString().slice(0, 10)
}

export default function AdminLeaves() {
  const [rows,     setRows]     = useState([])
  const [loading,  setLoading]  = useState(true)
  const [startDate, setStartDate] = useState(weekAgo)
  const [endDate,   setEndDate]   = useState(today)

  const load = () => {
    setLoading(true)
    adminApi.getAbsences({ start_date: startDate, end_date: endDate })
      .then(r => setRows(r.data?.data ?? []))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [startDate, endDate]) // eslint-disable-line

  return (
    <>
      <div className="page-header">
        <h1>Absences</h1>
        <p>Employees with no attendance record for the selected date range.</p>
      </div>

      <div className="card">
        {/* Date range filter */}
        <div className="toolbar" style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <div className="field" style={{ marginBottom: 0 }}>
              <label style={{ fontSize: '.8rem', color: 'var(--c-muted)', display: 'block', marginBottom: 4 }}>From</label>
              <input
                type="date"
                value={startDate}
                max={endDate}
                onChange={e => setStartDate(e.target.value)}
                style={{ padding: '6px 10px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--c-border)', background: 'var(--c-surface)', color: 'var(--c-text)', fontSize: '.875rem' }}
              />
            </div>
            <div className="field" style={{ marginBottom: 0 }}>
              <label style={{ fontSize: '.8rem', color: 'var(--c-muted)', display: 'block', marginBottom: 4 }}>To</label>
              <input
                type="date"
                value={endDate}
                min={startDate}
                max={today()}
                onChange={e => setEndDate(e.target.value)}
                style={{ padding: '6px 10px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--c-border)', background: 'var(--c-surface)', color: 'var(--c-text)', fontSize: '.875rem' }}
              />
            </div>
          </div>
          <div style={{ alignSelf: 'flex-end', color: 'var(--c-muted)', fontSize: '.8rem' }}>
            {rows.length} absence{rows.length !== 1 ? 's' : ''} found
          </div>
        </div>

        {loading
          ? <Spinner/>
          : rows.length === 0
            ? <EmptyState title="No absences found" desc="All employees had attendance records for this period."/>
            : (
            <div className="table-wrap">
              <table>
                <thead><tr>
                  <th>Employee</th><th>Department</th><th>Date</th><th>Status</th>
                </tr></thead>
                <tbody>
                  {rows.map(abs => (
                    <tr key={abs.id}>
                      <td className="font-semibold">{abs.employee_name}</td>
                      <td style={{ color: 'var(--c-muted)' }}>{abs.department ?? '—'}</td>
                      <td style={{ color: 'var(--c-muted)', fontSize: '.8rem' }}>{abs.start_date}</td>
                      <td><StatusBadge status={abs.status ?? 'absent'}/></td>
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
