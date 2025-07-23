## Results Obtained with Gurobi

The file model.txt summarizes the results of solving each feasible instance of the Student Seat Allocation Problem (SSAP) using the Gurobi optimizer. Each row contains:

- `ID`: Instance identifier  
- `objective_function`: Objective function value obtained  
- `status_Gurobi`: Solver status code  
- `time` (formatted): Time taken (HH:MM:SS)  
- `time` (seconds): Time taken in seconds (float)

### Gurobi Status Codes:

- `2` – **Optimal**: An optimal solution was found.  
- `9` – **Time Limit**: The solver reached the time limit; a feasible solution may have been returned.

Out of 135 generated instances, 131 feasible instances were solved and reported here. Infeasible instances were discarded.
