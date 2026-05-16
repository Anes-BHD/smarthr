<?php

namespace Database\Seeders;

use App\Enums\MaritalStatus;
use App\Enums\UserType;
use App\Models\Department;
use App\Models\Designation;
use App\Models\EmployeeDetail;
use App\Models\User;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class UserSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $users = [
            [
                'firstname' => 'Mushe',
                'lastname' => 'Abdul-Hakim',
                'email' => 'superadmin@smarthr.com',
                'password' => Hash::make('password'),
                'email_verified_at' => now(),
                'type' => UserType::SUPERADMIN,
                'is_active' => 1,
            ],
            [
                'firstname' => 'John',
                'lastname' => 'Doe',
                'email' => 'client@smarthr.com',
                'password' => Hash::make('password'),
                'email_verified_at' => now(),
                'type' => UserType::CLIENT,
                'is_active' => 1,
            ],
        ];

        foreach ($users as $userData) {
            User::updateOrCreate(['email' => $userData['email']], $userData);
        }
        $employee = User::updateOrCreate(
            ['email' => 'employee@smarthr.com'],
            [
                'firstname' => 'Smart',
                'lastname' => 'Employee',
                'password' => Hash::make('password'),
                'email_verified_at' => now(),
                'type' => UserType::EMPLOYEE,
                'is_active' => 1,
            ]
        );
        EmployeeDetail::create([
            'emp_id' => 'EMP-0001',
            'user_id' => $employee->id,
            'department_id' => Department::factory()->count(1)->create([
                'name' => 'Nuclues',
                'location' => 'Bay Area',
            ])->first()->id,
            'designation_id' => Designation::factory()->count(1)->create([
                'name' => 'Software Developer'
            ])->first()->id,
            'passport_no' => '1234567899',
            'passport_expiry_date' => '2024-06-30',
            'passport_tel' => '1234567899',
            'nationality' => 'Ghanain',
            'religion' => null,
            'ethnicity' => null,
            'marital_status' => MaritalStatus::SINGLE,
            'spouse_occupation' => 'no',
            'no_of_children' => '0',
            'emergency_contacts' => null,
            'date_joined' => now(),
            'dob' => '2023-01-01',
        ]);
    }
}
