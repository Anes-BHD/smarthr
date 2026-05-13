# SmartHR API - Quick Reference & Examples

## Quick Start

### 1. Get Authentication Token
```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"employee@smarthr.com","password":"password"}' | jq -r '.token')

echo $TOKEN
```

### 2. Use Token for All Requests
```bash
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8002/api/v1/employees
```

---

## HR Module Examples

### Employees
```bash
# List all employees
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/employees

# Get single employee
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/employees/1

# Create employee
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"firstname":"John","lastname":"Doe","email":"john@smarthr.com","type":"Employee"}' \
  http://127.0.0.1:8002/api/v1/employees
```

### Clients
```bash
# List all clients
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/clients

# Get single client
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/clients/1
```

### Attendances
```bash
# List all attendances
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/attendances

# Get attendance details
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/attendances/1
```

### Tickets (Support)
```bash
# List all tickets
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/tickets

# Get ticket details
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/tickets/1

# Create ticket
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"title":"Issue","description":"Ticket description","priority":"high"}' \
  http://127.0.0.1:8002/api/v1/tickets
```

### Assets
```bash
# List all assets
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/assets

# Get asset details
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/assets/1
```

### Payslips
```bash
# List all payslips
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/payslips

# Get payslip details
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/payslips/1

# Create payslip
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"employee_detail_id":1,"payslip_date":"2026-04-22","type":"Monthly"}' \
  http://127.0.0.1:8002/api/v1/payslips
```

### Holidays
```bash
# List all holidays
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/holidays

# Get holiday details
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/holidays/1
```

---

## Sales Module Examples

### Invoices ✅
```bash
# List all invoices
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/invoices

# Get invoice details
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/invoices/1

# Create invoice
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client": 1,
    "billing_address": "123 Main St",
    "startDate": "2026-04-01",
    "expiryDate": "2026-05-01",
    "items": [
      {"name": "Service 1", "cost": 100, "qty": 2}
    ]
  }' \
  http://127.0.0.1:8002/api/v1/invoices
```

### Estimates ✅
```bash
# List all estimates
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/estimates

# Get estimate details
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/estimates/1

# Create estimate
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client": 1,
    "billing_address": "456 Oak Ave",
    "startDate": "2026-04-01",
    "expiryDate": "2026-04-30"
  }' \
  http://127.0.0.1:8002/api/v1/estimates
```

### Taxes ✅
```bash
# List all taxes
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/taxes

# Get tax details
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/taxes/1

# Create tax
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Custom Tax","percentage":5,"status":true}' \
  http://127.0.0.1:8002/api/v1/taxes
```

### Expenses ✅
```bash
# List all expenses
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/expenses

# Get expense details
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/expenses/1

# Create expense
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_name": "Office Supplies",
    "purchase_from": "Office Depot",
    "amount": 150.50,
    "status": 1,
    "paid_by": 1
  }' \
  http://127.0.0.1:8002/api/v1/expenses
```

---

## Accounting Module Examples ✅

### Budgets ✅
```bash
# List all budgets
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/budgets

# Get budget details
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/budgets/1

# Create budget
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Q2 Budget",
    "type": "Monthly",
    "budget_amount": 50000,
    "startDate": "2026-04-01",
    "endDate": "2026-06-30",
    "note": "Q2 planning"
  }' \
  http://127.0.0.1:8002/api/v1/budgets
```

### Budget Categories ✅
```bash
# List all budget categories
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/budget-categories

# Get category details
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/budget-categories/1

# Create category
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"New Category"}' \
  http://127.0.0.1:8002/api/v1/budget-categories
```

---

## Authentication Examples

### Login
```bash
curl -X POST http://127.0.0.1:8002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "employee@smarthr.com",
    "password": "password"
  }'
```

### Get Current User
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/auth/me
```

### Logout
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8002/api/v1/auth/logout
```

---

## Response Examples

### Successful List Response
```json
{
  "data": [
    {
      "id": 1,
      "firstname": "John",
      "lastname": "Doe",
      "email": "john@smarthr.com",
      "type": "Employee",
      "created_at": "2026-04-21T23:49:22.000000Z"
    }
  ],
  "links": {
    "first": "http://127.0.0.1:8002/api/v1/employees?page=1",
    "last": "http://127.0.0.1:8002/api/v1/employees?page=1",
    "prev": null,
    "next": null
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 1,
    "per_page": 15,
    "to": 15,
    "total": 15
  }
}
```

### Successful Create Response
```json
{
  "message": "Record created successfully",
  "data": {
    "id": 50,
    "firstname": "Jane",
    "lastname": "Smith",
    "email": "jane@smarthr.com",
    "type": "Employee",
    "created_at": "2026-04-22T10:30:00.000000Z"
  }
}
```

### Error Response
```json
{
  "message": "Validation failed",
  "errors": {
    "email": ["Email already exists"]
  }
}
```

---

## Testing Workflow

### 1. Get Token (Save it)
```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"employee@smarthr.com","password":"password"}' | jq -r '.token')
```

### 2. Test Different Modules
```bash
# Test HR
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8002/api/v1/employees | jq

# Test Sales
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8002/api/v1/invoices | jq

# Test Accounting
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8002/api/v1/budgets | jq
```

### 3. Run Verification Scripts
```bash
# Basic verification
bash api-test-verification.sh

# Complete verification
bash api-complete-verification.sh
```

---

## Default Test Accounts

**Employee Account:**
- Email: `employee@smarthr.com`
- Password: `password`

**Client Account:**
- Email: `client@smarthr.com`
- Password: `password`

**Admin Account:**
- Email: `superadmin@smarthr.com`
- Password: `password`

---

## Useful Tools

### Save Token to File
```bash
curl -s -X POST http://127.0.0.1:8002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"employee@smarthr.com","password":"password"}' | jq -r '.token' > token.txt

TOKEN=$(cat token.txt)
```

### Pretty Print JSON
```bash
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8002/api/v1/employees | jq .
```

### Count Records
```bash
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8002/api/v1/employees | jq '.data | length'
```

### Extract Specific Fields
```bash
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8002/api/v1/employees | jq '.data[].email'
```

---

## API Documentation Links

- **Full Setup:** API_SETUP_DOCUMENTATION.md
- **Implementation Summary:** IMPLEMENTATION_SUMMARY.md
- **API Routes:** routes/api.php
- **Test Scripts:** api-complete-verification.sh

Happy API Testing! 🚀
