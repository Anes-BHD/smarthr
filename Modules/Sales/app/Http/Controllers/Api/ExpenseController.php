<?php

namespace Modules\Sales\Http\Controllers\Api;

use Modules\Sales\Models\Expense;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;

class ExpenseController extends Controller
{
    public function index(Request $request)
    {
        $expenses = Expense::latest()->paginate($request->per_page ?? 15);
        return response()->json(['data' => $expenses]);
    }

    public function store(Request $request)
    {
        $request->validate([
            'item_name'     => 'required|string',
            'purchase_from' => 'required|string',
            'amount'        => 'required|numeric',
            'status'        => 'required',
            'paid_by'       => 'required',
        ]);

        $expense = Expense::create([
            'item_name'      => $request->item_name,
            'purchased_from' => $request->purchase_from,
            'purchase_date'  => $request->purchase_date ?? now(),
            'amount'         => $request->amount,
            'status'         => $request->status,
            'paid_by'        => $request->paid_by,
            'created_by'     => auth()->user()->id,
        ]);

        return response()->json([
            'message' => __('Expense has been created'),
            'data'    => $expense,
        ], 201);
    }

    public function show(Expense $expense)
    {
        return response()->json(['data' => $expense]);
    }

    public function update(Request $request, Expense $expense)
    {
        $request->validate([
            'item_name'     => 'required|string',
            'purchase_from' => 'required|string',
            'amount'        => 'required|numeric',
            'status'        => 'required',
            'paid_by'       => 'required',
        ]);

        $expense->update([
            'item_name'      => $request->item_name,
            'purchased_from' => $request->purchase_from,
            'purchase_date'  => $request->purchase_date ?? now(),
            'amount'         => $request->amount,
            'status'         => $request->status,
            'paid_by'        => $request->paid_by,
            'created_by'     => auth()->user()->id,
        ]);

        return response()->json([
            'message' => __('Expense has been updated'),
            'data'    => $expense,
        ]);
    }

    public function destroy(Expense $expense)
    {
        $expense->delete();
        return response()->json(['message' => __('Expense has been deleted')]);
    }
}
