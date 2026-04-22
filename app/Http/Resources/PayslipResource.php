<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class PayslipResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id'             => $this->id,
            'ps_id'          => $this->ps_id,
            'title'          => $this->title,
            'type'           => $this->type,
            'payslip_date'   => $this->payslip_date,
            'start_date'     => $this->startDate,
            'end_date'       => $this->endDate,
            'total_hours'    => $this->total_hours,
            'weeks'          => $this->weeks,
            'net_pay'        => $this->net_pay,
            'use_allowance'  => (bool) $this->use_allowance,
            'use_deduction'  => (bool) $this->use_deduction,
            'employee'       => $this->when($this->relationLoaded('employee'), fn() => [
                'id'        => $this->employee->id,
                'emp_id'    => $this->employee->emp_id,
                'user'      => $this->when($this->employee->relationLoaded('user'), fn() => [
                    'id'        => $this->employee->user->id,
                    'full_name' => $this->employee->user->full_name,
                    'email'     => $this->employee->user->email,
                ]),
            ]),
            'created_at' => $this->created_at?->toISOString(),
            'updated_at' => $this->updated_at?->toISOString(),
        ];
    }
}
