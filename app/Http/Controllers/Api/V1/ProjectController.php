<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\Request;
use Modules\Project\Models\Project;

class ProjectController extends Controller
{
    /**
     * List projects for API consumers.
     *
     * GET /api/v1/projects
     */
    public function index(Request $request)
    {
        $query = Project::with(['client', 'leader', 'team.user']);

        if ($request->filled('search')) {
            $search = $request->search;
            $query->where('name', 'LIKE', "%{$search}%");
        }

        if ($request->filled('priority')) {
            $query->where('priority', $request->priority);
        }

        $projects = $query->latest()->get()->map(function (Project $project) {
            return [
                'id' => $project->id,
                'name' => $project->name,
                'client' => $this->userName($project->client),
                'client_id' => $project->client_id,
                'start_date' => $project->startDate,
                'end_date' => $project->endDate,
                'deadline' => $project->endDate,
                'priority' => $project->priority,
                'rate' => $project->rate,
                'rate_type' => $project->rateType,
                'project_leader' => $this->userName($project->leader),
                'leader_id' => $project->leader_id,
                'team' => $project->team->map(function ($member) {
                    return [
                        'id' => $member->user_id,
                        'name' => $this->userName($member->user),
                        'email' => optional($member->user)->email,
                    ];
                })->values(),
                'description' => $project->description ?: $project->short_desc,
                'short_desc' => $project->short_desc,
            ];
        })->values();

        return response()->json([
            'data' => $projects,
        ]);
    }

    private function userName(?User $user): ?string
    {
        if (!$user) {
            return null;
        }

        return trim("{$user->firstname} {$user->middlename} {$user->lastname}") ?: $user->email;
    }
}
