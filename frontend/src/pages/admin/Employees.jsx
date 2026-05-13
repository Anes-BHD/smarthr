import { useState, useEffect } from 'react'
import { adminApi } from '../../lib/api'
import {
  Spinner, EmptyState, SearchInput, Pagination,
  Modal, Confirm, StatusBadge, Avatar, Input, Select,
} from '../../components/ui/index'
import { Plus, Pencil, Trash2 } from 'lucide-react'

const BLANK = { firstname:'', lastname:'', email:'', phone:'', type:'Employee', department_id:'' }

export default function AdminEmployees() {
  const [rows,    setRows]    = useState([])
  const [meta,    setMeta]    = useState(null)
  const [page,    setPage]    = useState(1)
  const [q,       setQ]       = useState('')
  const [depts,   setDepts]   = useState([])
  const [loading, setLoading] = useState(true)
  const [form,    setForm]    = useState(BLANK)
  const [editId,  setEditId]  = useState(null)
  const [showM,   setShowM]   = useState(false)
  const [delId,   setDelId]   = useState(null)
  const [saving,  setSaving]  = useState(false)
  const [deleting,setDeleting]= useState(false)

  const load = (p = page) => {
    setLoading(true)
    adminApi.getEmployees(p)
      .then(r => { setRows(r.data?.data ?? []); setMeta(r.data?.meta ?? null) })
      .finally(() => setLoading(false))
  }

  useEffect(() => { load(page) }, [page]) // eslint-disable-line
  useEffect(() => { adminApi.getDepartments().then(r => setDepts(r.data?.data ?? [])) }, [])

  const filtered = rows.filter(r =>
    `${r.firstname} ${r.lastname} ${r.email}`.toLowerCase().includes(q.toLowerCase())
  )

  const openCreate = () => { setForm(BLANK); setEditId(null); setShowM(true) }
  const openEdit   = emp => { setForm({
    firstname: emp.firstname ?? '', lastname: emp.lastname ?? '',
    email: emp.email ?? '', phone: emp.phone ?? '',
    type: emp.type ?? 'Employee', department_id: emp.department_id ?? '',
  }); setEditId(emp.id); setShowM(true) }

  const save = async e => {
    e.preventDefault(); setSaving(true)
    try {
      if (editId) await adminApi.updateEmployee(editId, form)
      else        await adminApi.createEmployee(form)
      setShowM(false); load(page)
    } catch {} finally { setSaving(false) }
  }

  const doDelete = async () => {
    setDeleting(true)
    try { await adminApi.deleteEmployee(delId); setDelId(null); load(page) }
    catch {} finally { setDeleting(false) }
  }

  return (
    <>
      <div className="page-header">
        <h1>Employees</h1>
        <p>Manage all employees in your organisation.</p>
      </div>

      <div className="card">
        <div className="toolbar">
          <SearchInput value={q} onChange={setQ} placeholder="Search employees…"/>
          <div className="toolbar-right">
            <button className="btn btn-primary" onClick={openCreate}><Plus size={15}/>Add Employee</button>
          </div>
        </div>

        {loading
          ? <Spinner/>
          : filtered.length === 0
            ? <EmptyState title="No employees found" desc="Create your first employee to get started."/>
            : (
            <div className="table-wrap">
              <table>
                <thead><tr>
                  <th>Employee</th><th>Email</th><th>Phone</th><th>Type</th><th>Actions</th>
                </tr></thead>
                <tbody>
                  {filtered.map(emp => (
                    <tr key={emp.id}>
                      <td>
                        <div style={{display:'flex',alignItems:'center',gap:10}}>
                          <Avatar name={`${emp.firstname} ${emp.lastname}`} size="sm"/>
                          <span className="font-semibold">{emp.firstname} {emp.lastname}</span>
                        </div>
                      </td>
                      <td style={{color:'var(--c-muted)'}}>{emp.email}</td>
                      <td style={{color:'var(--c-muted)'}}>{emp.phone ?? '—'}</td>
                      <td><StatusBadge status={emp.type ?? 'Employee'}/></td>
                      <td>
                        <div style={{display:'flex',gap:6}}>
                          <button className="btn-icon" onClick={()=>openEdit(emp)} title="Edit"><Pencil size={14}/></button>
                          <button className="btn-icon" onClick={()=>setDelId(emp.id)} title="Delete" style={{color:'var(--c-danger)'}}><Trash2 size={14}/></button>
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

      {/* Create / Edit Modal */}
      <Modal open={showM} onClose={()=>setShowM(false)} title={editId ? 'Edit Employee' : 'New Employee'}>
        <form onSubmit={save}>
          <div className="field-row">
            <Input label="First Name" value={form.firstname} onChange={e=>setForm(f=>({...f,firstname:e.target.value}))} required/>
            <Input label="Last Name"  value={form.lastname}  onChange={e=>setForm(f=>({...f,lastname:e.target.value}))}  required/>
          </div>
          <Input label="Email" type="email" value={form.email} onChange={e=>setForm(f=>({...f,email:e.target.value}))} required/>
          <Input label="Phone" type="tel"   value={form.phone} onChange={e=>setForm(f=>({...f,phone:e.target.value}))}/>
          <Select label="Type" value={form.type} onChange={e=>setForm(f=>({...f,type:e.target.value}))}>
            <option>Employee</option><option>Manager</option><option>HR</option>
          </Select>
          {depts.length > 0 && (
            <Select label="Department" value={form.department_id} onChange={e=>setForm(f=>({...f,department_id:e.target.value}))}>
              <option value="">Select department</option>
              {depts.map(d=><option key={d.id} value={d.id}>{d.name}</option>)}
            </Select>
          )}
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={()=>setShowM(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving?'Saving…':'Save'}</button>
          </div>
        </form>
      </Modal>

      <Confirm
        open={!!delId} onClose={()=>setDelId(null)} onConfirm={doDelete} loading={deleting}
        title="Delete Employee" message="This will permanently remove the employee record."
      />
    </>
  )
}
