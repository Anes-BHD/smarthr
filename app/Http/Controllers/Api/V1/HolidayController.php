<?php

namespace App\Http\Controllers\Api\V1;

use App\Models\Holiday;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;
use App\Http\Resources\HolidayResource;

class HolidayController extends Controller
{
    public function index(Request $request)
    {
        $holidays = Holiday::latest()->paginate($request->per_page ?? 15);
        return HolidayResource::collection($holidays);
    }

    public function store(Request $request)
    {
        $request->validate([
            'name'        => 'required|string',
            'startDate'   => 'required|date',
            'endDate'     => 'required|date',
            'description' => 'nullable|max:255',
            'is_annual'   => 'nullable|boolean',
            'color'       => 'nullable|string',
        ]);

        $holiday = Holiday::create([
            'name'        => $request->name,
            'startDate'   => $request->startDate,
            'endDate'     => $request->endDate,
            'description' => $request->description,
            'is_annual'   => $request->boolean('is_annual'),
            'color'       => $request->color,
        ]);

        return (new HolidayResource($holiday))
            ->additional(['message' => __('Holiday has been created')])
            ->response()->setStatusCode(201);
    }

    public function show(Holiday $holiday)
    {
        return new HolidayResource($holiday);
    }

    public function update(Request $request, Holiday $holiday)
    {
        $request->validate([
            'name'        => 'required|string',
            'startDate'   => 'required|date',
            'endDate'     => 'required|date',
            'description' => 'nullable|max:255',
        ]);

        $holiday->update([
            'name'        => $request->name,
            'startDate'   => $request->startDate,
            'endDate'     => $request->endDate,
            'description' => $request->description,
            'is_annual'   => $request->boolean('is_annual'),
            'color'       => $request->color,
        ]);

        return (new HolidayResource($holiday))
            ->additional(['message' => __('Holiday has been updated')]);
    }

    public function destroy(Holiday $holiday)
    {
        $holiday->delete();
        return response()->json(['message' => __('Holiday has been deleted')]);
    }
}
