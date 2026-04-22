import { EmptyState } from '../../components/ui/index'

export default function AdminClients() {
  return (
    <>
      <div className="page-header">
        <h1>Clients</h1>
        <p>Manage your clients and their profiles.</p>
      </div>
      <div className="card">
        <EmptyState title="Clients Module" desc="This page is under construction." />
      </div>
    </>
  )
}
