<?php

use Illuminate\Support\Facades\Route;
use Modules\Sales\Http\Controllers\Api\TaxController;
use Modules\Sales\Http\Controllers\Api\ExpenseController;
use Modules\Sales\Http\Controllers\Api\InvoiceController;
use Modules\Sales\Http\Controllers\Api\EstimateController;

/*
 *--------------------------------------------------------------------------
 * API Routes
 *--------------------------------------------------------------------------
 *
 * Here is where you can register API routes for your application. These
 * routes are loaded by the RouteServiceProvider within a group which
 * is assigned the "api" middleware group. Enjoy building your API!
 *
*/

Route::middleware(['auth:sanctum'])->prefix('v1')->group(function () {
    Route::apiResource('invoices', InvoiceController::class)->names('api.invoices');
    Route::apiResource('expenses', ExpenseController::class)->names('api.expenses');
    Route::apiResource('estimates', EstimateController::class)->names('api.estimates');
    Route::apiResource('taxes', TaxController::class)->names('api.taxes');
});
