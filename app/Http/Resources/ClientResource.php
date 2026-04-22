<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class ClientResource extends JsonResource
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
            'client_detail' => $this->when($this->relationLoaded('clientDetail') && $this->clientDetail, [
                'clt_id'          => $this->clientDetail?->clt_id,
                'billing_address' => $this->clientDetail?->billing_address,
                'post_address'    => $this->clientDetail?->post_address,
            ]),
            'created_at' => $this->created_at?->toISOString(),
            'updated_at' => $this->updated_at?->toISOString(),
        ];
    }
}
