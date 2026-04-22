<?php

namespace Modules\Accounting\Http\Controllers\Api;

use Modules\Accounting\Models\Budget;
use Modules\Accounting\Models\ExpenseBudget;
use Modules\Accounting\Models\RevenueBudget;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;

class BudgetController extends Controller
{
    public function index(Request $request)
    {
        $budgets = Budget::with(['category', 'project'])
            ->latest()->paginate($request->per_page ?? 15);
        return response()->json(['data' => $budgets]);
    }

    public function store(Request $request)
    {
        $request->validate([
            'title'         => 'required|string',
            'type'          => 'required|string',
            'budget_amount' => 'required|numeric',
            'startDate'     => 'date|before_or_equal:endDate',
            'endDate'       => 'date|after_or_equal:startDate',
            'note'          => 'nullable|string|max:255',
        ]);

        $budget = Budget::create([
            'title'              => $request->title,
            'type'               => $request->type,
            'startDate'          => $request->startDate,
            'endDate'            => $request->endDate,
            'total_revenue'      => $request->overall_revenues,
            'total_expense'      => $request->overall_expenses,
            'profit'             => $request->expected_profit,
            'budget_category_id' => $request->category,
            'project_id'         => $request->project,
            'taxes'              => $request->tax,
            'amount'             => $request->budget_amount,
            'note'               => $request->note,
        ]);

        if (!empty($request->expenses)) {
            foreach ($request->expenses as $item) {
                ExpenseBudget::create([
                    'title'              => $item['title'],
                    'amount'             => $item['amount'],
                    'budget_id'          => $budget->id,
                    'budget_category_id' => $budget->budget_category_id,
                    'startDate'          => $budget->startDate,
                    'endDate'            => $budget->endDate,
                ]);
            }
        }

        if (!empty($request->revenues)) {
            foreach ($request->revenues as $item) {
                RevenueBudget::create([
                    'title'              => $item['title'],
                    'amount'             => $item['amount'],
                    'budget_id'          => $budget->id,
                    'budget_category_id' => $budget->budget_category_id,
                    'startDate'          => $budget->startDate,
                    'endDate'            => $budget->endDate,
                ]);
            }
        }

        $budget->load(['category', 'expenses', 'revenue']);

        return response()->json([
            'message' => __('Budget has been added'),
            'data'    => $budget,
        ], 201);
    }

    public function show(Budget $budget)
    {
        $budget->load(['category', 'project', 'expenses', 'revenue']);
        return response()->json(['data' => $budget]);
    }

    public function update(Request $request, Budget $budget)
    {
        $request->validate([
            'title'         => 'required|string',
            'type'          => 'required|string',
            'budget_amount' => 'required|numeric',
            'startDate'     => 'date|before_or_equal:endDate',
            'endDate'       => 'date|after_or_equal:startDate',
        ]);

        $budget->update([
            'title'              => $request->title,
            'type'               => $request->type,
            'startDate'          => $request->startDate,
            'endDate'            => $request->endDate,
            'total_revenue'      => $request->overall_revenues,
            'total_expense'      => $request->overall_expenses,
            'profit'             => $request->expected_profit,
            'budget_category_id' => $request->category,
            'project_id'         => $request->project,
            'taxes'              => $request->tax,
            'amount'             => $request->budget_amount,
            'note'               => $request->note,
        ]);

        $budget->load(['category', 'expenses', 'revenue']);

        return response()->json([
            'message' => __('Budget has been updated'),
            'data'    => $budget,
        ]);
    }

    public function destroy(Budget $budget)
    {
        $budget->delete();
        return response()->json(['message' => __('Budget has been deleted')]);
    }
}
