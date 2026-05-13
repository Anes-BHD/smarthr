import { EmptyState } from '../../components/ui/index'

export default function AdminSales() {
  return (
    <>
      <div className="page-header">
        <h1>Sales</h1>
        <p>Manage estimates, invoices, expenses, and taxes.</p>
      </div>
      <div className="card">
        <EmptyState title="Sales Module" desc="This page is under construction." />
      </div>
    </>
  )
}
