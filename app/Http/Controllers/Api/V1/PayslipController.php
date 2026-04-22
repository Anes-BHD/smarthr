<?php

namespace App\Http\Controllers\Api\V1;

use App\Models\Payslip;
use App\Models\PayslipItem;
use App\Models\EmployeeDetail;
use App\Models\EmployeeAllowance;
use App\Models\EmployeeDeduction;
use App\Models\AttendanceTimestamp;
use App\Enums\Payroll\SalaryType;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use App\Http\Controllers\Controller;
use App\Http\Resources\PayslipResource;

class PayslipController extends Controller
{
    public function index(Request $request)
    {
        $payslips = Payslip::with('employee.user')
            ->latest()->paginate($request->per_page ?? 15);

        return PayslipResource::collection($payslips);
    }

    public function store(Request $request)
    {
        $request->validate([
            'employee'     => 'required|exists:employee_details,id',
            'type'         => 'required|string',
            'payslip_date' => 'nullable|date',
            'title'        => 'required_if:type,contract',
            'from_date'    => 'required_if:type,hourly',
            'to_date'      => 'nullable|date',
            'weeks'        => 'required_if:type,weekly',
        ]);

        $employee = EmployeeDetail::findOrFail($request->employee);
        $salaryInfo = $employee->salaryDetails;
        $deductions = 0;
        $allowances = 0;
        $total_hours = 0;
        $allowancesItems = null;
        $deductionItems = null;

        if (!empty($request->use_allowance)) {
            $allowancesItems = EmployeeAllowance::where('employee_detail_id', $employee->id)->get();
            $allowances = $allowancesItems->sum('amount');
        }
        if (!empty($request->use_deductions)) {
            $deductionItems = EmployeeDeduction::where('employee_detail_id', $employee->id)->get();
            $deductions = $deductionItems->sum('amount');
        }

        $net_pay = ($salaryInfo->base_salary + $allowances) - $deductions;

        if ($request->type === SalaryType::Hourly) {
            $total_hours = AttendanceTimestamp::where('user_id', $employee->user_id)
                ->whereBetween('created_at', [Carbon::parse($request->from_date), Carbon::parse($request->to_date)])
                ->whereNotNull(['attendance_id', 'startTime', 'endTime'])
                ->sum('totalHours');
            $net_pay = (($total_hours * $salaryInfo->base_salary) + $allowances) - $deductions;
        }
        if ($request->type === SalaryType::Weekly) {
            $net_pay = (($request->weeks * $salaryInfo->base_salary) + $allowances) - $deductions;
        }

        $payslip = Payslip::create([
            'ps_id'              => pad_zeros(Payslip::count() + 1),
            'title'              => $request->title,
            'employee_detail_id' => $employee->id,
            'use_allowance'      => !empty($request->use_allowance),
            'use_deduction'      => !empty($request->use_deductions),
            'payslip_date'       => $request->payslip_date,
            'type'               => $request->type,
            'startDate'          => $request->from_date,
            'endDate'            => $request->to_date,
            'total_hours'        => $total_hours,
            'weeks'              => $request->weeks,
            'net_pay'            => $net_pay,
        ]);

        if (!empty($allowancesItems)) {
            PayslipItem::insert($allowancesItems->map(fn(EmployeeAllowance $item) => [
                'type'       => 'allowance',
                'payslip_id' => $payslip->id,
                'item_id'    => $item->id,
            ])->all());
        }
        if (!empty($deductionItems)) {
            PayslipItem::insert($deductionItems->map(fn(EmployeeDeduction $item) => [
                'type'       => 'deduction',
                'payslip_id' => $payslip->id,
                'item_id'    => $item->id,
            ])->all());
        }

        $payslip->load('employee.user');

        return (new PayslipResource($payslip))
            ->additional(['message' => __('Payslip has been created')])
            ->response()->setStatusCode(201);
    }

    public function show(Payslip $payslip)
    {
        $payslip->load(['employee.user', 'items']);

        return new PayslipResource($payslip);
    }

    public function update(Request $request, Payslip $payslip)
    {
        $request->validate([
            'employee'     => 'required|exists:employee_details,id',
            'type'         => 'required|string',
            'payslip_date' => 'nullable|date',
            'title'        => 'required_if:type,contract',
            'from_date'    => 'required_if:type,hourly',
            'weeks'        => 'required_if:type,weekly',
        ]);

        $employee = EmployeeDetail::findOrFail($request->employee);
        $salaryInfo = $employee->salaryDetails;
        $deductions = 0;
        $allowances = 0;
        $total_hours = 0;

        if (!empty($request->use_allowance)) {
            $allowances = EmployeeAllowance::where('employee_detail_id', $employee->id)->sum('amount');
        }
        if (!empty($request->use_deductions)) {
            $deductions = EmployeeDeduction::where('employee_detail_id', $employee->id)->sum('amount');
        }

        $net_pay = ($salaryInfo->base_salary + $allowances) - $deductions;

        if ($request->type === SalaryType::Hourly) {
            $total_hours = AttendanceTimestamp::where('user_id', $employee->user_id)
                ->whereBetween('created_at', [Carbon::parse($request->from_date), Carbon::parse($request->to_date)])
                ->whereNotNull(['attendance_id', 'startTime', 'endTime'])
                ->sum('totalHours');
            $net_pay = (($total_hours * $salaryInfo->base_salary) + $allowances) - $deductions;
        }
        if ($request->type === SalaryType::Weekly) {
            $net_pay = (($request->weeks * $salaryInfo->base_salary) + $allowances) - $deductions;
        }

        $payslip->update([
            'title'              => $request->title,
            'employee_detail_id' => $employee->id,
            'use_allowance'      => !empty($request->use_allowance),
            'use_deduction'      => !empty($request->use_deductions),
            'payslip_date'       => $request->payslip_date,
            'type'               => $request->type,
            'startDate'          => $request->from_date,
            'endDate'            => $request->to_date,
            'total_hours'        => $total_hours,
            'weeks'              => $request->weeks,
            'net_pay'            => $net_pay,
        ]);

        $payslip->load('employee.user');

        return (new PayslipResource($payslip))
            ->additional(['message' => __('Payslip has been updated')]);
    }

    public function destroy(Payslip $payslip)
    {
        $payslip->delete();
        return response()->json(['message' => __('Payslip has been deleted')]);
    }
}
