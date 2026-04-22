import { useState, useEffect } from 'react'
import { adminApi } from '../../lib/api'
import { Spinner, EmptyState, Pagination, Modal, Confirm, Input, Select } from '../../components/ui/index'
import { Plus, Trash2 } from 'lucide-react'

const BLANK = { name:'', email:'', password:'', type:'employee' }

export default function AdminUsers() {
  const [rows,    setRows]    = useState([])
  const [meta,    setMeta]    = useState(null)
  const [page,    setPage]    = useState(1)
  const [loading, setLoading] = useState(true)
  const [showM,   setShowM]   = useState(false)
  const [form,    setForm]    = useState(BLANK)
  const [saving,  setSaving]  = useState(false)
  const [delId,   setDelId]   = useState(null)
  const [deleting,setDeleting]= useState(false)
  const [error,   setError]   = useState('')

  const load = (p = page) => {
    setLoading(true)
    adminApi.getUsers(p)
      .then(r => { setRows(r.data?.data ?? []); setMeta(r.data?.meta ?? null) })
      .finally(() => setLoading(false))
  }

  useEffect(() => { load(page) }, [page]) // eslint-disable-line

  const save = async e => {
    e.preventDefault(); setSaving(true); setError('')
    try { await adminApi.createUser(form); setShowM(false); load(page) }
    catch (err) { setError(err.response?.data?.message ?? 'Error creating user.') }
    finally { setSaving(false) }
  }

  const doDelete = async () => {
    setDeleting(true)
    try { await adminApi.deleteUser(delId); setDelId(null); load(page) }
    catch {} finally { setDeleting(false) }
  }

  return (
    <>
      <div className="page-header">
        <h1>Users</h1>
        <p>Create system users and assign roles.</p>
      </div>

      <div className="card">
        <div className="toolbar">
          <div className="toolbar-right">
            <button className="btn btn-primary" onClick={()=>{setForm(BLANK);setError('');setShowM(true)}}>
              <Plus size={15}/>Create User
            </button>
          </div>
        </div>

        {loading
          ? <Spinner/>
          : rows.length === 0
            ? <EmptyState title="No users found" desc="Create the first system user."/>
            : (
            <div className="table-wrap">
              <table>
                <thead><tr>
                  <th>Name</th><th>Email</th><th>Role / Type</th><th>Created</th><th>Actions</th>
                </tr></thead>
                <tbody>
                  {rows.map(u => (
                    <tr key={u.id}>
                      <td className="font-semibold">{u.name ?? u.firstname}</td>
                      <td style={{color:'var(--c-muted)'}}>{u.email}</td>
                      <td style={{textTransform:'capitalize'}}>{u.type ?? u.roles?.[0] ?? '—'}</td>
                      <td style={{color:'var(--c-muted)',fontSize:'.8rem'}}>{u.created_at?.slice(0,10)}</td>
                      <td>
                        <button className="btn-icon" onClick={()=>setDelId(u.id)} title="Delete" style={{color:'var(--c-danger)'}}>
                          <Trash2 size={14}/>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        <Pagination meta={meta} onPage={setPage}/>
      </div>

      <Modal open={showM} onClose={()=>setShowM(false)} title="Create User">
        <form onSubmit={save}>
          {error && (
            <div style={{background:'rgba(239,68,68,.1)',border:'1px solid rgba(239,68,68,.25)',borderRadius:'var(--radius-sm)',padding:'10px 14px',marginBottom:14,fontSize:'.875rem',color:'var(--c-danger)'}}>
              {error}
            </div>
          )}
          <Input label="Name"     value={form.name}     onChange={e=>setForm(f=>({...f,name:e.target.value}))}     required/>
          <Input label="Email"    type="email" value={form.email}    onChange={e=>setForm(f=>({...f,email:e.target.value}))}    required/>
          <Input label="Password" type="password" value={form.password} onChange={e=>setForm(f=>({...f,password:e.target.value}))} required/>
          <Select label="Role" value={form.type} onChange={e=>setForm(f=>({...f,type:e.target.value}))}>
            <option value="employee">Employee</option>
            <option value="admin">Admin</option>
            <option value="superadmin">Super Admin</option>
            <option value="client">Client</option>
          </Select>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={()=>setShowM(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving?'Creating…':'Create User'}</button>
          </div>
        </form>
      </Modal>

      <Confirm open={!!delId} onClose={()=>setDelId(null)} onConfirm={doDelete} loading={deleting}
        title="Delete User" message="This user will be permanently deleted."/>
    </>
  )
}
