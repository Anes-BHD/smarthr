<?php

namespace App\Http\Controllers\Api\V1;

use App\Models\Asset;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;
use App\Http\Resources\AssetResource;

class AssetController extends Controller
{
    public function index(Request $request)
    {
        $query = Asset::with(['user', 'createdBy']);

        if ($request->has('status')) {
            $query->where('status', $request->status);
        }
        if ($request->has('user_id')) {
            $query->where('user_id', $request->user_id);
        }

        $assets = $query->latest()->paginate($request->per_page ?? 15);
        return AssetResource::collection($assets);
    }

    public function store(Request $request)
    {
        $request->validate([
            'name'          => 'required|max:200',
            'purchase_date' => 'required|date',
            'purchase_from' => 'required|string',
            'manufacturer'  => 'required|string',
            'model'         => 'nullable|max:100',
            'serial_no'     => 'nullable|max:50',
            'supplier'      => 'nullable|max:200',
            'condition'     => 'nullable|max:200',
            'warranty'      => 'nullable',
            'cost'          => 'required|numeric',
            'status'        => 'required|string',
            'user_id'       => 'required|exists:users,id',
            'description'   => 'nullable|max:255',
        ]);

        $totalAsset = Asset::count();
        $assetId = "AST-" . pad_zeros($totalAsset + 1);

        $asset = Asset::create([
            'ast_id'        => $request->ast_id ?? $assetId,
            'name'          => $request->name,
            'purchase_date' => $request->purchase_date,
            'purchase_from' => $request->purchase_from,
            'manufacturer'  => $request->manufacturer,
            'model'         => $request->model,
            'serial_no'     => $request->serial_no,
            'supplier'      => $request->supplier,
            'ast_condition' => $request->condition,
            'warranty'      => $request->warranty,
            'warranty_end'  => $request->warranty_end,
            'brand'         => $request->brand,
            'cost'          => $request->cost,
            'description'   => $request->description,
            'status'        => $request->status,
            'user_id'       => $request->user_id,
            'created_by'    => auth()->user()->id,
        ]);

        $asset->load(['user', 'createdBy']);

        return (new AssetResource($asset))
            ->additional(['message' => __('Asset has been added')])
            ->response()->setStatusCode(201);
    }

    public function show(Asset $asset)
    {
        $asset->load(['user', 'createdBy', 'issues']);
        return new AssetResource($asset);
    }

    public function update(Request $request, Asset $asset)
    {
        $request->validate([
            'name'          => 'required|max:200',
            'purchase_date' => 'required|date',
            'purchase_from' => 'required|string',
            'manufacturer'  => 'required|string',
            'cost'          => 'required|numeric',
            'status'        => 'required|string',
            'user_id'       => 'required|exists:users,id',
        ]);

        $asset->update([
            'ast_id'        => $request->ast_id ?? $asset->ast_id,
            'name'          => $request->name,
            'purchase_date' => $request->purchase_date,
            'purchase_from' => $request->purchase_from,
            'manufacturer'  => $request->manufacturer,
            'model'         => $request->model,
            'serial_no'     => $request->serial_no,
            'supplier'      => $request->supplier,
            'ast_condition' => $request->condition,
            'warranty'      => $request->warranty,
            'warranty_end'  => $request->warranty_end,
            'brand'         => $request->brand,
            'cost'          => $request->cost,
            'description'   => $request->description,
            'status'        => $request->status,
            'user_id'       => $request->user_id,
            'created_by'    => auth()->user()->id,
        ]);

        $asset->load(['user', 'createdBy']);

        return (new AssetResource($asset))
            ->additional(['message' => __('Asset has been updated')]);
    }

    public function destroy(Asset $asset)
    {
        $asset->delete();
        return response()->json(['message' => __('Asset has been deleted')]);
    }
}
