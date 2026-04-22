<?php

namespace App\Http\Controllers\Api\V1;

use App\Models\User;
use App\Enums\UserType;
use Illuminate\Http\Request;
use Spatie\Permission\Models\Role;
use App\Http\Controllers\Controller;
use App\Http\Resources\UserResource;
use Illuminate\Support\Facades\Hash;

class UserController extends Controller
{
    public function index(Request $request)
    {
        $users = User::where('type', UserType::SUPERADMIN)
            ->latest()->paginate($request->per_page ?? 15);

        return UserResource::collection($users);
    }

    public function store(Request $request)
    {
        $request->validate([
            'firstname' => 'required|string',
            'middlename'=> 'nullable|string',
            'lastname'  => 'required|string',
            'email'     => 'required|email|unique:users,email',
            'password'  => 'required|string|confirmed',
            'status'    => 'required|boolean',
            'role'      => 'nullable|string|exists:roles,name',
        ]);

        $user = User::create([
            'type'         => UserType::SUPERADMIN,
            'firstname'    => $request->firstname,
            'middlename'   => $request->middlename,
            'lastname'     => $request->lastname,
            'email'        => $request->email,
            'username'     => $request->username,
            'address'      => $request->address,
            'country'      => $request->country,
            'country_code' => $request->country_code,
            'dial_code'    => $request->dial_code,
            'phone'        => $request->phone,
            'created_by'   => auth()->user()->id,
            'is_active'    => $request->status,
            'password'     => Hash::make($request->password),
        ]);

        if ($request->filled('role')) {
            $user->assignRole($request->role);
        }

        return (new UserResource($user))
            ->additional(['message' => __('User has been created')])
            ->response()->setStatusCode(201);
    }

    public function show(User $user)
    {
        $user->load('roles');
        return new UserResource($user);
    }

    public function update(Request $request, User $user)
    {
        $request->validate([
            'firstname' => 'required|string',
            'lastname'  => 'required|string',
            'password'  => 'nullable|string|confirmed',
            'status'    => 'required|boolean',
            'role'      => 'nullable|string|exists:roles,name',
        ]);

        $user->update([
            'firstname'    => $request->firstname ?? $user->firstname,
            'middlename'   => $request->middlename ?? $user->middlename,
            'lastname'     => $request->lastname ?? $user->lastname,
            'email'        => $request->email ?? $user->email,
            'username'     => $request->username ?? $user->username,
            'address'      => $request->address ?? $user->address,
            'country'      => $request->country ?? $user->country,
            'country_code' => $request->country_code ?? $user->country_code,
            'dial_code'    => $request->dial_code ?? $user->dial_code,
            'phone'        => $request->phone ?? $user->phone,
            'is_active'    => $request->status ?? $user->is_active,
            'password'     => !empty($request->password) ? Hash::make($request->password) : $user->password,
        ]);

        if ($request->filled('role')) {
            $user->syncRoles($request->role);
        }

        return (new UserResource($user))
            ->additional(['message' => __('User has been updated')]);
    }

    public function destroy(User $user)
    {
        $user->delete();
        return response()->json(['message' => __('User has been deleted')]);
    }
}
