import { useState, useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'
import { employeeApi } from '../../lib/api'
import { Spinner, Avatar, Input, Modal } from '../../components/ui/index'
import { Pencil, KeyRound } from 'lucide-react'

export default function EmployeeProfile() {
  const { user } = useAuth()
  const [profile,  setProfile]  = useState(null)
  const [loading,  setLoading]  = useState(true)
  const [editing,  setEditing]  = useState(false)
  const [form,     setForm]     = useState({})
  const [saving,   setSaving]   = useState(false)
  const [showPw,   setShowPw]   = useState(false)
  const [pwForm,   setPwForm]   = useState({ current_password:'', password:'', password_confirmation:'' })
  const [pwSaving, setPwSaving] = useState(false)
  const [pwError,  setPwError]  = useState('')

  useEffect(() => {
    if (!user?.id) { setLoading(false); return }
    employeeApi.getProfile(user.id)
      .then(r => { setProfile(r.data?.data ?? r.data); setForm(r.data?.data ?? r.data ?? {}) })
      .finally(() => setLoading(false))
  }, [user?.id])

  const save = async e => {
    e.preventDefault(); setSaving(true)
    try {
      const r = await employeeApi.updateProfile(user.id, form)
      setProfile(r.data?.data ?? r.data); setEditing(false)
    } catch {} finally { setSaving(false) }
  }

  const savePw = async e => {
    e.preventDefault(); setPwSaving(true); setPwError('')
    try {
      await employeeApi.updateProfile(user.id, pwForm)
      setShowPw(false); setPwForm({ current_password:'', password:'', password_confirmation:'' })
    } catch (err) { setPwError(err.response?.data?.message ?? 'Password change failed.') }
    finally { setPwSaving(false) }
  }

  if (loading) return <Spinner/>

  const p = profile ?? user
  const displayName = `${p?.firstname ?? p?.name ?? ''} ${p?.lastname ?? ''}`.trim()

  return (
    <>
      <div className="page-header">
        <h1>My Profile</h1>
        <p>View and update your personal information.</p>
      </div>

      {/* Profile card */}
      <div className="card" style={{marginBottom:20}}>
        <div style={{display:'flex',alignItems:'center',gap:20,marginBottom:24}}>
          <Avatar name={displayName} size="lg"/>
          <div>
            <div style={{fontSize:'1.2rem',fontWeight:700}}>{displayName}</div>
            <div style={{color:'var(--c-muted)',fontSize:'.875rem'}}>{p?.email}</div>
            <div style={{color:'var(--c-muted)',fontSize:'.8rem',marginTop:2}}>{p?.type ?? 'Employee'}</div>
          </div>
          <div style={{marginLeft:'auto',display:'flex',gap:10}}>
            <button className="btn btn-secondary" onClick={()=>setEditing(true)}><Pencil size={14}/>Edit Profile</button>
            <button className="btn btn-secondary" onClick={()=>setShowPw(true)}><KeyRound size={14}/>Change Password</button>
          </div>
        </div>

        <div className="grid-2">
          {[
            ['First Name',  p?.firstname],
            ['Last Name',   p?.lastname],
            ['Email',       p?.email],
            ['Phone',       p?.phone ?? '—'],
            ['Department',  p?.department?.name ?? '—'],
            ['Designation', p?.designation?.name ?? '—'],
          ].map(([label, val]) => (
            <div key={label}>
              <div style={{fontSize:'.78rem',color:'var(--c-muted)',marginBottom:4}}>{label}</div>
              <div style={{fontWeight:500}}>{val || '—'}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Edit Modal */}
      <Modal open={editing} onClose={()=>setEditing(false)} title="Edit Profile">
        <form onSubmit={save}>
          <div className="field-row">
            <Input label="First Name" value={form.firstname??''} onChange={e=>setForm(f=>({...f,firstname:e.target.value}))}/>
            <Input label="Last Name"  value={form.lastname??''}  onChange={e=>setForm(f=>({...f,lastname:e.target.value}))}/>
          </div>
          <Input label="Phone" value={form.phone??''} onChange={e=>setForm(f=>({...f,phone:e.target.value}))}/>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={()=>setEditing(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving?'Saving…':'Save Changes'}</button>
          </div>
        </form>
      </Modal>

      {/* Change Password Modal */}
      <Modal open={showPw} onClose={()=>setShowPw(false)} title="Change Password">
        <form onSubmit={savePw}>
          {pwError && <div style={{color:'var(--c-danger)',marginBottom:12,fontSize:'.875rem'}}>{pwError}</div>}
          <Input label="Current Password" type="password" value={pwForm.current_password} onChange={e=>setPwForm(f=>({...f,current_password:e.target.value}))} required/>
          <Input label="New Password"     type="password" value={pwForm.password}          onChange={e=>setPwForm(f=>({...f,password:e.target.value}))}          required/>
          <Input label="Confirm Password" type="password" value={pwForm.password_confirmation} onChange={e=>setPwForm(f=>({...f,password_confirmation:e.target.value}))} required/>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={()=>setShowPw(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={pwSaving}>{pwSaving?'Saving…':'Update Password'}</button>
          </div>
        </form>
      </Modal>
    </>
  )
}
