<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\V1\AuthController;
use App\Http\Controllers\Api\V1\AssetController;
use App\Http\Controllers\Api\V1\ClientController;
use App\Http\Controllers\Api\V1\TicketController;
use App\Http\Controllers\Api\V1\ProjectController;
use App\Http\Controllers\Api\V1\HolidayController;
use App\Http\Controllers\Api\V1\PayslipController;
use App\Http\Controllers\Api\V1\EmployeeController;
use App\Http\Controllers\Api\V1\UserController;
use App\Http\Controllers\Api\V1\DepartmentController;
use App\Http\Controllers\Api\V1\DesignationController;
use App\Http\Controllers\Api\V1\AttendanceController;
use App\Http\Controllers\Api\V1\AbsenceController;
use Modules\Sales\Http\Controllers\Api\InvoiceController;
use Modules\Sales\Http\Controllers\Api\EstimateController;
use Modules\Sales\Http\Controllers\Api\TaxController;
use Modules\Sales\Http\Controllers\Api\ExpenseController;
use Modules\Accounting\Http\Controllers\Api\BudgetController;
use Modules\Accounting\Http\Controllers\Api\BudgetCategoryController;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded within a group which is assigned the "api" middleware
| group. All routes are prefixed with /api.
|
*/

Route::prefix('v1')->group(function () {

    // Public auth routes
    Route::post('auth/login', [AuthController::class, 'login']);

    // Protected routes
    Route::middleware('auth:sanctum')->group(function () {

        // Auth
        Route::post('auth/logout', [AuthController::class, 'logout']);
        Route::get('auth/me', [AuthController::class, 'me']);

        // Core HR entities
        Route::apiResource('employees', EmployeeController::class)->names('api.employees');
        Route::apiResource('clients', ClientController::class)->names('api.clients');
        Route::apiResource('departments', DepartmentController::class)->names('api.departments');
        Route::apiResource('designations', DesignationController::class)->names('api.designations');
        Route::apiResource('users', UserController::class)->names('api.users');
        Route::apiResource('attendances', AttendanceController::class)->only(['index', 'show'])->names('api.attendances');
        Route::get('absences', [AbsenceController::class, 'index']);
        Route::apiResource('payslips', PayslipController::class)->names('api.payslips');
        Route::apiResource('holidays', HolidayController::class)->names('api.holidays');
        Route::apiResource('tickets', TicketController::class)->names('api.tickets');
        Route::get('projects', [ProjectController::class, 'index']);
        Route::apiResource('assets', AssetController::class)->names('api.assets');

        // Sales Module
        Route::apiResource('invoices', InvoiceController::class)->names('api.invoices');
        Route::apiResource('estimates', EstimateController::class)->names('api.estimates');
        Route::apiResource('taxes', TaxController::class)->names('api.taxes');
        Route::apiResource('expenses', ExpenseController::class)->names('api.expenses');

        // Accounting Module
        Route::apiResource('budgets', BudgetController::class)->names('api.budgets');
        Route::apiResource('budget-categories', BudgetCategoryController::class)->names('api.budget-categories');
    });
});
