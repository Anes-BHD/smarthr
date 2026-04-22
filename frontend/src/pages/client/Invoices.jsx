import { useState, useEffect } from 'react'
import { clientApi } from '../../lib/api'
import { Spinner, EmptyState, StatusBadge } from '../../components/ui/index'
import { Download } from 'lucide-react'

export default function ClientInvoices() {
  const [invoices, setInvoices] = useState([])
  const [loading,  setLoading]  = useState(true)

  useEffect(() => {
    clientApi.getInvoices()
      .then(r => setInvoices(r.data?.data ?? []))
      .finally(() => setLoading(false))
  }, [])

  const downloadPdf = inv => {
    const content = `INVOICE #${inv.id}\n\nDate: ${inv.startDate ?? inv.created_at?.slice(0,10)}\nDue: ${inv.expiryDate ?? '—'}\nAmount: $${inv.total ?? 0}\nStatus: ${inv.status ?? 'Pending'}\n`
    const blob = new Blob([content], { type:'text/plain' })
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob)
    a.download = `invoice-${inv.id}.txt`; a.click()
  }

  return (
    <>
      <div className="page-header">
        <h1>Invoices</h1>
        <p>View and download your billing history.</p>
      </div>

      <div className="card">
        {loading
          ? <Spinner/>
          : invoices.length === 0
            ? <EmptyState title="No invoices" desc="You don't have any invoices yet."/>
            : (
            <div className="table-wrap">
              <table>
                <thead><tr>
                  <th>Invoice ID</th><th>Date</th><th>Due Date</th><th>Amount</th><th>Status</th><th>Action</th>
                </tr></thead>
                <tbody>
                  {invoices.map(inv => (
                    <tr key={inv.id}>
                      <td className="font-semibold" style={{color:'var(--c-primary)'}}>#INV-{inv.id.toString().padStart(4, '0')}</td>
                      <td>{inv.startDate ?? inv.created_at?.slice(0,10)}</td>
                      <td>{inv.expiryDate ?? '—'}</td>
                      <td className="font-semibold">${Number(inv.total ?? 0).toLocaleString()}</td>
                      <td><StatusBadge status={inv.status ?? 'pending'}/></td>
                      <td>
                        <button className="btn btn-secondary btn-sm" onClick={() => downloadPdf(inv)}>
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
