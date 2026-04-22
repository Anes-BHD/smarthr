<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class UserResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id'           => $this->id,
            'type'         => $this->type,
            'firstname'    => $this->firstname,
            'middlename'   => $this->middlename,
            'lastname'     => $this->lastname,
            'full_name'    => $this->full_name,
            'email'        => $this->email,
            'username'     => $this->username,
            'address'      => $this->address,
            'country'      => $this->country,
            'country_code' => $this->country_code,
            'dial_code'    => $this->dial_code,
            'phone'        => $this->phone,
            'phone_number' => $this->phone_number,
            'avatar'       => $this->avatar,
            'is_active'    => (bool) $this->is_active,
            'is_online'    => (bool) $this->is_online,
            'roles'        => $this->whenLoaded('roles', fn() => $this->roles->pluck('name')),
            'created_at'   => $this->created_at?->toISOString(),
            'updated_at'   => $this->updated_at?->toISOString(),
        ];
    }
}
