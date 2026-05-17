<?php

namespace Database\Seeders;

use App\Enums\MaritalStatus;
use App\Enums\UserType;
use App\Models\Attendance;
use App\Models\Department;
use App\Models\Designation;
use App\Models\EmployeeDetail;
use App\Models\EmployeeSalaryDetail;
use App\Models\LeaveRequest;
use App\Models\Ticket;
use App\Models\User;
use Carbon\Carbon;
use Carbon\CarbonPeriod;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;
use Modules\Project\Models\Project;
use Modules\Project\Models\ProjectLead;
use Modules\Project\Models\ProjectTeam;
use Spatie\Permission\Models\Role;

class SmartHRDemoSeeder extends Seeder
{
    private User $admin;

    public function run(): void
    {
        $this->ensureRoles();
        $this->admin = User::where('type', UserType::SUPERADMIN)->first()
            ?? User::where('email', 'superadmin@smarthr.com')->first();

        $departments  = $this->seedDepartments();
        $designations = $this->seedDesignations();
        $employees    = $this->seedEmployees($departments, $designations);

        $this->seedAttendance($employees);
        $this->seedLeaveRequests($employees);
        $this->seedTickets($employees);
        $this->seedProjects($employees);
    }

    // ── Departments ────────────────────────────────────────────────────────────

    private function seedDepartments(): array
    {
        $depts = [
            ['name' => 'Engineering',       'location' => 'Tunis'],
            ['name' => 'Human Resources',   'location' => 'Tunis'],
            ['name' => 'Finance',           'location' => 'Tunis'],
            ['name' => 'Marketing',         'location' => 'Sfax'],
            ['name' => 'Operations',        'location' => 'Tunis'],
            ['name' => 'Sales',             'location' => 'Sousse'],
            ['name' => 'IT',                'location' => 'Tunis'],
            ['name' => 'Legal',             'location' => 'Tunis'],
        ];

        $result = [];
        foreach ($depts as $d) {
            $result[] = Department::firstOrCreate(['name' => $d['name']], ['location' => $d['location']]);
        }
        return $result;
    }

    // ── Designations ───────────────────────────────────────────────────────────

    private function seedDesignations(): array
    {
        $desigs = [
            'Software Engineer', 'Senior Software Engineer', 'Tech Lead',
            'DevOps Engineer', 'Data Analyst', 'Product Manager',
            'HR Manager', 'HR Specialist', 'Recruiter',
            'Financial Analyst', 'Accountant', 'CFO',
            'Marketing Manager', 'Content Creator', 'SEO Specialist',
            'Operations Manager', 'Sales Executive', 'Sales Manager',
            'IT Support', 'Network Engineer', 'Legal Advisor',
        ];

        $result = [];
        foreach ($desigs as $name) {
            $result[] = Designation::firstOrCreate(['name' => $name]);
        }
        return $result;
    }

    // ── Employees ──────────────────────────────────────────────────────────────

