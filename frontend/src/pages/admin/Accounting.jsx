import { useState, useEffect } from 'react'
import { adminApi, extractPage } from '../../lib/api'
import {
  Spinner, EmptyState, Pagination, Modal, Confirm, Input, Select, StatusBadge,
} from '../../components/ui/index'
import { Plus, Trash2 } from 'lucide-react'

// ── Budgets tab ───────────────────────────────────────────────────────────────
function BudgetsTab() {
  const [rows,     setRows]     = useState([])
  const [meta,     setMeta]     = useState(null)
  const [page,     setPage]     = useState(1)
  const [loading,  setLoading]  = useState(true)
  const [showM,    setShowM]    = useState(false)
  const [delId,    setDelId]    = useState(null)
  const [saving,   setSaving]   = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [categories, setCategories] = useState([])
  const BLANK = { title: '', type: 'Monthly', budget_amount: '', startDate: '', endDate: '', note: '', category: '' }
  const [form, setForm] = useState(BLANK)

  const load = (p = page) => {
    setLoading(true)
    adminApi.getBudgets(p)
      .then(r => { const { rows, meta } = extractPage(r); setRows(rows); setMeta(meta) })
      .finally(() => setLoading(false))
  }

  useEffect(() => { load(page) }, [page]) // eslint-disable-line
  useEffect(() => { adminApi.getBudgetCategories().then(r => setCategories(extractPage(r).rows)) }, [])

  const save = async e => {
    e.preventDefault(); setSaving(true)
    try {
      await adminApi.createBudget({ ...form, budget_amount: Number(form.budget_amount), category: form.category || undefined })
      setShowM(false); load(page)
    } catch {} finally { setSaving(false) }
  }

  const doDelete = async () => {
    setDeleting(true)
    try { await adminApi.deleteBudget(delId); setDelId(null); load(page) }
    catch {} finally { setDeleting(false) }
  }

  return (
    <>
      <div className="toolbar" style={{ marginBottom: 12 }}>
        <div className="toolbar-right">
          <button className="btn btn-primary" onClick={() => { setForm(BLANK); setShowM(true) }}><Plus size={15}/>New Budget</button>
        </div>
      </div>

      {loading ? <Spinner/> : rows.length === 0 ? <EmptyState title="No budgets yet" desc="Create your first budget to get started."/> : (
        <div className="table-wrap">
          <table>
            <thead><tr><th>Title</th><th>Category</th><th>Type</th><th>Amount</th><th>Start</th><th>End</th><th></th></tr></thead>
            <tbody>
              {rows.map(b => (
                <tr key={b.id}>
                  <td className="font-semibold">{b.title}</td>
                  <td style={{ color: 'var(--c-muted)' }}>{b.category?.name ?? '—'}</td>
                  <td><StatusBadge status={b.type}/></td>
                  <td className="font-semibold">${Number(b.amount ?? b.budget_amount ?? 0).toLocaleString()}</td>
                  <td style={{ color: 'var(--c-muted)', fontSize: '.8rem' }}>{b.startDate?.slice(0, 10) ?? '—'}</td>
                  <td style={{ color: 'var(--c-muted)', fontSize: '.8rem' }}>{b.endDate?.slice(0, 10) ?? '—'}</td>
                  <td>
                    <button className="btn-icon" onClick={() => setDelId(b.id)} style={{ color: 'var(--c-danger)' }}><Trash2 size={14}/></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <Pagination meta={meta} onPage={setPage}/>

      <Modal open={showM} onClose={() => setShowM(false)} title="New Budget">
        <form onSubmit={save}>
          <Input label="Title" value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} required/>
          <div className="field-row">
            <Select label="Type" value={form.type} onChange={e => setForm(f => ({ ...f, type: e.target.value }))}>
              <option>Monthly</option><option>Quarterly</option><option>Yearly</option>
            </Select>
            <Select label="Category" value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))}>
              <option value="">No category</option>
              {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </Select>
          </div>
          <Input label="Budget Amount ($)" type="number" value={form.budget_amount} onChange={e => setForm(f => ({ ...f, budget_amount: e.target.value }))} required/>
          <div className="field-row">
            <Input label="Start Date" type="date" value={form.startDate} onChange={e => setForm(f => ({ ...f, startDate: e.target.value }))}/>
            <Input label="End Date"   type="date" value={form.endDate}   onChange={e => setForm(f => ({ ...f, endDate:   e.target.value }))}/>
          </div>
          <div className="field">
            <label>Note</label>
            <textarea value={form.note} onChange={e => setForm(f => ({ ...f, note: e.target.value }))} placeholder="Optional note…"/>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={() => setShowM(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Creating…' : 'Create'}</button>
          </div>
        </form>
      </Modal>

      <Confirm open={!!delId} onClose={() => setDelId(null)} onConfirm={doDelete} loading={deleting}
        title="Delete Budget" message="This budget will be permanently removed."/>
    </>
  )
}

// ── Categories tab ────────────────────────────────────────────────────────────
function CategoriesTab() {
  const [rows,     setRows]     = useState([])
  const [meta,     setMeta]     = useState(null)
  const [page,     setPage]     = useState(1)
  const [loading,  setLoading]  = useState(true)
  const [showM,    setShowM]    = useState(false)
  const [delId,    setDelId]    = useState(null)
  const [saving,   setSaving]   = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [name,     setName]     = useState('')

  const load = (p = page) => {
    setLoading(true)
    adminApi.getBudgetCategories(p)
      .then(r => { const { rows, meta } = extractPage(r); setRows(rows); setMeta(meta) })
      .finally(() => setLoading(false))
  }

  useEffect(() => { load(page) }, [page]) // eslint-disable-line

  const save = async e => {
    e.preventDefault(); setSaving(true)
    try { await adminApi.createBudgetCategory({ name }); setName(''); setShowM(false); load(page) }
    catch {} finally { setSaving(false) }
  }

  const doDelete = async () => {
    setDeleting(true)
    try { await adminApi.deleteBudgetCategory(delId); setDelId(null); load(page) }
    catch {} finally { setDeleting(false) }
  }

  return (
    <>
      <div className="toolbar" style={{ marginBottom: 12 }}>
        <div className="toolbar-right">
          <button className="btn btn-primary" onClick={() => { setName(''); setShowM(true) }}><Plus size={15}/>New Category</button>
        </div>
      </div>

      {loading ? <Spinner/> : rows.length === 0 ? <EmptyState title="No categories yet"/> : (
        <div className="table-wrap">
          <table>
            <thead><tr><th>Name</th><th>Created</th><th></th></tr></thead>
            <tbody>
              {rows.map(c => (
                <tr key={c.id}>
                  <td className="font-semibold">{c.name}</td>
                  <td style={{ color: 'var(--c-muted)', fontSize: '.8rem' }}>{c.created_at?.slice(0, 10) ?? '—'}</td>
                  <td>
                    <button className="btn-icon" onClick={() => setDelId(c.id)} style={{ color: 'var(--c-danger)' }}><Trash2 size={14}/></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <Pagination meta={meta} onPage={setPage}/>

      <Modal open={showM} onClose={() => setShowM(false)} title="New Category">
        <form onSubmit={save}>
          <Input label="Category Name" value={name} onChange={e => setName(e.target.value)} required/>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={() => setShowM(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Creating…' : 'Create'}</button>
          </div>
        </form>
      </Modal>

      <Confirm open={!!delId} onClose={() => setDelId(null)} onConfirm={doDelete} loading={deleting}
        title="Delete Category" message="This category will be permanently removed."/>
    </>
  )
}

// ── Main Accounting page ──────────────────────────────────────────────────────
const TABS = ['Budgets', 'Categories']

export default function AdminAccounting() {
  const [tab, setTab] = useState('Budgets')

  return (
    <>
      <div className="page-header">
        <h1>Accounting</h1>
        <p>Manage budgets and budget categories.</p>
      </div>

      <div className="card">
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

        {tab === 'Budgets'    && <BudgetsTab/>}
        {tab === 'Categories' && <CategoriesTab/>}
      </div>
    </>
  )
}
