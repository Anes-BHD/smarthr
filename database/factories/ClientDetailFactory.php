<?php

namespace Database\Factories;

use App\Models\ClientDetail;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\ClientDetail>
 */
class ClientDetailFactory extends Factory
{
    protected $model = ClientDetail::class;

    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            'clt_id' => 'CLT-' . $this->faker->unique()->numberBetween(1000, 9999),
            'user_id' => User::factory(),
            'company' => $this->faker->company(),
            'billing_address' => $this->faker->address(),
            'post_address' => $this->faker->address(),
            'created_at' => now(),
            'updated_at' => now(),
        ];
    }
}
