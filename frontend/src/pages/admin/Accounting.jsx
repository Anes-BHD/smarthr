import { EmptyState } from '../../components/ui/index'

export default function AdminAccounting() {
  return (
    <>
      <div className="page-header">
        <h1>Accounting</h1>
        <p>Manage budgets, revenues, and categories.</p>
      </div>
      <div className="card">
        <EmptyState title="Accounting Module" desc="This page is under construction." />
      </div>
    </>
  )
}
