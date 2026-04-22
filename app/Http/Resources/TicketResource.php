<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class TicketResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id'          => $this->id,
            'tk_id'       => $this->tk_id,
            'subject'     => $this->subject,
            'description' => $this->description,
            'status'      => $this->status,
            'priority'    => $this->priority,
            'end_date'    => $this->endDate,
            'created_by'  => $this->when($this->relationLoaded('createdBy'), fn() => [
                'id'        => $this->createdBy?->id,
                'full_name' => $this->createdBy?->full_name,
            ]),
            'assigned_to' => $this->when($this->relationLoaded('user'), fn() => $this->user ? [
                'id'        => $this->user->id,
                'full_name' => $this->user->full_name,
            ] : null),
            'replies_count' => $this->when($this->relationLoaded('replies'), fn() => $this->replies->count()),
            'created_at'    => $this->created_at?->toISOString(),
            'updated_at'    => $this->updated_at?->toISOString(),
        ];
    }
}