    private function seedEmployees(array $departments, array $designations): array
    {
        $profiles = [
            // Engineering
            ['firstname' => 'Ahmed',    'lastname' => 'Ben Ali',     'email' => 'ahmed.benali@smarthr.com',     'dept' => 'Engineering',     'desig' => 'Software Engineer'],
            ['firstname' => 'Sarra',    'lastname' => 'Mansour',     'email' => 'sarra.mansour@smarthr.com',    'dept' => 'Engineering',     'desig' => 'Senior Software Engineer'],
            ['firstname' => 'Oussama',  'lastname' => 'Trabelsi',    'email' => 'oussama.trabelsi@smarthr.com', 'dept' => 'Engineering',     'desig' => 'Tech Lead'],
            ['firstname' => 'Rania',    'lastname' => 'Chaabane',    'email' => 'rania.chaabane@smarthr.com',   'dept' => 'Engineering',     'desig' => 'DevOps Engineer'],
            // IT
            ['firstname' => 'Sedki',    'lastname' => 'Hamdi',       'email' => 'sedki.hamdi@smarthr.com',      'dept' => 'IT',              'desig' => 'IT Support'],
            ['firstname' => 'Ines',     'lastname' => 'Jebali',      'email' => 'ines.jebali@smarthr.com',      'dept' => 'IT',              'desig' => 'Network Engineer'],
            // HR
            ['firstname' => 'Nadia',    'lastname' => 'Belhadj',     'email' => 'nadia.belhadj@smarthr.com',    'dept' => 'Human Resources', 'desig' => 'HR Manager'],
            ['firstname' => 'Khaled',   'lastname' => 'Mrad',        'email' => 'khaled.mrad@smarthr.com',      'dept' => 'Human Resources', 'desig' => 'Recruiter'],
            // Finance
            ['firstname' => 'Fatma',    'lastname' => 'Gharbi',      'email' => 'fatma.gharbi@smarthr.com',     'dept' => 'Finance',         'desig' => 'Accountant'],
            ['firstname' => 'Walid',    'lastname' => 'Saadi',       'email' => 'walid.saadi@smarthr.com',      'dept' => 'Finance',         'desig' => 'Financial Analyst'],
            // Marketing
            ['firstname' => 'Amira',    'lastname' => 'Bouzid',      'email' => 'amira.bouzid@smarthr.com',     'dept' => 'Marketing',       'desig' => 'Marketing Manager'],
            ['firstname' => 'Yassine',  'lastname' => 'Khelifi',     'email' => 'yassine.khelifi@smarthr.com',  'dept' => 'Marketing',       'desig' => 'Content Creator'],
            // Operations
            ['firstname' => 'Malek',    'lastname' => 'Dridi',       'email' => 'malek.dridi@smarthr.com',      'dept' => 'Operations',      'desig' => 'Operations Manager'],
            ['firstname' => 'Houda',    'lastname' => 'Ferchichi',   'email' => 'houda.ferchichi@smarthr.com',  'dept' => 'Operations',      'desig' => 'Data Analyst'],
            // Sales
            ['firstname' => 'Bilel',    'lastname' => 'Naceur',      'email' => 'bilel.naceur@smarthr.com',     'dept' => 'Sales',           'desig' => 'Sales Executive'],
            ['firstname' => 'Rim',      'lastname' => 'Bouaziz',     'email' => 'rim.bouaziz@smarthr.com',      'dept' => 'Sales',           'desig' => 'Sales Manager'],
            // Legal
            ['firstname' => 'Tarek',    'lastname' => 'Chebbi',      'email' => 'tarek.chebbi@smarthr.com',     'dept' => 'Legal',           'desig' => 'Legal Advisor'],
        ];

        $deptMap  = collect($departments)->keyBy('name');
        $desigMap = collect($designations)->keyBy('name');
        $empCount = EmployeeDetail::count();
        $employees = [];

        foreach ($profiles as $p) {
            $user = User::firstOrCreate(
                ['email' => $p['email']],
                [
                    'firstname'          => $p['firstname'],
                    'lastname'           => $p['lastname'],
                    'password'           => Hash::make('password'),
                    'type'               => UserType::EMPLOYEE,
                    'is_active'          => 1,
                    'phone'              => '+216 ' . rand(20, 99) . ' ' . rand(100, 999) . ' ' . rand(100, 999),
                    'email_verified_at'  => now(),
                ]
            );

            if (!$user->employeeDetail) {
                $empCount++;
                $detail = EmployeeDetail::create([
                    'emp_id'         => 'EMP-' . str_pad($empCount, 4, '0', STR_PAD_LEFT),
                    'user_id'        => $user->id,
                    'department_id'  => $deptMap[$p['dept']]->id,
                    'designation_id' => $desigMap[$p['desig']]->id,
                    'date_joined'    => Carbon::now()->subMonths(rand(3, 36)),
                    'dob'            => Carbon::now()->subYears(rand(24, 45)),
                    'marital_status' => collect(MaritalStatus::cases())->random(),
                    'no_of_children' => rand(0, 3),
                    'nationality'    => 'Tunisian',
                ]);

                EmployeeSalaryDetail::factory()->create(['employee_detail_id' => $detail->id]);
            } else {
                $dept  = $deptMap[$p['dept']] ?? null;
                $desig = $desigMap[$p['desig']] ?? null;
                if ($dept || $desig) {
                    $user->employeeDetail->update(array_filter([
                        'department_id'  => $dept?->id,
                        'designation_id' => $desig?->id,
                    ]));
                }
            }

            try { $user->assignRole(UserType::EMPLOYEE->value); } catch (\Throwable) {}
            $employees[] = $user;
        }

        return $employees;
    }

    // ── Attendance (last 60 working days, ~85 % attendance rate) ──────────────

    private function seedAttendance(array $employees): void
    {
        $start = Carbon::today()->subDays(60);
        $end   = Carbon::today()->subDay();

        foreach ($employees as $employee) {
            foreach (CarbonPeriod::create($start, $end) as $day) {
                // Skip weekends
                if ($day->isWeekend()) {
                    continue;
                }
                // Skip if already has attendance
                $exists = Attendance::where('user_id', $employee->id)
                    ->whereDate('startDate', $day)->exists();
                if ($exists) {
                    continue;
                }
                // 85% attendance rate
                if (rand(1, 100) <= 85) {
                    Attendance::create([
                        'user_id'   => $employee->id,
                        'startDate' => $day->toDateString(),
                        'endDate'   => $day->toDateString(),
                    ]);
                }
            }
        }
    }

    // ── Leave Requests ─────────────────────────────────────────────────────────

