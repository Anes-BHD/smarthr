<?php

namespace App\Http\Controllers\Api\V1;

use App\Enums\UserType;
use App\Http\Controllers\Controller;
use App\Models\Attendance;
use App\Models\User;
use Carbon\Carbon;
use Carbon\CarbonPeriod;
use Illuminate\Http\Request;

class AbsenceController extends Controller
{
    /**
     * GET /api/v1/absences
     */
    public function index(Request $request)
    {
        $request->validate([
            'start_date' => 'nullable|date',
            'end_date' => 'nullable|date',
            'employee_id' => 'nullable|integer|exists:users,id',
            'status' => 'nullable|string',
        ]);

        if ($request->filled('status') && strtolower($request->status) !== 'absent') {
            return response()->json(['data' => []]);
        }

        $startDate = $request->filled('start_date')
            ? Carbon::parse($request->start_date)->startOfDay()
            : Carbon::today();

        $endDate = $request->filled('end_date')
            ? Carbon::parse($request->end_date)->startOfDay()
            : $startDate->copy();

        if ($endDate->lt($startDate)) {
            return response()->json([
                'message' => 'The end_date must be after or equal to start_date.',
            ], 422);
        }

        $employees = User::where('type', UserType::EMPLOYEE)
            ->when($request->filled('employee_id'), function ($query) use ($request) {
                $query->where('id', $request->employee_id);
            })
            ->with(['employeeDetail.department'])
            ->get();

        $absences = [];

        foreach ($employees as $employee) {
            foreach (CarbonPeriod::create($startDate, $endDate) as $day) {
                $hasAttendance = Attendance::where('user_id', $employee->id)
                    ->whereDate('startDate', '<=', $day)
                    ->whereDate('endDate', '>=', $day)
                    ->exists();

                if ($hasAttendance) {
                    continue;
                }

                $absences[] = [
                    'id' => $employee->id . '-' . $day->toDateString(),
                    'employee_id' => $employee->id,
                    'employee_name' => trim($employee->firstname . ' ' . $employee->lastname),
                    'department' => $employee->employeeDetail?->department?->name,
                    'start_date' => $day->toDateString(),
                    'end_date' => $day->toDateString(),
                    'days_count' => 1,
                    'reason' => 'Absence',
                    'status' => 'absent',
                ];
            }
        }

        return response()->json(['data' => $absences]);
    }
}
