<?php

namespace App\Http\Controllers\Api\V1;

use App\Models\Department;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;
use App\Http\Resources\DepartmentResource;

class DepartmentController extends Controller
{
    /**
     * List all departments.
     *
     * GET /api/v1/departments
     */
    public function index(Request $request)
    {
        $departments = Department::latest()->paginate($request->per_page ?? 15);

        return DepartmentResource::collection($departments);
    }

    /**
     * Create a new department.
     *
     * POST /api/v1/departments
     */
    public function store(Request $request)
    {
        $request->validate([
            'name'        => 'required|string',
            'location'    => 'nullable|string',
            'description' => 'nullable|max:255',
            'parent_department_id' => 'nullable|exists:departments,id',
        ]);

        $department = Department::create([
            'name'                 => $request->name,
            'parent_department_id' => $request->parent_department_id,
            'location'             => $request->location,
            'description'          => $request->description,
        ]);

        return (new DepartmentResource($department))
            ->additional(['message' => __('Department has been added')])
            ->response()
            ->setStatusCode(201);
    }

    /**
     * Show a specific department.
     *
     * GET /api/v1/departments/{department}
     */
    public function show(Department $department)
    {
        return new DepartmentResource($department);
    }

    /**
     * Update a department.
     *
     * PUT /api/v1/departments/{department}
     */
    public function update(Request $request, Department $department)
    {
        $request->validate([
            'name'        => 'required|string',
            'description' => 'nullable|max:255',
        ]);

        $department->update([
            'name'                 => $request->name,
            'parent_department_id' => $request->parent_department_id,
            'location'             => $request->location,
            'description'          => $request->description,
        ]);

        return (new DepartmentResource($department))
            ->additional(['message' => __('Department has been updated')]);
    }

    /**
     * Delete a department.
     *
     * DELETE /api/v1/departments/{department}
     */
    public function destroy(Department $department)
    {
        $department->delete();

        return response()->json([
            'message' => __('Department has been deleted'),
        ]);
    }
}