    private function seedLeaveRequests(array $employees): void
    {
        $types = ['annual', 'sick', 'emergency', 'unpaid'];
        $reasons = [
            'annual'    => ['Vacances familiales', 'Repos annuel', 'Congé personnel'],
            'sick'      => ['Maladie', 'Consultation médicale', 'Convalescence'],
            'emergency' => ["Urgence familiale", 'Hospitalisation d\'un proche', 'Décès dans la famille'],
            'unpaid'    => ['Voyage personnel', 'Formation externe'],
        ];

        foreach ($employees as $i => $employee) {
            // Each employee gets 1-3 leave periods in the past 3 months
            $leaveCount = rand(1, 3);
            for ($j = 0; $j < $leaveCount; $j++) {
                $type      = $types[($i + $j) % count($types)];
                $daysOff   = rand(1, 5);
                $startDate = Carbon::today()->subDays(rand(5, 90));
                $endDate   = $startDate->copy()->addDays($daysOff - 1);

                // Avoid duplicate leave for same period
                $overlap = LeaveRequest::where('user_id', $employee->id)
                    ->where('start_date', '<=', $endDate->toDateString())
                    ->where('end_date', '>=', $startDate->toDateString())
                    ->exists();

                if ($overlap) {
                    continue;
                }

                $status = collect(['approved', 'approved', 'approved', 'pending', 'rejected'])->random();
                LeaveRequest::create([
                    'user_id'     => $employee->id,
                    'type'        => $type,
                    'start_date'  => $startDate->toDateString(),
                    'end_date'    => $endDate->toDateString(),
                    'days'        => $daysOff,
                    'reason'      => collect($reasons[$type])->random(),
                    'status'      => $status,
                    'approved_by' => $status === 'approved' ? $this->admin->id : null,
                    'approved_at' => $status === 'approved' ? now()->subDays(rand(1, 10)) : null,
                ]);
            }
        }
    }

    // ── Tickets ────────────────────────────────────────────────────────────────

    private function seedTickets(array $employees): void
    {
        foreach ($employees as $employee) {
            $existing = Ticket::where('user_id', $employee->id)->count();
            if ($existing >= 2) {
                continue;
            }
            Ticket::factory(rand(1, 3))->create([
                'user_id'    => $employee->id,
                'created_by' => $this->admin->id,
            ]);
        }
    }

    // ── Projects ───────────────────────────────────────────────────────────────

    private function seedProjects(array $employees): void
    {
        if (Project::count() >= 5) {
            return;
        }

        $projectData = [
            ['name' => 'SmartHR Platform',    'priority' => 'High',   'desc' => 'Internal HR management platform development.'],
            ['name' => 'ERP Migration',        'priority' => 'High',   'desc' => 'Migrate legacy ERP to cloud-native solution.'],
            ['name' => 'Mobile App v2',        'priority' => 'Normal', 'desc' => 'Second version of the employee mobile application.'],
            ['name' => 'Data Warehouse',       'priority' => 'Normal', 'desc' => 'Build centralised data warehouse for analytics.'],
            ['name' => 'Security Audit 2026',  'priority' => 'High',   'desc' => 'Annual penetration testing and security hardening.'],
            ['name' => 'Onboarding Portal',    'priority' => 'Low',    'desc' => 'Self-service onboarding portal for new hires.'],
            ['name' => 'Payroll Automation',   'priority' => 'Normal', 'desc' => 'Automate monthly payroll processing and payslips.'],
        ];

        $clients = User::where('type', UserType::CLIENT)->get();
        if ($clients->isEmpty()) {
            return;
        }

        $startDate = Carbon::today()->subMonths(3);

        foreach ($projectData as $i => $pd) {
            $leader  = $employees[$i % count($employees)];
            $endDate = Carbon::today()->addMonths(rand(1, 6));

            $project = Project::create([
                'name'       => $pd['name'],
                'client_id'  => $clients->random()->id,
                'leader_id'  => $leader->id,
                'priority'   => $pd['priority'],
                'short_desc' => $pd['desc'],
                'description'=> $pd['desc'],
                'startDate'  => $startDate->copy()->addDays($i * 7)->toDateString(),
                'endDate'    => $endDate->toDateString(),
                'rate'       => rand(20, 80),
                'rateType'   => collect(['Hourly', 'Fixed'])->random(),
                'created_by' => $this->admin->id,
            ]);

            // Project lead entry
            ProjectLead::firstOrCreate(
                ['project_id' => $project->id, 'user_id' => $leader->id],
                ['position' => 'Lead']
            );

            // Assign 3-5 random team members
            $team = collect($employees)->shuffle()->take(rand(3, 5));
            foreach ($team as $member) {
                ProjectTeam::firstOrCreate([
                    'project_id' => $project->id,
                    'user_id'    => $member->id,
                ]);
            }
        }
    }

    // ── Helpers ────────────────────────────────────────────────────────────────

    private function ensureRoles(): void
    {
        foreach (UserType::cases() as $type) {
            Role::firstOrCreate(['name' => $type->value, 'guard_name' => 'web']);
        }
    }
}
