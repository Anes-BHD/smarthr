# SmartHR API - Complete Setup Documentation

## Overview
SmartHR API is fully set up with all core modules, test data, and API endpoints ready for testing and development.

## Completed Tasks

### 1. ✅ API Endpoints Created
All REST API endpoints have been implemented and tested.

#### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout  
- `GET /api/v1/auth/me` - Get current user

#### HR Module
- `GET|POST /api/v1/employees` - Manage employees
- `GET|POST /api/v1/clients` - Manage clients
- `GET|POST /api/v1/departments` - Manage departments
- `GET|POST /api/v1/designations` - Manage designations
- `GET|POST /api/v1/users` - Manage users
- `GET /api/v1/attendances` - View attendances
- `GET|POST /api/v1/payslips` - Manage payslips
- `GET|POST /api/v1/holidays` - Manage holidays
- `GET|POST /api/v1/tickets` - Manage support tickets
- `GET|POST /api/v1/assets` - Manage company assets

#### Sales Module
- `GET|POST /api/v1/invoices` - Manage invoices
- `GET|POST /api/v1/estimates` - Manage estimates
- `GET|POST /api/v1/taxes` - Manage tax rates
- `GET|POST /api/v1/expenses` - Manage expenses

#### Accounting Module
- `GET|POST /api/v1/budgets` - Manage budgets
- `GET|POST /api/v1/budget-categories` - Manage budget categories

### 2. ✅ Test Data Seeded

#### Core Data
- **Users**: 88 (61 Employees + 26 Clients + 1 SuperAdmin)
- **Departments**: 1
- **Designations**: 1

#### HR Module
- **Attendances**: 250 records
- **Assets**: 100 items
- **Tickets**: 100 support tickets
- **Payslips**: 308 payslips

#### Sales Module
- **Invoices**: 15 invoices
- **Estimates**: 10 estimates
- **Taxes**: 3 tax types (VAT, GST, Sales Tax)
- **Expenses**: 10 expense records

#### Accounting Module
- **Budgets**: 5 budgets
- **Budget Categories**: 60 categories
- **Expense Budgets**: 25 expense budget items
- **Revenue Budgets**: 30 revenue budget items

### 3. ✅ Files Modified/Created

#### API Routes
- **routes/api.php** - Added all module routes and controllers

#### Seeders
- **database/seeders/ApiTestSeeder.php** - Enhanced with all module data creation

#### Factories
- **Modules/Sales/database/factories/ExpenseFactory.php** - Fixed auth context
- **database/factories/ClientDetailFactory.php** - Fixed column mappings
- **database/factories/PayslipFactory.php** - Fixed attendance hour calculation

#### Resources
- **app/Http/Resources/AttendanceResource.php** - Fixed map() error handling

#### API Verification Scripts
- **api-test-verification.sh** - Basic endpoint verification
- **api-complete-verification.sh** - Comprehensive endpoint testing

## How to Use

### Start Development Server
```bash
cd /home/anesbhd/tst/smarthr
php artisan serve --port=8002
```

### Authentication
```bash
curl -X POST http://127.0.0.1:8002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"employee@smarthr.com","password":"password"}'
```

**Default Credentials:**
- Email: `employee@smarthr.com`
- Password: `password`

### Example API Calls

#### Get Employees
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:8002/api/v1/employees
```

#### Get Invoices
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:8002/api/v1/invoices
```

#### Get Budgets
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:8002/api/v1/budgets
```

### Run Tests
```bash
# Quick verification
bash api-test-verification.sh

# Comprehensive verification
bash api-complete-verification.sh
```

## API Response Format

### Success Response
```json
{
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      ...
    }
  ]
}
```

### Paginated Response
```json
{
  "data": [...],
  "links": {...},
  "meta": {
    "current_page": 1,
    "per_page": 15,
    "total": 50
  }
}
```

## Database Configuration

**Database Name:** smarthr  
**Driver:** MySQL  
**Host:** localhost  
**Port:** 3306

## Available Test Data

### Employee Account
- **Email:** employee@smarthr.com
- **Password:** password
- **Type:** Employee
- **Access:** All employee features + limited admin

### Client Account  
- **Email:** client@smarthr.com
- **Password:** password
- **Type:** Client
- **Access:** Client portal features

### Admin Account
- **Email:** superadmin@smarthr.com
- **Password:** password
- **Type:** Super Admin
- **Access:** Full system access

## Module Structure

```
Modules/
├── Sales/
│   ├── Models/ (Invoice, Estimate, Expense, Tax)
│   ├── Controllers/Api/ (InvoiceController, EstimateController, etc.)
│   └── database/factories/
├── Accounting/
│   ├── Models/ (Budget, BudgetCategory, ExpenseBudget, RevenueBudget)
│   ├── Controllers/Api/ (BudgetController, BudgetCategoryController)
│   └── database/factories/
├── Project/
├── Roles/
└── Whiteboard/
```

## Troubleshooting

### Port Already in Use
If port 8002 is already in use:
```bash
php artisan serve --port=8003
```

### Seeder Errors
Re-run the seeder:
```bash
php artisan db:seed --class=ApiTestSeeder
```

### Reset Database
```bash
php artisan migrate:fresh --seed
```

## Next Steps

1. ✅ All API endpoints are functional
2. ✅ Comprehensive test data is seeded
3. ✅ Authentication is working
4. ✅ All modules are integrated
5. Ready for: 
   - Frontend development
   - Mobile app integration
   - Custom feature development
   - Performance testing

## Support

For issues or questions, check:
- `/routes/api.php` - API route definitions
- `/database/seeders/ApiTestSeeder.php` - Test data generation
- Module controllers in `Modules/*/app/Http/Controllers/Api/`
