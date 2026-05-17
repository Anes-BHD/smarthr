import { useState, useEffect } from 'react'
import { adminApi } from '../../lib/api'
import {
  Spinner, EmptyState, SearchInput, Pagination,
  Modal, Confirm, StatusBadge, Avatar, Input,
} from '../../components/ui/index'
import { Plus, Pencil, Trash2 } from 'lucide-react'

const BLANK = { firstname: '', lastname: '', email: '', phone: '', company_name: '' }

export default function AdminClients() {
  const [rows,     setRows]     = useState([])
  const [meta,     setMeta]     = useState(null)
  const [page,     setPage]     = useState(1)
  const [q,        setQ]        = useState('')
  const [loading,  setLoading]  = useState(true)
  const [form,     setForm]     = useState(BLANK)
  const [editId,   setEditId]   = useState(null)
  const [showM,    setShowM]    = useState(false)
  const [delId,    setDelId]    = useState(null)
  const [saving,   setSaving]   = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [error,    setError]    = useState('')

  const load = (p = page) => {
    setLoading(true)
    adminApi.getClients(p)
      .then(r => { setRows(r.data?.data ?? []); setMeta(r.data?.meta ?? null) })
      .finally(() => setLoading(false))
  }

  useEffect(() => { load(page) }, [page]) // eslint-disable-line

  const filtered = rows.filter(r =>
    `${r.firstname} ${r.lastname} ${r.email} ${r.company_name ?? ''}`.toLowerCase().includes(q.toLowerCase())
  )

  const openCreate = () => { setForm(BLANK); setEditId(null); setError(''); setShowM(true) }
  const openEdit   = c  => {
    setForm({
      firstname:    c.firstname    ?? '',
      lastname:     c.lastname     ?? '',
      email:        c.email        ?? '',
      phone:        c.phone        ?? '',
      company_name: c.company_name ?? '',
    })
    setEditId(c.id); setError(''); setShowM(true)
  }

  const save = async e => {
    e.preventDefault(); setSaving(true); setError('')
    try {
      if (editId) await adminApi.updateClient(editId, form)
      else        await adminApi.createClient(form)
      setShowM(false); load(page)
    } catch (err) {
      setError(err.response?.data?.message ?? 'Failed to save client.')
    } finally { setSaving(false) }
  }

  const doDelete = async () => {
    setDeleting(true)
    try { await adminApi.deleteClient(delId); setDelId(null); load(page) }
    catch {} finally { setDeleting(false) }
  }

  return (
    <>
      <div className="page-header">
        <h1>Clients</h1>
        <p>Manage your clients and their profiles.</p>
      </div>

      <div className="card">
        <div className="toolbar">
          <SearchInput value={q} onChange={setQ} placeholder="Search clients…"/>
          <div className="toolbar-right">
            <button className="btn btn-primary" onClick={openCreate}><Plus size={15}/>Add Client</button>
          </div>
        </div>

        {loading
          ? <Spinner/>
          : filtered.length === 0
            ? <EmptyState title="No clients found" desc="Add your first client to get started."/>
            : (
            <div className="table-wrap">
              <table>
                <thead><tr>
                  <th>Client</th><th>Email</th><th>Phone</th><th>Company</th><th>Actions</th>
                </tr></thead>
                <tbody>
                  {filtered.map(c => (
                    <tr key={c.id}>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <Avatar name={`${c.firstname} ${c.lastname}`} size="sm"/>
                          <span className="font-semibold">{c.firstname} {c.lastname}</span>
                        </div>
                      </td>
                      <td style={{ color: 'var(--c-muted)' }}>{c.email}</td>
                      <td style={{ color: 'var(--c-muted)' }}>{c.phone ?? '—'}</td>
                      <td style={{ color: 'var(--c-muted)' }}>{c.company_name ?? '—'}</td>
                      <td>
                        <div style={{ display: 'flex', gap: 6 }}>
                          <button className="btn-icon" onClick={() => openEdit(c)} title="Edit"><Pencil size={14}/></button>
                          <button className="btn-icon" onClick={() => setDelId(c.id)} title="Delete" style={{ color: 'var(--c-danger)' }}><Trash2 size={14}/></button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        <Pagination meta={meta} onPage={setPage}/>
      </div>

      <Modal open={showM} onClose={() => setShowM(false)} title={editId ? 'Edit Client' : 'New Client'}>
        <form onSubmit={save}>
          {error && (
            <div style={{ background: 'rgba(239,68,68,.1)', border: '1px solid rgba(239,68,68,.25)', borderRadius: 'var(--radius-sm)', padding: '10px 14px', marginBottom: 14, fontSize: '.875rem', color: 'var(--c-danger)' }}>
              {error}
            </div>
          )}
          <div className="field-row">
            <Input label="First Name" value={form.firstname} onChange={e => setForm(f => ({ ...f, firstname: e.target.value }))} required/>
            <Input label="Last Name"  value={form.lastname}  onChange={e => setForm(f => ({ ...f, lastname:  e.target.value }))} required/>
          </div>
          <Input label="Email"        type="email" value={form.email}        onChange={e => setForm(f => ({ ...f, email:        e.target.value }))} required/>
          <Input label="Phone"        type="tel"   value={form.phone}        onChange={e => setForm(f => ({ ...f, phone:        e.target.value }))}/>
          <Input label="Company Name"              value={form.company_name} onChange={e => setForm(f => ({ ...f, company_name: e.target.value }))}/>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={() => setShowM(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Saving…' : 'Save'}</button>
          </div>
        </form>
      </Modal>

      <Confirm
        open={!!delId} onClose={() => setDelId(null)} onConfirm={doDelete} loading={deleting}
        title="Delete Client" message="This will permanently remove the client record."
      />
    </>
  )
}
