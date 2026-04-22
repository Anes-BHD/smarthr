<?php

namespace Database\Seeders;

use App\Models\User;
use App\Enums\UserType;
use App\Models\Asset;
use App\Models\Ticket;
use App\Models\Holiday;
use App\Models\Payslip;
use App\Models\Attendance;
use App\Models\Department;
use App\Models\Designation;
use App\Models\ClientDetail;
use App\Models\EmployeeDetail;
use Illuminate\Database\Seeder;
use App\Models\AttendanceTimestamp;
use Modules\Sales\Models\Invoice;
use Modules\Sales\Models\Expense;
use Modules\Sales\Models\Estimate;
use Modules\Sales\Models\Tax;
use Modules\Accounting\Models\Budget;
use Modules\Accounting\Models\BudgetCategory;
use Modules\Accounting\Models\ExpenseBudget;
use Modules\Accounting\Models\RevenueBudget;
use Spatie\Permission\Models\Role;

class ApiTestSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // 0. Create roles if they don't exist
        $this->createRoles();

        // 1. Ensure Departments and Designations exist
        if (Department::count() === 0) {
            $this->call(DemoDataSeeder::class);
        }

        $departments = Department::all();
        $designations = Designation::all();

        // 2. Create Employees
        User::factory(10)->create([
            'type' => UserType::EMPLOYEE,
        ])->each(function ($user) use ($departments, $designations) {
            $user->assignRole(UserType::EMPLOYEE);
            
            // Employee details and salary are created in UserFactory afterCreating hook
            $detail = $user->employeeDetail;
            if ($detail) {
                $detail->update([
                    'department_id' => $departments->random()->id,
                    'designation_id' => $designations->random()->id,
                ]);

                // Create some attendance for this employee
                for ($i = 0; $i < 5; $i++) {
                    $attendance = Attendance::factory()->create([
                        'user_id' => $user->id,
                        'startDate' => now()->subDays($i)->format('Y-m-d'),
                    ]);

                    AttendanceTimestamp::factory()->create([
                        'user_id' => $user->id,
                        'attendance_id' => $attendance->id,
                        'created_at' => now()->subDays($i),
                    ]);
                }

                // Create some assets for this employee
                Asset::factory(2)->create([
                    'user_id' => $user->id,
                    'created_by' => 1, // Admin
                ]);

                // Create some tickets for this employee
                Ticket::factory(2)->create([
                    'user_id' => $user->id,
                    'created_by' => 1,
                ]);
            }
        });

        // 3. Create Clients
        User::factory(5)->create([
            'type' => UserType::CLIENT,
        ])->each(function ($user) {
            $user->assignRole(UserType::CLIENT);
            ClientDetail::factory()->create([
                'user_id' => $user->id,
            ]);
        });

        // 4. Create Holidays
        if (Holiday::count() < 5) {
            Holiday::factory(5)->create();
        }

        // 5. Create Payslips for employees
        EmployeeDetail::all()->each(function ($detail) {
            Payslip::factory(2)->create([
                'employee_detail_id' => $detail->id,
            ]);
        });

        // 6. Sales Module Data (Taxes, Invoices, Estimates, Expenses)
        $this->seedSalesData();

        // 7. Accounting Module Data (Budgets, BudgetCategories)
        $this->seedAccountingData();
    }

    /**
     * Seed sales module data
     */
    private function seedSalesData(): void
    {
        $clients = User::where('type', UserType::CLIENT)->get();
        
        if ($clients->isEmpty()) {
            return;
        }

        // Create taxes
        Tax::firstOrCreate(['name' => 'VAT'], ['percentage' => 15, 'active' => true]);
        Tax::firstOrCreate(['name' => 'GST'], ['percentage' => 10, 'active' => true]);
        Tax::firstOrCreate(['name' => 'Sales Tax'], ['percentage' => 8, 'active' => true]);

        // Create invoices
        Invoice::factory(5)->create([
            'client_id' => $clients->random()->id,
        ]);

        // Create expenses
        Expense::factory(5)->create();

        // Create estimates
        Estimate::factory(5)->create([
            'client_id' => $clients->random()->id,
        ]);
    }

    /**
     * Seed accounting module data
     */
    private function seedAccountingData(): void
    {
        // Create budget categories
        $categories = [
            'Marketing',
            'Operations',
            'Development',
            'HR',
            'Infrastructure',
        ];

        foreach ($categories as $category) {
            BudgetCategory::firstOrCreate(['name' => $category]);
        }

        $budgetCategories = BudgetCategory::all();

        if ($budgetCategories->isEmpty()) {
            return;
        }

        // Create budgets with expense and revenue budgets
        for ($i = 0; $i < 5; $i++) {
            $budget = Budget::factory()->create([
                'budget_category_id' => $budgetCategories->random()->id,
                'amount' => rand(10000, 100000),
            ]);

            // Create expense budgets for this budget
            for ($j = 0; $j < 3; $j++) {
                ExpenseBudget::factory()->create([
                    'budget_id' => $budget->id,
                    'amount' => rand(1000, 10000),
                ]);
            }

            // Create revenue budgets for this budget
            for ($j = 0; $j < 2; $j++) {
                RevenueBudget::factory()->create([
                    'budget_id' => $budget->id,
                    'amount' => rand(5000, 50000),
                ]);
            }
        }
    }

    /**
     * Create roles for different user types
     */
    private function createRoles(): void
    {
        $guard = 'web';
        
        // Create roles if they don't exist
        foreach (UserType::cases() as $userType) {
            Role::firstOrCreate(
                ['name' => $userType->value, 'guard_name' => $guard]
            );
        }
    }
}
