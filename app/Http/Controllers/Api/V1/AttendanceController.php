<?php

namespace App\Http\Controllers\Api\V1;

use App\Models\User;
use App\Enums\UserType;
use App\Models\Attendance;
use Carbon\CarbonPeriod;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use App\Http\Controllers\Controller;
use App\Http\Resources\AttendanceResource;

class AttendanceController extends Controller
{
    public function index(Request $request)
    {
        $selectedMonth = $request->month ?? Carbon::now()->month;
        $selectedYear = $request->year ?? Carbon::now()->year;

        $query = Attendance::with(['user', 'timestamps'])
            ->whereMonth('created_at', $selectedMonth)
            ->whereYear('created_at', $selectedYear);

        if ($request->has('employee_id')) {
            $query->where('user_id', $request->employee_id);
        }

        $attendances = $query->latest()->paginate($request->per_page ?? 15);

        return AttendanceResource::collection($attendances);
    }

    public function show(Attendance $attendance)
    {
        $attendance->load(['user', 'timestamps']);

        return (new AttendanceResource($attendance))->additional([
            'total_hours' => $attendance->timestamps()->sum('totalHours'),
        ]);
    }
}
