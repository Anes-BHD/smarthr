<?php

namespace App\Http\Controllers\Api\V1;

use App\Models\User;
use App\Enums\UserType;
use App\Models\ClientDetail;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;
use App\Http\Resources\ClientResource;
use Illuminate\Support\Facades\Hash;

class ClientController extends Controller
{
    /**
     * List all clients with pagination.
     *
     * GET /api/v1/clients
     */
    public function index(Request $request)
    {
        $query = User::where('type', UserType::CLIENT)
            ->with(['clientDetail']);

        if ($request->has('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('firstname', 'LIKE', "%{$search}%")
                  ->orWhere('lastname', 'LIKE', "%{$search}%")
                  ->orWhere('email', 'LIKE', "%{$search}%");
            });
        }

        $clients = $query->latest()->paginate($request->per_page ?? 15);

        return ClientResource::collection($clients);
    }

    /**
     * Create a new client.
     *
     * POST /api/v1/clients
     */
    public function store(Request $request)
    {
        $request->validate([
            'firstname'   => 'required|string',
            'middlename'  => 'nullable|string',
            'lastname'    => 'required|string',
            'email'       => 'required|email|unique:users,email',
            'password'    => 'required|string|confirmed',
            'username'    => 'nullable|string',
            'address'     => 'nullable|string',
            'country'     => 'nullable|string',
            'country_code'=> 'nullable|string',
            'dial_code'   => 'nullable|string',
            'phone'       => 'nullable|string',
            'status'      => 'required|boolean',
        ]);

        $user = User::create([
            'type'         => UserType::CLIENT,
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

        $user->assignRole(UserType::CLIENT);

        $totalClients = User::where('type', UserType::CLIENT)->where('is_active', true)->count();
        $cltId = "CLT-" . pad_zeros($totalClients + 1);

        ClientDetail::create([
            'clt_id'  => $cltId,
            'user_id' => $user->id,
        ]);

        $user->load('clientDetail');

        return (new ClientResource($user))
            ->additional(['message' => __('Client has been created')])
            ->response()
            ->setStatusCode(201);
    }

    /**
     * Show a specific client.
     *
     * GET /api/v1/clients/{client}
     */
    public function show(User $client)
    {
        $client->load('clientDetail');

        return new ClientResource($client);
    }

    /**
     * Update a client.
     *
     * PUT /api/v1/clients/{client}
     */
    public function update(Request $request, User $client)
    {
        $request->validate([
            'firstname' => 'required|string',
            'lastname'  => 'required|string',
            'password'  => 'nullable|string|confirmed',
            'status'    => 'required|boolean',
        ]);

        $client->update([
            'firstname'    => $request->firstname ?? $client->firstname,
            'middlename'   => $request->middlename ?? $client->middlename,
            'lastname'     => $request->lastname ?? $client->lastname,
            'email'        => $request->email ?? $client->email,
            'username'     => $request->username ?? $client->username,
            'address'      => $request->address ?? $client->address,
            'country'      => $request->country ?? $client->country,
            'country_code' => $request->country_code ?? $client->country_code,
            'dial_code'    => $request->dial_code ?? $client->dial_code,
            'phone'        => $request->phone ?? $client->phone,
            'is_active'    => $request->status ?? $client->is_active,
            'password'     => !empty($request->password) ? Hash::make($request->password) : $client->password,
        ]);

        if (!$client->hasRole(UserType::CLIENT)) {
            $client->assignRole(UserType::CLIENT);
        }

        $client->load('clientDetail');

        return (new ClientResource($client))
            ->additional(['message' => __('Client has been updated')]);
    }

    /**
     * Delete a client.
     *
     * DELETE /api/v1/clients/{client}
     */
    public function destroy(User $client)
    {
        $client->delete();

        return response()->json([
            'message' => __('Client has been deleted'),
        ]);
    }
}
