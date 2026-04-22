<?php

namespace Modules\Sales\Http\Controllers\Api;

use Modules\Sales\Models\Tax;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;

class TaxController extends Controller
{
    public function index(Request $request)
    {
        $taxes = Tax::latest()->paginate($request->per_page ?? 15);
        return response()->json(['data' => $taxes]);
    }

    public function store(Request $request)
    {
        $request->validate([
            'name'       => 'required|string',
            'percentage' => 'required|numeric',
            'status'     => 'required|boolean',
        ]);

        $tax = Tax::create([
            'name'       => $request->name,
            'percentage' => $request->percentage,
            'active'     => $request->status,
        ]);

        return response()->json([
            'message' => __('Tax has been added'),
            'data'    => $tax,
        ], 201);
    }

    public function show(Tax $tax)
    {
        return response()->json(['data' => $tax]);
    }

    public function update(Request $request, Tax $tax)
    {
        $request->validate([
            'name'       => 'required|string',
            'percentage' => 'required|numeric',
            'status'     => 'required|boolean',
        ]);

        $tax->update([
            'name'       => $request->name,
            'percentage' => $request->percentage,
            'active'     => $request->status,
        ]);

        return response()->json([
            'message' => __('Tax has been updated'),
            'data'    => $tax,
        ]);
    }

    public function destroy(Tax $tax)
    {
        $tax->delete();
        return response()->json(['message' => __('Tax has been deleted')]);
    }
}
