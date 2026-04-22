<?php

namespace Modules\Sales\Http\Controllers\Api;

use Modules\Sales\Models\Invoice;
use Modules\Sales\Models\InvoiceItem;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;

class InvoiceController extends Controller
{
    public function index(Request $request)
    {
        $invoices = Invoice::with(['client', 'items'])
            ->latest()->paginate($request->per_page ?? 15);

        return response()->json(['data' => $invoices]);
    }

    public function store(Request $request)
    {
        $request->validate([
            'client'          => 'required|exists:users,id',
            'billing_address' => 'required|string',
            'startDate'       => 'required|date|before_or_equal:expiryDate',
            'expiryDate'      => 'required|date|after_or_equal:startDate',
            'items'           => 'required|array|min:1',
            'items.*.name'    => 'required|string',
            'items.*.cost'    => 'required|numeric',
            'items.*.qty'     => 'required|integer|min:1',
        ]);

        $invoiceSettings = app(\App\Settings\InvoiceSettings::class);
        $invoice = Invoice::create([
            'inv_id'          => ($invoiceSettings->prefix ?: '#INV-') . pad_zeros(Invoice::count() + 1),
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

        foreach ($request->items as $item) {
            InvoiceItem::create([
                'invoice_id'  => $invoice->id,
                'name'        => $item['name'],
                'description' => $item['description'] ?? null,
                'unit_cost'   => $item['cost'],
                'quantity'    => $item['qty'],
                'total'       => $item['total'] ?? ($item['cost'] * $item['qty']),
            ]);
        }

        $invoice->load('items');

        return response()->json([
            'message' => __('Invoice has been created'),
            'data'    => $invoice,
        ], 201);
    }

    public function show(Invoice $invoice)
    {
        $invoice->load(['client', 'items']);
        return response()->json(['data' => $invoice]);
    }

    public function update(Request $request, Invoice $invoice)
    {
        $request->validate([
            'client'          => 'required|exists:users,id',
            'billing_address' => 'required|string',
            'startDate'       => 'required|date|before_or_equal:expiryDate',
            'expiryDate'      => 'required|date|after_or_equal:startDate',
        ]);

        $invoice->update([
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
            InvoiceItem::where('invoice_id', $invoice->id)
                ->whereNotIn('id', collect($items)->pluck('id')->filter()->all())
                ->delete();

            foreach ($items as $item) {
                InvoiceItem::updateOrCreate(
                    ['id' => $item['id'] ?? null, 'invoice_id' => $invoice->id],
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

        $invoice->load('items');

        return response()->json([
            'message' => __('Invoice has been updated'),
            'data'    => $invoice,
        ]);
    }

    public function destroy(Invoice $invoice)
    {
        $invoice->delete();
        return response()->json(['message' => __('Invoice has been deleted')]);
    }
}
