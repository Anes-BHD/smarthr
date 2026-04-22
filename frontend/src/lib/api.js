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
  getDepartments: () => http.get('/departments'),
  // Designations
  getDesignations: () => http.get('/designations'),

  // Clients
  getClients:   (p=1) => http.get(`/clients?page=${p}`),
  createClient: data  => http.post('/clients', data),
  updateClient: (id,d)=> http.put(`/clients/${id}`, d),
  deleteClient: id    => http.delete(`/clients/${id}`),
}

// ─── Employee ────────────────────────────────────────────────────────────
export const employeeApi = {
  me:           ()   => http.get('/auth/me'),
  getPayslips:  ()   => http.get('/payslips'),
  getTickets:   ()   => http.get('/tickets'),
  createTicket: d    => http.post('/tickets', d),
  getProfile:   id   => http.get(`/employees/${id}`),
  updateProfile:(id,d)=>http.put(`/employees/${id}`, d),
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

export default http
