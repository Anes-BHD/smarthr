<?php

namespace App\Http\Controllers\Api\V1;

use App\Enums\UserType;
use App\Http\Controllers\Controller;
use App\Models\Attendance;
use App\Models\LeaveRequest;
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
            'start_date'  => 'nullable|date',
            'end_date'    => 'nullable|date',
            'employee_id' => 'nullable|integer|exists:users,id',
            'status'      => 'nullable|string',
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
            ->when($request->filled('employee_id'), fn ($q) => $q->where('id', $request->employee_id))
            ->with(['employeeDetail.department'])
            ->get();

        // Pre-load approved leave requests covering this period
        $approvedLeaves = LeaveRequest::where('status', 'approved')
            ->when($request->filled('employee_id'), fn ($q) => $q->where('user_id', $request->employee_id))
            ->where('start_date', '<=', $endDate->toDateString())
            ->where('end_date', '>=', $startDate->toDateString())
            ->get()
            ->groupBy('user_id');

        $absences = [];
        $seen = [];  // deduplicate: employee+day already covered by a leave record

        // 1. Approved leave requests (richer reason/type data)
        foreach ($employees as $employee) {
            $leaves = $approvedLeaves->get($employee->id, collect());
            foreach ($leaves as $leave) {
                $leaveStart = Carbon::parse($leave->start_date)->max($startDate);
                $leaveEnd   = Carbon::parse($leave->end_date)->min($endDate);
                foreach (CarbonPeriod::create($leaveStart, $leaveEnd) as $day) {
                    $key = $employee->id . '-' . $day->toDateString();
                    $seen[$key] = true;
                    $absences[] = [
                        'id'            => $key,
                        'employee_id'   => $employee->id,
                        'employee_name' => trim($employee->firstname . ' ' . $employee->lastname),
                        'department'    => $employee->employeeDetail?->department?->name,
                        'start_date'    => $day->toDateString(),
                        'end_date'      => $day->toDateString(),
                        'days_count'    => 1,
                        'reason'        => $leave->reason ?? ucfirst($leave->type) . ' leave',
                        'status'        => 'absent',
                        'leave_type'    => $leave->type,
                    ];
                }
            }
        }

        // 2. Unexcused absences (no attendance AND no approved leave)
        foreach ($employees as $employee) {
            foreach (CarbonPeriod::create($startDate, $endDate) as $day) {
                $key = $employee->id . '-' . $day->toDateString();
                if (isset($seen[$key])) {
                    continue;
                }

                $hasAttendance = Attendance::where('user_id', $employee->id)
                    ->whereDate('startDate', '<=', $day)
                    ->whereDate('endDate', '>=', $day)
                    ->exists();

                if ($hasAttendance) {
                    continue;
                }

                $absences[] = [
                    'id'            => $key,
                    'employee_id'   => $employee->id,
                    'employee_name' => trim($employee->firstname . ' ' . $employee->lastname),
                    'department'    => $employee->employeeDetail?->department?->name,
                    'start_date'    => $day->toDateString(),
                    'end_date'      => $day->toDateString(),
                    'days_count'    => 1,
                    'reason'        => 'Absence',
                    'status'        => 'absent',
                    'leave_type'    => null,
                ];
            }
        }

        return response()->json(['data' => $absences]);
    }
}
