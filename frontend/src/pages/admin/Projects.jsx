import { EmptyState } from '../../components/ui/index'

export default function AdminProjects() {
  return (
    <>
      <div className="page-header">
        <h1>Projects</h1>
        <p>Manage all projects and task boards.</p>
      </div>
      <div className="card">
        <EmptyState title="Projects Module" desc="This page is under construction." />
      </div>
    </>
  )
}
