<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\V1\AuthController;
use App\Http\Controllers\Api\V1\AssetController;
use App\Http\Controllers\Api\V1\ClientController;
use App\Http\Controllers\Api\V1\TicketController;
use App\Http\Controllers\Api\V1\HolidayController;
use App\Http\Controllers\Api\V1\PayslipController;
use App\Http\Controllers\Api\V1\EmployeeController;
use App\Http\Controllers\Api\V1\UserController;
use App\Http\Controllers\Api\V1\DepartmentController;
use App\Http\Controllers\Api\V1\DesignationController;
use App\Http\Controllers\Api\V1\AttendanceController;
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
        Route::apiResource('employees', EmployeeController::class);
        Route::apiResource('clients', ClientController::class);
        Route::apiResource('departments', DepartmentController::class);
        Route::apiResource('designations', DesignationController::class);
        Route::apiResource('users', UserController::class);
        Route::apiResource('attendances', AttendanceController::class)->only(['index', 'show']);
        Route::apiResource('payslips', PayslipController::class);
        Route::apiResource('holidays', HolidayController::class);
        Route::apiResource('tickets', TicketController::class);
        Route::apiResource('assets', AssetController::class);

        // Sales Module
        Route::apiResource('invoices', InvoiceController::class);
        Route::apiResource('estimates', EstimateController::class);
        Route::apiResource('taxes', TaxController::class);
        Route::apiResource('expenses', ExpenseController::class);

        // Accounting Module
        Route::apiResource('budgets', BudgetController::class);
        Route::apiResource('budget-categories', BudgetCategoryController::class);
    });
});
