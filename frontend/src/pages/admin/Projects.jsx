import { useState, useEffect } from 'react'
import { adminApi } from '../../lib/api'
import { Spinner, EmptyState, SearchInput, StatusBadge, Avatar } from '../../components/ui/index'

export default function AdminProjects() {
  const [rows,    setRows]    = useState([])
  const [q,       setQ]       = useState('')
  const [filter,  setFilter]  = useState('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminApi.getProjects()
      .then(r => setRows(r.data?.data ?? []))
      .finally(() => setLoading(false))
  }, [])

  const priorities = ['all', 'high', 'medium', 'low']

  const filtered = rows
    .filter(p => filter === 'all' || (p.priority ?? '').toLowerCase() === filter)
    .filter(p => (p.name ?? '').toLowerCase().includes(q.toLowerCase()))

  return (
    <>
      <div className="page-header">
        <h1>Projects</h1>
        <p>Overview of all active and completed projects.</p>
      </div>

      <div className="card">
        <div className="toolbar">
          <SearchInput value={q} onChange={setQ} placeholder="Search projects…"/>
          <div style={{ display: 'flex', gap: 6 }}>
            {priorities.map(p => (
              <button
                key={p}
                className={`btn btn-secondary btn-sm${filter === p ? ' active' : ''}`}
                style={filter === p ? { background: 'var(--c-primary)', color: '#fff', borderColor: 'var(--c-primary)' } : {}}
                onClick={() => setFilter(p)}
              >
                {p.charAt(0).toUpperCase() + p.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {loading
          ? <Spinner/>
          : filtered.length === 0
            ? <EmptyState title="No projects found" desc="Projects will appear here once created."/>
            : (
            <div className="table-wrap">
              <table>
                <thead><tr>
                  <th>Project</th><th>Client</th><th>Leader</th><th>Priority</th><th>Start</th><th>Deadline</th><th>Team</th>
                </tr></thead>
                <tbody>
                  {filtered.map(proj => (
                    <tr key={proj.id}>
                      <td>
                        <div className="font-semibold">{proj.name}</div>
                        {proj.short_desc && (
                          <div style={{ color: 'var(--c-muted)', fontSize: '.8rem' }}>
                            {proj.short_desc.slice(0, 60)}{proj.short_desc.length > 60 ? '…' : ''}
                          </div>
                        )}
                      </td>
                      <td style={{ color: 'var(--c-muted)' }}>{proj.client ?? '—'}</td>
                      <td style={{ color: 'var(--c-muted)' }}>{proj.project_leader ?? '—'}</td>
                      <td><StatusBadge status={proj.priority ?? 'medium'}/></td>
                      <td style={{ color: 'var(--c-muted)', fontSize: '.8rem' }}>{proj.start_date ?? '—'}</td>
                      <td style={{ color: 'var(--c-muted)', fontSize: '.8rem' }}>{proj.deadline ?? proj.end_date ?? '—'}</td>
                      <td>
                        <div style={{ display: 'flex', gap: 4 }}>
                          {(proj.team ?? []).slice(0, 4).map(m => (
                            <Avatar key={m.id} name={m.name} size="sm" title={m.name}/>
                          ))}
                          {(proj.team ?? []).length > 4 && (
                            <span style={{ fontSize: '.75rem', color: 'var(--c-muted)', alignSelf: 'center' }}>
                              +{proj.team.length - 4}
                            </span>
                          )}
                        </div>
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
