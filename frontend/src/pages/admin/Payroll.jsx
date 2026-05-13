import { useState, useEffect } from 'react'
import { adminApi } from '../../lib/api'
import { Spinner, EmptyState, Pagination, Modal, Confirm, Input, Select } from '../../components/ui/index'
import { Plus, Trash2, Download } from 'lucide-react'

const BLANK = { employee_detail_id:'', payslip_date:'', type:'Monthly', net_salary:'', basic_salary:'' }

export default function AdminPayroll() {
  const [rows,      setRows]      = useState([])
  const [meta,      setMeta]      = useState(null)
  const [page,      setPage]      = useState(1)
  const [employees, setEmployees] = useState([])
  const [loading,   setLoading]   = useState(true)
  const [showM,     setShowM]     = useState(false)
  const [form,      setForm]      = useState(BLANK)
  const [saving,    setSaving]    = useState(false)
  const [delId,     setDelId]     = useState(null)
  const [deleting,  setDeleting]  = useState(false)

  const load = (p = page) => {
    setLoading(true)
    adminApi.getPayslips(p)
      .then(r => { setRows(r.data?.data ?? []); setMeta(r.data?.meta ?? null) })
      .finally(() => setLoading(false))
  }

  useEffect(() => { load(page) }, [page]) // eslint-disable-line
  useEffect(() => { adminApi.getEmployees().then(r => setEmployees(r.data?.data ?? [])) }, [])

  const save = async e => {
    e.preventDefault(); setSaving(true)
    try { await adminApi.createPayslip(form); setShowM(false); load(page) }
    catch {} finally { setSaving(false) }
  }

  const doDelete = async () => {
    setDeleting(true)
    try { await adminApi.deletePayslip(delId); setDelId(null); load(page) }
    catch {} finally { setDeleting(false) }
  }

  const downloadPdf = slip => {
    const content = `PAYSLIP\n\nEmployee ID: ${slip.employee_detail_id}\nDate: ${slip.payslip_date}\nType: ${slip.type}\nNet Salary: $${slip.net_salary ?? 0}\n`
    const blob = new Blob([content], { type:'text/plain' })
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob)
    a.download = `payslip-${slip.id}.txt`; a.click()
  }

  return (
    <>
      <div className="page-header">
        <h1>Payroll</h1>
        <p>Manage payslips and payroll records.</p>
      </div>

      <div className="card">
        <div className="toolbar">
          <div className="toolbar-right">
            <button className="btn btn-primary" onClick={()=>{setForm(BLANK);setShowM(true)}}>
              <Plus size={15}/>Create Payslip
            </button>
          </div>
        </div>

        {loading
          ? <Spinner/>
          : rows.length === 0
            ? <EmptyState title="No payslips yet" desc="Create the first payslip to get started."/>
            : (
            <div className="table-wrap">
              <table>
                <thead><tr>
                  <th>#</th><th>Employee</th><th>Date</th><th>Type</th><th>Net Salary</th><th>Actions</th>
                </tr></thead>
                <tbody>
                  {rows.map(slip => (
                    <tr key={slip.id}>
                      <td style={{color:'var(--c-muted)',fontSize:'.8rem'}}>{slip.id}</td>
                      <td>{slip.employee_detail_id}</td>
                      <td style={{color:'var(--c-muted)'}}>{slip.payslip_date ?? slip.created_at?.slice(0,10)}</td>
                      <td>{slip.type}</td>
                      <td className="font-semibold">${Number(slip.net_salary ?? 0).toLocaleString()}</td>
                      <td>
                        <div style={{display:'flex',gap:6}}>
                          <button className="btn-icon" onClick={()=>downloadPdf(slip)} title="Download"><Download size={14}/></button>
                          <button className="btn-icon" onClick={()=>setDelId(slip.id)} title="Delete" style={{color:'var(--c-danger)'}}><Trash2 size={14}/></button>
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

      <Modal open={showM} onClose={()=>setShowM(false)} title="Create Payslip">
        <form onSubmit={save}>
          <Select label="Employee" value={form.employee_detail_id} onChange={e=>setForm(f=>({...f,employee_detail_id:e.target.value}))} required>
            <option value="">Select employee</option>
            {employees.map(emp=>(
              <option key={emp.id} value={emp.id}>{emp.firstname} {emp.lastname}</option>
            ))}
          </Select>
          <Input label="Payslip Date" type="date" value={form.payslip_date} onChange={e=>setForm(f=>({...f,payslip_date:e.target.value}))} required/>
          <Select label="Type" value={form.type} onChange={e=>setForm(f=>({...f,type:e.target.value}))}>
            <option>Monthly</option><option>Weekly</option><option>Bonus</option>
          </Select>
          <div className="field-row">
            <Input label="Basic Salary ($)" type="number" value={form.basic_salary} onChange={e=>setForm(f=>({...f,basic_salary:e.target.value}))}/>
            <Input label="Net Salary ($)"   type="number" value={form.net_salary}   onChange={e=>setForm(f=>({...f,net_salary:e.target.value}))}/>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={()=>setShowM(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving?'Creating…':'Create'}</button>
          </div>
        </form>
      </Modal>

      <Confirm open={!!delId} onClose={()=>setDelId(null)} onConfirm={doDelete} loading={deleting}
        title="Delete Payslip" message="This payslip record will be permanently removed."/>
    </>
  )
}
