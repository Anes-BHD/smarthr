<?php

namespace App\Http\Controllers\Api\V1;

use App\Models\User;
use App\Enums\UserType;
use App\Models\Department;
use App\Models\Designation;
use App\Models\EmployeeDetail;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;
use App\Http\Resources\EmployeeResource;
use Illuminate\Support\Facades\Hash;

class EmployeeController extends Controller
{
    /**
     * List all employees with pagination.
     *
     * GET /api/v1/employees
     */
    public function index(Request $request)
    {
        $query = User::where('type', UserType::EMPLOYEE)
            ->with(['employeeDetail.department', 'employeeDetail.designation']);

        if ($request->has('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('firstname', 'LIKE', "%{$search}%")
                  ->orWhere('lastname', 'LIKE', "%{$search}%")
                  ->orWhere('email', 'LIKE', "%{$search}%")
                  ->orWhere('username', 'LIKE', "%{$search}%");
            });
        }

        if ($request->has('status')) {
            $query->where('is_active', $request->boolean('status'));
        }

        $employees = $query->latest()->paginate($request->per_page ?? 15);

        return EmployeeResource::collection($employees);
    }

    /**
     * Create a new employee.
     *
     * POST /api/v1/employees
     */
    public function store(Request $request)
    {
        $request->validate([
            'firstname'   => 'required|string',
            'middlename'  => 'nullable|string',
            'lastname'    => 'required|string',
            'email'       => 'required|email|unique:users,email',
            'password'    => 'required|string|confirmed',
            'username'    => 'nullable|string',
            'address'     => 'nullable|string',
            'country'     => 'nullable|string',
            'country_code'=> 'nullable|string',
            'dial_code'   => 'nullable|string',
            'phone'       => 'nullable|string',
            'status'      => 'required|boolean',
            'department'  => 'nullable|exists:departments,id',
            'designation' => 'nullable|exists:designations,id',
        ]);

        $user = User::create([
            'type'         => UserType::EMPLOYEE,
            'firstname'    => $request->firstname,
            'middlename'   => $request->middlename,
            'lastname'     => $request->lastname,
            'email'        => $request->email,
            'username'     => $request->username,
            'address'      => $request->address,
            'country'      => $request->country,
            'country_code' => $request->country_code,
            'dial_code'    => $request->dial_code,
            'phone'        => $request->phone,
            'created_by'   => auth()->user()->id,
            'is_active'    => $request->status,
            'password'     => Hash::make($request->password),
        ]);

        $user->assignRole(UserType::EMPLOYEE);

        $totalEmployees = User::where('type', UserType::EMPLOYEE)->where('is_active', true)->count();
        $empId = "EMP-" . pad_zeros($totalEmployees + 1);

        EmployeeDetail::create([
            'emp_id'         => $empId,
            'user_id'        => $user->id,
            'department_id'  => $request->department,
            'designation_id' => $request->designation,
        ]);

        $user->load(['employeeDetail.department', 'employeeDetail.designation']);

        return (new EmployeeResource($user))
            ->additional(['message' => __('Employee has been added')])
            ->response()
            ->setStatusCode(201);
    }

    /**
     * Show a specific employee.
     *
     * GET /api/v1/employees/{employee}
     */
    public function show(User $employee)
    {
        $employee->load([
            'employeeDetail.department',
            'employeeDetail.designation',
            'employeeDetail.education',
            'employeeDetail.workExperience',
            'employeeDetail.salaryDetails',
        ]);

        return new EmployeeResource($employee);
    }

    /**
     * Update an employee.
     *
     * PUT /api/v1/employees/{employee}
     */
    public function update(Request $request, User $employee)
    {
        $request->validate([
            'firstname'   => 'required|string',
            'lastname'    => 'required|string',
            'password'    => 'nullable|string|confirmed',
            'status'      => 'required|boolean',
            'department'  => 'nullable|exists:departments,id',
            'designation' => 'nullable|exists:designations,id',
        ]);

        $employee->update([
            'firstname'    => $request->firstname ?? $employee->firstname,
            'middlename'   => $request->middlename ?? $employee->middlename,
            'lastname'     => $request->lastname ?? $employee->lastname,
            'email'        => $request->email ?? $employee->email,
            'username'     => $request->username ?? $employee->username,
            'address'      => $request->address ?? $employee->address,
            'country'      => $request->country ?? $employee->country,
            'country_code' => $request->country_code ?? $employee->country_code,
            'dial_code'    => $request->dial_code ?? $employee->dial_code,
            'phone'        => $request->phone ?? $employee->phone,
            'is_active'    => $request->status ?? $employee->is_active,
            'password'     => !empty($request->password) ? Hash::make($request->password) : $employee->password,
        ]);

        if (!$employee->hasRole(UserType::EMPLOYEE)) {
            $employee->assignRole(UserType::EMPLOYEE);
        }

        EmployeeDetail::updateOrCreate(
            ['user_id' => $employee->id],
            [
                'department_id'  => $request->department,
                'designation_id' => $request->designation,
            ]
        );

        $employee->load(['employeeDetail.department', 'employeeDetail.designation']);

        return (new EmployeeResource($employee))
            ->additional(['message' => __('Employee has been updated')]);
    }

    /**
     * Delete an employee.
     *
     * DELETE /api/v1/employees/{employee}
     */
    public function destroy(User $employee)
    {
        $employee->delete();

        return response()->json([
            'message' => __('Employee has been deleted'),
        ]);
    }
}
