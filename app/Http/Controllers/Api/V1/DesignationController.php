<?php

namespace App\Http\Controllers\Api\V1;

use App\Models\Designation;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;
use App\Http\Resources\DesignationResource;

class DesignationController extends Controller
{
    public function index(Request $request)
    {
        $designations = Designation::latest()->paginate($request->per_page ?? 15);
        return DesignationResource::collection($designations);
    }

    public function store(Request $request)
    {
        $request->validate([
            'name'        => 'required|string',
            'description' => 'nullable|string',
        ]);

        $designation = Designation::create([
            'name'        => $request->name,
            'description' => $request->description,
        ]);

        return (new DesignationResource($designation))
            ->additional(['message' => __('Designation has been added')])
            ->response()->setStatusCode(201);
    }

    public function show(Designation $designation)
    {
        return new DesignationResource($designation);
    }

    public function update(Request $request, Designation $designation)
    {
        $request->validate(['name' => 'required|string']);

        $designation->update([
            'name'        => $request->name,
            'description' => $request->description,
        ]);

        return (new DesignationResource($designation))
            ->additional(['message' => __('Designation has been updated')]);
    }

    public function destroy(Designation $designation)
    {
        $designation->delete();
        return response()->json(['message' => __('Designation has been deleted')]);
    }
}
