<?php

namespace Modules\Sales\Http\Controllers\Api;

use Modules\Sales\Models\Estimate;
use Modules\Sales\Models\EstimateItem;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;

class EstimateController extends Controller
{
    public function index(Request $request)
    {
        $estimates = Estimate::with(['client', 'items'])
            ->latest()->paginate($request->per_page ?? 15);
        return response()->json(['data' => $estimates]);
    }

    public function store(Request $request)
    {
        $request->validate([
            'client'          => 'required|exists:users,id',
            'billing_address' => 'required|string',
            'startDate'       => 'required|date|before_or_equal:expiryDate',
            'expiryDate'      => 'required|date|after_or_equal:startDate',
        ]);

        $estimate = Estimate::create([
            'est_id'          => "EST-" . pad_zeros(Estimate::count() + 1),
            'client_id'       => $request->client,
            'project_id'      => $request->project,
            'taxe_id'         => $request->tax,
            'client_address'  => $request->client_address,
            'billing_address' => $request->billing_address,
            'startDate'       => $request->startDate,
            'expiryDate'      => $request->expiryDate,
            'tax_amount'      => $request->taxes_sum,
            'discount'        => $request->discount,
            'grand_total'     => $request->grand_total,
            'subtotal'        => $request->subtotal,
            'note'            => $request->note,
            'status'          => $request->status,
        ]);

        if (!empty($request->items)) {
            foreach ($request->items as $item) {
                EstimateItem::create([
                    'estimate_id' => $estimate->id,
                    'name'        => $item['name'],
                    'description' => $item['description'] ?? null,
                    'unit_cost'   => $item['cost'],
                    'quantity'    => $item['qty'],
                    'total'       => $item['total'] ?? ($item['cost'] * $item['qty']),
                ]);
            }
        }

        $estimate->load('items');

        return response()->json([
            'message' => __('Estimate has been created'),
            'data'    => $estimate,
        ], 201);
    }

    public function show(Estimate $estimate)
    {
        $estimate->load(['client', 'items']);
        return response()->json(['data' => $estimate]);
    }

    public function update(Request $request, Estimate $estimate)
    {
        $request->validate([
            'client'          => 'required|exists:users,id',
            'billing_address' => 'required|string',
            'startDate'       => 'required|date|before_or_equal:expiryDate',
            'expiryDate'      => 'required|date|after_or_equal:startDate',
        ]);

        $estimate->update([
            'client_id'       => $request->client,
            'project_id'      => $request->project,
            'taxe_id'         => $request->tax,
            'client_address'  => $request->client_address,
            'billing_address' => $request->billing_address,
            'startDate'       => $request->startDate,
            'expiryDate'      => $request->expiryDate,
            'tax_amount'      => $request->taxes_sum,
            'discount'        => $request->discount,
            'grand_total'     => $request->grand_total,
            'subtotal'        => $request->subtotal,
            'note'            => $request->note,
            'status'          => $request->status,
        ]);

        if ($request->has('items')) {
            $items = $request->items;
            EstimateItem::where('estimate_id', $estimate->id)
                ->whereNotIn('id', collect($items)->pluck('id')->filter()->all())
                ->delete();

            foreach ($items as $item) {
                EstimateItem::updateOrCreate(
                    ['id' => $item['id'] ?? null, 'estimate_id' => $estimate->id],
                    [
                        'name'        => $item['name'],
                        'description' => $item['description'] ?? null,
                        'unit_cost'   => $item['cost'],
                        'quantity'    => $item['qty'],
                        'total'       => $item['total'] ?? ($item['cost'] * $item['qty']),
                    ]
                );
            }
        }

        $estimate->load('items');

        return response()->json([
            'message' => __('Estimate has been updated'),
            'data'    => $estimate,
        ]);
    }

    public function destroy(Estimate $estimate)
    {
        $estimate->delete();
        return response()->json(['message' => __('Estimate has been deleted')]);
    }
}
