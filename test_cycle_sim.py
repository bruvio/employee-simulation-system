#!/usr/bin/env python3

from employee_population_simulator import EmployeePopulationGenerator
from review_cycle_simulator import ReviewCycleSimulator

# Generate small population
pop_gen = EmployeePopulationGenerator(population_size=10, random_seed=42)
small_population = pop_gen.generate_population()

print("Generated population with keys:", small_population[0].keys())
print("First employee:", small_population[0])

try:
    # Test cycle simulator initialization
    cycle_simulator = ReviewCycleSimulator(initial_population=small_population, random_seed=42)
    print("Cycle simulator initialized successfully")
except Exception as e:
    print(f"Error in cycle simulator initialization: {e}")
    import traceback

    traceback.print_exc()
