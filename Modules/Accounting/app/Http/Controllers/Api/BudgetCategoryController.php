<?php

namespace Modules\Accounting\Http\Controllers\Api;

use Modules\Accounting\Models\BudgetCategory;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;

class BudgetCategoryController extends Controller
{
    public function index(Request $request)
    {
        $categories = BudgetCategory::latest()->paginate($request->per_page ?? 15);
        return response()->json(['data' => $categories]);
    }

    public function store(Request $request)
    {
        $request->validate(['name' => 'required|string']);

        $category = BudgetCategory::create(['name' => $request->name]);

        return response()->json([
            'message' => __('Budget category has been created'),
            'data'    => $category,
        ], 201);
    }

    public function show(BudgetCategory $budgetCategory)
    {
        return response()->json(['data' => $budgetCategory]);
    }

    public function update(Request $request, BudgetCategory $budgetCategory)
    {
        $request->validate(['name' => 'required|string']);

        $budgetCategory->update(['name' => $request->name]);

        return response()->json([
            'message' => __('Budget category has been updated'),
            'data'    => $budgetCategory,
        ]);
    }

    public function destroy(BudgetCategory $budgetCategory)
    {
        $budgetCategory->delete();
        return response()->json(['message' => __('Budget category has been deleted')]);
    }
}
