import { useState, useEffect } from 'react'
import { adminApi, extractPage } from '../../lib/api'
import {
  Spinner, EmptyState, Pagination, Modal, Confirm, Input, Select, StatusBadge,
} from '../../components/ui/index'
import { Plus, Trash2 } from 'lucide-react'

// ── Invoices tab ─────────────────────────────────────────────────────────────
function InvoicesTab() {
  const [rows,     setRows]     = useState([])
  const [meta,     setMeta]     = useState(null)
  const [page,     setPage]     = useState(1)
  const [loading,  setLoading]  = useState(true)
  const [showM,    setShowM]    = useState(false)
  const [delId,    setDelId]    = useState(null)
  const [saving,   setSaving]   = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [clients,  setClients]  = useState([])
  const [form,     setForm]     = useState({
    client: '', billing_address: '', startDate: '', expiryDate: '',
    items: [{ name: '', cost: '', qty: 1 }],
  })

  const load = (p = page) => {
    setLoading(true)
    adminApi.getInvoices(p)
      .then(r => { const { rows, meta } = extractPage(r); setRows(rows); setMeta(meta) })
      .finally(() => setLoading(false))
  }

  useEffect(() => { load(page) }, [page]) // eslint-disable-line
  useEffect(() => { adminApi.getClients().then(r => setClients(extractPage(r).rows)) }, [])

  const setItem = (i, k, v) => setForm(f => {
    const items = [...f.items]; items[i] = { ...items[i], [k]: v }; return { ...f, items }
  })
  const addItem    = ()  => setForm(f => ({ ...f, items: [...f.items, { name: '', cost: '', qty: 1 }] }))
  const removeItem = (i) => setForm(f => ({ ...f, items: f.items.filter((_, idx) => idx !== i) }))

  const save = async e => {
    e.preventDefault(); setSaving(true)
    try {
      await adminApi.createInvoice({
        ...form,
        client: Number(form.client),
        items: form.items.map(it => ({ ...it, cost: Number(it.cost), qty: Number(it.qty) })),
      })
      setShowM(false); load(page)
    } catch {} finally { setSaving(false) }
  }

  const doDelete = async () => {
    setDeleting(true)
    try { await adminApi.deleteInvoice(delId); setDelId(null); load(page) }
    catch {} finally { setDeleting(false) }
  }

  return (
    <>
      <div className="toolbar" style={{ marginBottom: 12 }}>
        <div className="toolbar-right">
          <button className="btn btn-primary" onClick={() => setShowM(true)}><Plus size={15}/>New Invoice</button>
        </div>
      </div>

      {loading ? <Spinner/> : rows.length === 0 ? <EmptyState title="No invoices yet"/> : (
        <div className="table-wrap">
          <table>
            <thead><tr><th>ID</th><th>Client</th><th>Start</th><th>Expiry</th><th>Total</th><th>Status</th><th></th></tr></thead>
            <tbody>
              {rows.map(inv => (
                <tr key={inv.id}>
                  <td style={{ color: 'var(--c-muted)', fontSize: '.8rem' }}>{inv.inv_id ?? `#${inv.id}`}</td>
                  <td>{inv.client?.firstname ?? inv.client?.name ?? inv.client_id ?? '—'}</td>
                  <td style={{ color: 'var(--c-muted)', fontSize: '.8rem' }}>{inv.startDate?.slice(0, 10) ?? '—'}</td>
                  <td style={{ color: 'var(--c-muted)', fontSize: '.8rem' }}>{inv.expiryDate?.slice(0, 10) ?? '—'}</td>
                  <td className="font-semibold">${Number(inv.grand_total ?? 0).toLocaleString()}</td>
                  <td><StatusBadge status={inv.status ?? 'draft'}/></td>
                  <td>
                    <button className="btn-icon" onClick={() => setDelId(inv.id)} style={{ color: 'var(--c-danger)' }}><Trash2 size={14}/></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <Pagination meta={meta} onPage={setPage}/>

      <Modal open={showM} onClose={() => setShowM(false)} title="New Invoice">
        <form onSubmit={save}>
          <Select label="Client" value={form.client} onChange={e => setForm(f => ({ ...f, client: e.target.value }))} required>
            <option value="">Select client</option>
            {clients.map(c => <option key={c.id} value={c.id}>{c.firstname} {c.lastname}</option>)}
          </Select>
          <Input label="Billing Address" value={form.billing_address} onChange={e => setForm(f => ({ ...f, billing_address: e.target.value }))} required/>
          <div className="field-row">
            <Input label="Start Date"  type="date" value={form.startDate}  onChange={e => setForm(f => ({ ...f, startDate:  e.target.value }))} required/>
            <Input label="Expiry Date" type="date" value={form.expiryDate} onChange={e => setForm(f => ({ ...f, expiryDate: e.target.value }))} required/>
          </div>
          <div style={{ marginBottom: 10 }}>
            <label style={{ fontSize: '.875rem', fontWeight: 500, color: 'var(--c-text)', display: 'block', marginBottom: 6 }}>Items</label>
            {form.items.map((it, i) => (
              <div key={i} className="field-row" style={{ alignItems: 'flex-end', marginBottom: 6 }}>
                <Input label="" placeholder="Item name" value={it.name} onChange={e => setItem(i, 'name', e.target.value)} required/>
                <Input label="" placeholder="Cost" type="number" value={it.cost} onChange={e => setItem(i, 'cost', e.target.value)} required style={{ maxWidth: 90 }}/>
                <Input label="" placeholder="Qty"  type="number" value={it.qty}  onChange={e => setItem(i, 'qty',  e.target.value)} required style={{ maxWidth: 70 }}/>
                {form.items.length > 1 && (
                  <button type="button" className="btn-icon" onClick={() => removeItem(i)} style={{ color: 'var(--c-danger)', marginBottom: 2 }}><Trash2 size={14}/></button>
                )}
              </div>
            ))}
            <button type="button" className="btn btn-secondary btn-sm" onClick={addItem}><Plus size={13}/>Add item</button>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={() => setShowM(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Creating…' : 'Create'}</button>
          </div>
        </form>
      </Modal>

      <Confirm open={!!delId} onClose={() => setDelId(null)} onConfirm={doDelete} loading={deleting}
        title="Delete Invoice" message="This invoice will be permanently removed."/>
    </>
  )
}

// ── Estimates tab ─────────────────────────────────────────────────────────────
function EstimatesTab() {
  const [rows,     setRows]     = useState([])
  const [meta,     setMeta]     = useState(null)
  const [page,     setPage]     = useState(1)
  const [loading,  setLoading]  = useState(true)
  const [showM,    setShowM]    = useState(false)
  const [delId,    setDelId]    = useState(null)
  const [saving,   setSaving]   = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [clients,  setClients]  = useState([])
  const BLANK = { client: '', billing_address: '', startDate: '', expiryDate: '' }
  const [form, setForm] = useState(BLANK)

  const load = (p = page) => {
    setLoading(true)
    adminApi.getEstimates(p)
      .then(r => { const { rows, meta } = extractPage(r); setRows(rows); setMeta(meta) })
      .finally(() => setLoading(false))
  }

  useEffect(() => { load(page) }, [page]) // eslint-disable-line
  useEffect(() => { adminApi.getClients().then(r => setClients(extractPage(r).rows)) }, [])

  const save = async e => {
    e.preventDefault(); setSaving(true)
    try { await adminApi.createEstimate({ ...form, client: Number(form.client) }); setShowM(false); load(page) }
    catch {} finally { setSaving(false) }
  }

  const doDelete = async () => {
    setDeleting(true)
    try { await adminApi.deleteEstimate(delId); setDelId(null); load(page) }
    catch {} finally { setDeleting(false) }
  }

  return (
    <>
      <div className="toolbar" style={{ marginBottom: 12 }}>
        <div className="toolbar-right">
          <button className="btn btn-primary" onClick={() => { setForm(BLANK); setShowM(true) }}><Plus size={15}/>New Estimate</button>
        </div>
      </div>

      {loading ? <Spinner/> : rows.length === 0 ? <EmptyState title="No estimates yet"/> : (
        <div className="table-wrap">
          <table>
            <thead><tr><th>ID</th><th>Client</th><th>Start</th><th>Expiry</th><th>Status</th><th></th></tr></thead>
            <tbody>
              {rows.map(est => (
                <tr key={est.id}>
                  <td style={{ color: 'var(--c-muted)', fontSize: '.8rem' }}>#EST-{est.id}</td>
                  <td>{est.client?.firstname ?? est.client_id ?? '—'}</td>
                  <td style={{ color: 'var(--c-muted)', fontSize: '.8rem' }}>{est.startDate?.slice(0, 10) ?? '—'}</td>
                  <td style={{ color: 'var(--c-muted)', fontSize: '.8rem' }}>{est.expiryDate?.slice(0, 10) ?? '—'}</td>
                  <td><StatusBadge status={est.status ?? 'draft'}/></td>
                  <td>
                    <button className="btn-icon" onClick={() => setDelId(est.id)} style={{ color: 'var(--c-danger)' }}><Trash2 size={14}/></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <Pagination meta={meta} onPage={setPage}/>

      <Modal open={showM} onClose={() => setShowM(false)} title="New Estimate">
        <form onSubmit={save}>
          <Select label="Client" value={form.client} onChange={e => setForm(f => ({ ...f, client: e.target.value }))} required>
            <option value="">Select client</option>
            {clients.map(c => <option key={c.id} value={c.id}>{c.firstname} {c.lastname}</option>)}
          </Select>
          <Input label="Billing Address" value={form.billing_address} onChange={e => setForm(f => ({ ...f, billing_address: e.target.value }))} required/>
          <div className="field-row">
            <Input label="Start Date"  type="date" value={form.startDate}  onChange={e => setForm(f => ({ ...f, startDate:  e.target.value }))} required/>
            <Input label="Expiry Date" type="date" value={form.expiryDate} onChange={e => setForm(f => ({ ...f, expiryDate: e.target.value }))} required/>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={() => setShowM(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Creating…' : 'Create'}</button>
          </div>
        </form>
      </Modal>

      <Confirm open={!!delId} onClose={() => setDelId(null)} onConfirm={doDelete} loading={deleting}
        title="Delete Estimate" message="This estimate will be permanently removed."/>
    </>
  )
}

// ── Expenses tab ──────────────────────────────────────────────────────────────
function ExpensesTab() {
  const [rows,     setRows]     = useState([])
  const [meta,     setMeta]     = useState(null)
  const [page,     setPage]     = useState(1)
  const [loading,  setLoading]  = useState(true)
  const [showM,    setShowM]    = useState(false)
  const [delId,    setDelId]    = useState(null)
  const [saving,   setSaving]   = useState(false)
  const [deleting, setDeleting] = useState(false)
  const BLANK = { item_name: '', purchase_from: '', amount: '', status: 1, paid_by: '' }
  const [form, setForm] = useState(BLANK)
  const [employees, setEmployees] = useState([])

  const load = (p = page) => {
    setLoading(true)
    adminApi.getExpenses(p)
      .then(r => { const { rows, meta } = extractPage(r); setRows(rows); setMeta(meta) })
      .finally(() => setLoading(false))
  }

  useEffect(() => { load(page) }, [page]) // eslint-disable-line
  useEffect(() => { adminApi.getEmployees().then(r => setEmployees(extractPage(r).rows)) }, [])

  const save = async e => {
    e.preventDefault(); setSaving(true)
    try {
      await adminApi.createExpense({ ...form, amount: Number(form.amount), paid_by: Number(form.paid_by) })
      setShowM(false); load(page)
    } catch {} finally { setSaving(false) }
  }

  const doDelete = async () => {
    setDeleting(true)
    try { await adminApi.deleteExpense(delId); setDelId(null); load(page) }
    catch {} finally { setDeleting(false) }
  }

  return (
    <>
      <div className="toolbar" style={{ marginBottom: 12 }}>
        <div className="toolbar-right">
          <button className="btn btn-primary" onClick={() => { setForm(BLANK); setShowM(true) }}><Plus size={15}/>Add Expense</button>
        </div>
      </div>

      {loading ? <Spinner/> : rows.length === 0 ? <EmptyState title="No expenses yet"/> : (
        <div className="table-wrap">
          <table>
            <thead><tr><th>Item</th><th>Purchased From</th><th>Date</th><th>Amount</th><th></th></tr></thead>
            <tbody>
              {rows.map(exp => (
                <tr key={exp.id}>
                  <td className="font-semibold">{exp.item_name}</td>
                  <td style={{ color: 'var(--c-muted)' }}>{exp.purchased_from ?? '—'}</td>
                  <td style={{ color: 'var(--c-muted)', fontSize: '.8rem' }}>{exp.purchase_date?.slice(0, 10) ?? exp.created_at?.slice(0, 10) ?? '—'}</td>
                  <td className="font-semibold">${Number(exp.amount ?? 0).toLocaleString()}</td>
                  <td>
                    <button className="btn-icon" onClick={() => setDelId(exp.id)} style={{ color: 'var(--c-danger)' }}><Trash2 size={14}/></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <Pagination meta={meta} onPage={setPage}/>

      <Modal open={showM} onClose={() => setShowM(false)} title="Add Expense">
        <form onSubmit={save}>
          <Input label="Item Name"      value={form.item_name}     onChange={e => setForm(f => ({ ...f, item_name:     e.target.value }))} required/>
          <Input label="Purchased From" value={form.purchase_from} onChange={e => setForm(f => ({ ...f, purchase_from: e.target.value }))} required/>
          <Input label="Amount ($)"     type="number" value={form.amount} onChange={e => setForm(f => ({ ...f, amount: e.target.value }))} required/>
          <Select label="Paid By" value={form.paid_by} onChange={e => setForm(f => ({ ...f, paid_by: e.target.value }))} required>
            <option value="">Select employee</option>
            {employees.map(emp => <option key={emp.id} value={emp.id}>{emp.firstname} {emp.lastname}</option>)}
          </Select>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={() => setShowM(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Saving…' : 'Save'}</button>
          </div>
        </form>
      </Modal>

      <Confirm open={!!delId} onClose={() => setDelId(null)} onConfirm={doDelete} loading={deleting}
        title="Delete Expense" message="This expense will be permanently removed."/>
    </>
  )
}

// ── Taxes tab ─────────────────────────────────────────────────────────────────
function TaxesTab() {
  const [rows,     setRows]     = useState([])
  const [loading,  setLoading]  = useState(true)
  const [showM,    setShowM]    = useState(false)
  const [delId,    setDelId]    = useState(null)
  const [saving,   setSaving]   = useState(false)
  const [deleting, setDeleting] = useState(false)
  const BLANK = { name: '', percentage: '', status: true }
  const [form, setForm] = useState(BLANK)

  const load = () => {
    setLoading(true)
    adminApi.getTaxes()
      .then(r => setRows(extractPage(r).rows))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, []) // eslint-disable-line

  const save = async e => {
    e.preventDefault(); setSaving(true)
    try {
      await adminApi.createTax({ ...form, percentage: Number(form.percentage) })
      setShowM(false); load()
    } catch {} finally { setSaving(false) }
  }

  const doDelete = async () => {
    setDeleting(true)
    try { await adminApi.deleteTax(delId); setDelId(null); load() }
    catch {} finally { setDeleting(false) }
  }

  return (
    <>
      <div className="toolbar" style={{ marginBottom: 12 }}>
        <div className="toolbar-right">
          <button className="btn btn-primary" onClick={() => { setForm(BLANK); setShowM(true) }}><Plus size={15}/>Add Tax</button>
        </div>
      </div>

      {loading ? <Spinner/> : rows.length === 0 ? <EmptyState title="No taxes configured"/> : (
        <div className="table-wrap">
          <table>
            <thead><tr><th>Name</th><th>Rate</th><th>Status</th><th></th></tr></thead>
            <tbody>
              {rows.map(tax => (
                <tr key={tax.id}>
                  <td className="font-semibold">{tax.name}</td>
                  <td>{tax.percentage}%</td>
                  <td><StatusBadge status={tax.status ? 'active' : 'inactive'}/></td>
                  <td>
                    <button className="btn-icon" onClick={() => setDelId(tax.id)} style={{ color: 'var(--c-danger)' }}><Trash2 size={14}/></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={showM} onClose={() => setShowM(false)} title="Add Tax">
        <form onSubmit={save}>
          <Input label="Tax Name"      value={form.name}       onChange={e => setForm(f => ({ ...f, name:       e.target.value }))} required/>
          <Input label="Rate (%)" type="number" value={form.percentage} onChange={e => setForm(f => ({ ...f, percentage: e.target.value }))} required/>
          <Select label="Status" value={form.status ? 'active' : 'inactive'} onChange={e => setForm(f => ({ ...f, status: e.target.value === 'active' }))}>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </Select>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={() => setShowM(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Saving…' : 'Save'}</button>
          </div>
        </form>
      </Modal>

      <Confirm open={!!delId} onClose={() => setDelId(null)} onConfirm={doDelete} loading={deleting}
        title="Delete Tax" message="This tax will be permanently removed."/>
    </>
  )
}

// ── Main Sales page ───────────────────────────────────────────────────────────
const TABS = ['Invoices', 'Estimates', 'Expenses', 'Taxes']

export default function AdminSales() {
  const [tab, setTab] = useState('Invoices')

  return (
    <>
      <div className="page-header">
        <h1>Sales</h1>
        <p>Manage estimates, invoices, expenses, and taxes.</p>
      </div>

      <div className="card">
        <div style={{ display: 'flex', gap: 4, borderBottom: '1px solid var(--c-border)', marginBottom: 20, paddingBottom: 0 }}>
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

        {tab === 'Invoices'  && <InvoicesTab/>}
        {tab === 'Estimates' && <EstimatesTab/>}
        {tab === 'Expenses'  && <ExpensesTab/>}
        {tab === 'Taxes'     && <TaxesTab/>}
      </div>
    </>
  )
}
