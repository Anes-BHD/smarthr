import axios from 'axios'

const BASE = '/api/v1'

const http = axios.create({ baseURL: BASE })

// ── Inject Bearer token on every request ──────────────────────────────────
http.interceptors.request.use(cfg => {
  const token = localStorage.getItem('shr_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// ── 401 → clear storage and redirect to login ─────────────────────────────
http.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('shr_token')
      localStorage.removeItem('shr_user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)

// ─── Auth ─────────────────────────────────────────────────────────────────
export const authApi = {
  login:  data => http.post('/auth/login', data),
  logout: ()   => http.post('/auth/logout'),
  me:     ()   => http.get('/auth/me'),
}

// ─── Admin / HR ──────────────────────────────────────────────────────────
export const adminApi = {
  // Employees
  getEmployees:   (p = 1) => http.get(`/employees?page=${p}`),
  getEmployee:    id      => http.get(`/employees/${id}`),
  createEmployee: data    => http.post('/employees', data),
  updateEmployee: (id, d) => http.put(`/employees/${id}`, d),
  deleteEmployee: id      => http.delete(`/employees/${id}`),

  // Users
  getUsers:   (p = 1) => http.get(`/users?page=${p}`),
  createUser: data    => http.post('/users', data),
  deleteUser: id      => http.delete(`/users/${id}`),

  // Payslips (Payroll)
  getPayslips:   (p = 1) => http.get(`/payslips?page=${p}`),
  createPayslip: data    => http.post('/payslips', data),
  deletePayslip: id      => http.delete(`/payslips/${id}`),

  // Tickets
  getTickets:   (p = 1) => http.get(`/tickets?page=${p}`),
  updateTicket: (id, d) => http.put(`/tickets/${id}`, d),

  // Holidays
  getHolidays:   ()   => http.get('/holidays'),
  createHoliday: d    => http.post('/holidays', d),
  deleteHoliday: id   => http.delete(`/holidays/${id}`),

  // Departments
  getDepartments:  () => http.get('/departments'),
  getDesignations: () => http.get('/designations'),

  // Clients
  getClients:   (p = 1) => http.get(`/clients?page=${p}`),
  createClient: data    => http.post('/clients', data),
  updateClient: (id, d) => http.put(`/clients/${id}`, d),
  deleteClient: id      => http.delete(`/clients/${id}`),

  // Absences (computed from attendance, read-only)
  getAbsences: (params = {}) => http.get('/absences', { params }),

  // Projects
  getProjects: (params = {}) => http.get('/projects', { params }),

  // Sales — Invoices
  getInvoices:   (p = 1) => http.get(`/invoices?page=${p}`),
  createInvoice: data    => http.post('/invoices', data),
  deleteInvoice: id      => http.delete(`/invoices/${id}`),

  // Sales — Estimates
  getEstimates:   (p = 1) => http.get(`/estimates?page=${p}`),
  createEstimate: data    => http.post('/estimates', data),
  deleteEstimate: id      => http.delete(`/estimates/${id}`),

  // Sales — Taxes
  getTaxes:   () => http.get('/taxes'),
  createTax:  data => http.post('/taxes', data),
  updateTax:  (id, d) => http.put(`/taxes/${id}`, d),
  deleteTax:  id => http.delete(`/taxes/${id}`),

  // Sales — Expenses
  getExpenses:   (p = 1) => http.get(`/expenses?page=${p}`),
  createExpense: data    => http.post('/expenses', data),
  deleteExpense: id      => http.delete(`/expenses/${id}`),

  // Accounting — Budgets
  getBudgets:   (p = 1) => http.get(`/budgets?page=${p}`),
  createBudget: data    => http.post('/budgets', data),
  deleteBudget: id      => http.delete(`/budgets/${id}`),

  // Accounting — Budget Categories
  getBudgetCategories:   (p = 1) => http.get(`/budget-categories?page=${p}`),
  createBudgetCategory:  data    => http.post('/budget-categories', data),
  deleteBudgetCategory:  id      => http.delete(`/budget-categories/${id}`),
}

// ─── Employee ────────────────────────────────────────────────────────────
export const employeeApi = {
  me:           ()          => http.get('/auth/me'),
  getPayslips:  ()          => http.get('/payslips'),
  getTickets:   ()          => http.get('/tickets'),
  createTicket: d           => http.post('/tickets', d),
  getProfile:   id          => http.get(`/employees/${id}`),
  updateProfile:(id, d)     => http.put(`/employees/${id}`, d),
  getAbsences:  (params={}) => http.get('/absences', { params }),
}

// ─── Client ──────────────────────────────────────────────────────────────
export const clientApi = {
  me:            ()   => http.get('/auth/me'),
  getInvoices:   ()   => http.get('/invoices'),
  getTickets:    ()   => http.get('/tickets'),
  createTicket:  d    => http.post('/tickets', d),
  getProfile:    id   => http.get(`/clients/${id}`),
  updateProfile: (id,d)=>http.put(`/clients/${id}`, d),
}

// ── Response normalizer ──────────────────────────────────────────────────────
// Some controllers use JsonResource::collection() → { data:[...], meta:{...} }
// Others use response()->json(['data' => $paginator]) → { data:{ data:[...], current_page, ... } }
// This helper handles both so callers don't need to care.
export function extractPage(r) {
  const payload = r.data?.data
  if (Array.isArray(payload)) {
    return { rows: payload, meta: r.data?.meta ?? null }
  }
  return {
    rows: payload?.data ?? [],
    meta: payload
      ? { current_page: payload.current_page, last_page: payload.last_page, per_page: payload.per_page, total: payload.total, from: payload.from, to: payload.to }
      : null,
  }
}

export default http
