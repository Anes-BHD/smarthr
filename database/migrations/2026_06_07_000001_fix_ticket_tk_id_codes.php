<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        // Step 1: strip leading '#' from every tk_id that has one
        DB::table('tickets')
            ->where('tk_id', 'like', '#%')
            ->update(['tk_id' => DB::raw("SUBSTRING(tk_id, 2)")]);

        // Step 2: find and fix duplicate tk_id values by reassigning from ticket id
        $duplicates = DB::table('tickets')
            ->select('tk_id')
            ->whereNotNull('tk_id')
            ->groupBy('tk_id')
            ->havingRaw('COUNT(*) > 1')
            ->pluck('tk_id');

        foreach ($duplicates as $code) {
            $tickets = DB::table('tickets')
                ->where('tk_id', $code)
                ->orderBy('id')
                ->get(['id']);

            // Keep the first one, reassign the rest using their own id
            foreach ($tickets->skip(1) as $ticket) {
                DB::table('tickets')
                    ->where('id', $ticket->id)
                    ->update(['tk_id' => 'TKT-' . str_pad($ticket->id, 4, '0', STR_PAD_LEFT)]);
            }
        }

        // Step 3: assign a proper code to any ticket that still has null tk_id
        $nullTickets = DB::table('tickets')->whereNull('tk_id')->get(['id']);
        foreach ($nullTickets as $ticket) {
            DB::table('tickets')
                ->where('id', $ticket->id)
                ->update(['tk_id' => 'TKT-' . str_pad($ticket->id, 4, '0', STR_PAD_LEFT)]);
        }
    }

    public function down(): void
    {
        // Irreversible data repair — no rollback needed
    }
};
