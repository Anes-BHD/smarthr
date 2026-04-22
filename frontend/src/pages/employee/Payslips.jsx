import { useState, useEffect } from 'react'
import { employeeApi } from '../../lib/api'
import { Spinner, EmptyState } from '../../components/ui/index'
import { Download } from 'lucide-react'

export default function EmployeePayslips() {
  const [payslips, setPayslips] = useState([])
  const [loading,  setLoading]  = useState(true)

  useEffect(() => {
    employeeApi.getPayslips()
      .then(r => setPayslips(r.data?.data ?? []))
      .finally(() => setLoading(false))
  }, [])

  const downloadPdf = slip => {
    const content = `PAYSLIP\n\nDate: ${slip.payslip_date ?? slip.created_at?.slice(0,10)}\nType: ${slip.type}\nBasic Salary: $${slip.basic_salary ?? 0}\nNet Salary: $${slip.net_salary ?? 0}\n`
    const blob = new Blob([content], { type:'text/plain' })
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob)
    a.download = `payslip-${slip.id}.txt`; a.click()
  }

  return (
    <>
      <div className="page-header">
        <h1>My Payslips</h1>
        <p>View and download your salary slips.</p>
      </div>

      <div className="card">
        {loading
          ? <Spinner/>
          : payslips.length === 0
            ? <EmptyState title="No payslips found" desc="Your payslips will appear here once generated."/>
            : (
            <div className="table-wrap">
              <table>
                <thead><tr>
                  <th>Date</th><th>Type</th><th>Net Salary</th><th>Action</th>
                </tr></thead>
                <tbody>
                  {payslips.map(slip => (
                    <tr key={slip.id}>
                      <td>{slip.payslip_date ?? slip.created_at?.slice(0,10)}</td>
                      <td>{slip.type}</td>
                      <td className="font-semibold">${Number(slip.net_salary ?? 0).toLocaleString()}</td>
                      <td>
                        <button className="btn btn-secondary btn-sm" onClick={() => downloadPdf(slip)}>
                          <Download size={14}/> Download
                        </button>
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
