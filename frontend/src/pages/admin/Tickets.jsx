import { useState, useEffect } from 'react'
import { adminApi } from '../../lib/api'
import { Spinner, EmptyState, Pagination, StatusBadge, SearchInput } from '../../components/ui/index'
import { CheckCircle } from 'lucide-react'

export default function AdminTickets() {
  const [rows,    setRows]    = useState([])
  const [meta,    setMeta]    = useState(null)
  const [page,    setPage]    = useState(1)
  const [q,       setQ]       = useState('')
  const [filter,  setFilter]  = useState('all')
  const [loading, setLoading] = useState(true)

  const load = (p = page) => {
    setLoading(true)
    adminApi.getTickets(p)
      .then(r => { setRows(r.data?.data ?? []); setMeta(r.data?.meta ?? null) })
      .finally(() => setLoading(false))
  }

  useEffect(() => { load(page) }, [page]) // eslint-disable-line

  const closeTicket = async id => {
    await adminApi.updateTicket(id, { status:'closed' })
    setRows(prev => prev.map(t => t.id === id ? { ...t, status:'closed' } : t))
  }

  const statuses = ['all','open','pending','closed','resolved']

  const filtered = rows
    .filter(t => filter === 'all' || (t.status??'').toLowerCase() === filter)
    .filter(t => `${t.title} ${t.description}`.toLowerCase().includes(q.toLowerCase()))

  return (
    <>
      <div className="page-header">
        <h1>Support Tickets</h1>
        <p>Review and manage all support requests.</p>
      </div>

      <div className="card">
        <div className="toolbar">
          <SearchInput value={q} onChange={setQ} placeholder="Search tickets…"/>
          <div style={{display:'flex',gap:6}}>
            {statuses.map(s => (
              <button
                key={s}
                className={`btn btn-secondary btn-sm ${filter===s?'active':''}`}
                style={filter===s?{background:'var(--c-primary)',color:'#fff',borderColor:'var(--c-primary)'}:{}}
                onClick={()=>setFilter(s)}
              >{s.charAt(0).toUpperCase()+s.slice(1)}</button>
            ))}
          </div>
        </div>

        {loading
          ? <Spinner/>
          : filtered.length === 0
            ? <EmptyState title="No tickets found"/>
            : (
            <div className="table-wrap">
              <table>
                <thead><tr>
                  <th>#</th><th>Title</th><th>Priority</th><th>Status</th><th>Created</th><th>Action</th>
                </tr></thead>
                <tbody>
                  {filtered.map(t => (
                    <tr key={t.id}>
                      <td style={{color:'var(--c-muted)',fontSize:'.8rem'}}>{t.id}</td>
                      <td>
                        <div className="font-semibold">{t.title}</div>
                        <div style={{color:'var(--c-muted)',fontSize:'.8rem'}}>{(t.description??'').slice(0,60)}{t.description?.length>60?'…':''}</div>
                      </td>
                      <td><StatusBadge status={t.priority ?? 'medium'}/></td>
                      <td><StatusBadge status={t.status ?? 'open'}/></td>
                      <td style={{color:'var(--c-muted)',fontSize:'.8rem'}}>{t.created_at?.slice(0,10)}</td>
                      <td>
                        {(t.status??'').toLowerCase() !== 'closed' && (
                          <button className="btn btn-secondary btn-sm" onClick={()=>closeTicket(t.id)}>
                            <CheckCircle size={13}/>Close
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        <Pagination meta={meta} onPage={setPage}/>
      </div>
    </>
  )
}
