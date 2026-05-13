<?php

namespace App\Http\Controllers\Api\V1;

use App\Models\Ticket;
use App\Enums\TicketStatus;
use App\Enums\GeneralPriority;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;
use App\Http\Resources\TicketResource;

class TicketController extends Controller
{
    public function index(Request $request)
    {
        $query = Ticket::with(['user', 'createdBy']);

        if ($request->has('status')) {
            $query->where('status', $request->status);
        }
        if ($request->has('priority')) {
            $query->where('priority', $request->priority);
        }

        $tickets = $query->latest()->paginate($request->per_page ?? 15);
        return TicketResource::collection($tickets);
    }

    public function store(Request $request)
    {
        $request->validate([
            'subject'     => 'required|string',
            'description' => 'required|string',
            'status'      => 'nullable|string',
            'priority'    => 'nullable|string',
            'user_id'     => 'nullable|exists:users,id',
            'endDate'     => 'nullable|date',
        ]);

        $ticket = Ticket::create([
            'tk_id'       => $request->tk_id ?? '#TKT-' . pad_zeros(Ticket::count() + 1),
            'subject'     => $request->subject,
            'created_by'  => auth()->user()->id,
            'user_id'     => $request->user_id,
            'description' => $request->description,
            'status'      => $request->status ?? TicketStatus::NEW,
            'priority'    => $request->priority ?? GeneralPriority::MEDIUM,
            'endDate'     => $request->endDate,
        ]);

        $ticket->load(['user', 'createdBy']);

        return (new TicketResource($ticket))
            ->additional(['message' => __('Ticket has been added')])
            ->response()->setStatusCode(201);
    }

    public function show(Ticket $ticket)
    {
        $ticket->load(['user', 'createdBy', 'replies']);
        return new TicketResource($ticket);
    }

    public function update(Request $request, Ticket $ticket)
    {
        $request->validate([
            'subject'     => 'required|string',
            'description' => 'required|string',
        ]);

        $ticket->update([
            'subject'     => $request->subject,
            'user_id'     => $request->user_id,
            'description' => $request->description,
            'status'      => $request->status ?? $ticket->status,
            'priority'    => $request->priority ?? $ticket->priority,
            'endDate'     => $request->endDate,
        ]);

        $ticket->load(['user', 'createdBy']);

        return (new TicketResource($ticket))
            ->additional(['message' => __('Ticket has been updated')]);
    }

    public function destroy(Ticket $ticket)
    {
        $ticket->delete();
        return response()->json(['message' => __('Ticket has been deleted')]);
    }
}
