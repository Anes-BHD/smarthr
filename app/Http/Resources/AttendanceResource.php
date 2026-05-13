<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class AttendanceResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id'         => $this->id,
            'user'       => $this->when($this->relationLoaded('user'), fn() => [
                'id'        => $this->user->id,
                'full_name' => $this->user->full_name,
                'email'     => $this->user->email,
            ]),
            'start_date' => $this->startDate,
            'end_date'   => $this->endDate,
            'timestamps' => $this->when($this->relationLoaded('timestamps'), fn() => 
                $this->timestamps && is_iterable($this->timestamps) 
                    ? $this->timestamps->map(fn($ts) => [
                        'id'          => $ts->id,
                        'start_time'  => $ts->startTime,
                        'end_time'    => $ts->endTime,
                        'created_at'  => $ts->created_at?->toISOString(),
                    ])->toArray()
                    : []
            ),
            'created_at' => $this->created_at?->toISOString(),
            'updated_at' => $this->updated_at?->toISOString(),
        ];
    }
}
