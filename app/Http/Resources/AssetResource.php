<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class AssetResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id'            => $this->id,
            'ast_id'        => $this->ast_id,
            'name'          => $this->name,
            'purchase_date' => $this->purchase_date,
            'purchase_from' => $this->purchase_from,
            'manufacturer'  => $this->manufacturer,
            'model'         => $this->model,
            'serial_no'     => $this->serial_no,
            'supplier'      => $this->supplier,
            'condition'     => $this->ast_condition,
            'warranty'      => $this->warranty,
            'warranty_end'  => $this->warranty_end,
            'brand'         => $this->brand,
            'cost'          => $this->cost,
            'description'   => $this->description,
            'status'        => $this->status,
            'assigned_to'   => $this->when($this->relationLoaded('user'), fn() => $this->user ? [
                'id'        => $this->user->id,
                'full_name' => $this->user->full_name,
            ] : null),
            'created_by'    => $this->when($this->relationLoaded('createdBy'), fn() => $this->createdBy ? [
                'id'        => $this->createdBy->id,
                'full_name' => $this->createdBy->full_name,
            ] : null),
            'created_at'    => $this->created_at?->toISOString(),
            'updated_at'    => $this->updated_at?->toISOString(),
        ];
    }
}
