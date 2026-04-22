<?php

namespace App\Http\Controllers\Api\V1;

use App\Models\User;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;
use App\Http\Resources\UserResource;
use Illuminate\Validation\ValidationException;

class AuthController extends Controller
{
    /**
     * Issue a new API token via email/password credentials.
     *
     * POST /api/v1/auth/login
     */
    public function login(Request $request)
    {
        $request->validate([
            'email'       => 'required|email',
            'password'    => 'required|string',
            'device_name' => 'nullable|string',
        ]);

        $user = User::where('email', $request->email)->first();

        if (! $user || ! Hash::check($request->password, $user->password)) {
            throw ValidationException::withMessages([
                'email' => [__('The provided credentials are incorrect.')],
            ]);
        }

        if (! $user->is_active) {
            throw ValidationException::withMessages([
                'email' => [__('Your account is disabled.')],
            ]);
        }

        $deviceName = $request->device_name ?? 'api-token';
        $token = $user->createToken($deviceName)->plainTextToken;

        return response()->json([
            'message' => __('Login successful'),
            'user'    => new UserResource($user),
            'token'   => $token,
        ]);
    }

    /**
     * Revoke the current API token.
     *
     * POST /api/v1/auth/logout
     */
    public function logout(Request $request)
    {
        $request->user()->currentAccessToken()->delete();

        return response()->json([
            'message' => __('Logged out successfully'),
        ]);
    }

    /**
     * Return the authenticated user.
     *
     * GET /api/v1/auth/me
     */
    public function me(Request $request)
    {
        $user = $request->user()->load(['employeeDetail', 'clientDetail']);

        return response()->json([
            'user' => new UserResource($user),
        ]);
    }
}
