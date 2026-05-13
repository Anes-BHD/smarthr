<?php

namespace Database\Factories;

use App\Models\AttendanceTimestamp;
use App\Models\User;
use App\Models\Attendance;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\AttendanceTimestamp>
 */
class AttendanceTimestampFactory extends Factory
{
    protected $model = AttendanceTimestamp::class;

    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        $startTime = $this->faker->dateTimeBetween('08:00:00', '10:00:00');
        $endTime = $this->faker->dateTimeBetween('17:00:00', '19:00:00');

        return [
            'user_id' => User::factory(),
            'attendance_id' => Attendance::factory(),
            'startTime' => $startTime->format('H:i:s'),
            'endTime' => $endTime->format('H:i:s'),
            'location' => $this->faker->city(),
            'billable' => $this->faker->boolean(),
            'ip' => $this->faker->ipv4(),
            'note' => $this->faker->sentence(),
            'created_at' => now(),
            'updated_at' => now(),
        ];
    }
}
