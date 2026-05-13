<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class EmployeeResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id'           => $this->id,
            'firstname'    => $this->firstname,
            'middlename'   => $this->middlename,
            'lastname'     => $this->lastname,
            'full_name'    => $this->full_name,
            'email'        => $this->email,
            'username'     => $this->username,
            'address'      => $this->address,
            'country'      => $this->country,
            'phone'        => $this->phone_number,
            'avatar'       => $this->avatar,
            'is_active'    => (bool) $this->is_active,
            'employee_detail' => $this->when($this->relationLoaded('employeeDetail') && $this->employeeDetail, [
                'emp_id'         => $this->employeeDetail?->emp_id,
                'department'     => $this->when(
                    $this->employeeDetail?->relationLoaded('department'),
                    fn() => new DepartmentResource($this->employeeDetail->department)
                ),
                'designation'    => $this->when(
                    $this->employeeDetail?->relationLoaded('designation'),
                    fn() => new DesignationResource($this->employeeDetail->designation)
                ),
                'date_joined'    => $this->employeeDetail?->date_joined?->toISOString(),
                'nationality'    => $this->employeeDetail?->nationality,
                'marital_status' => $this->employeeDetail?->marital_status,
            ]),
            'created_at' => $this->created_at?->toISOString(),
            'updated_at' => $this->updated_at?->toISOString(),
        ];
    }
}
