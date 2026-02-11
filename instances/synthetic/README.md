# Synthetic Dataset Format

This folder contains synthetic instances generated for the Student Seat Allocation Problem (SSAP). Each instance is described using five files, which together represent classroom structure, student conflicts, and seat preferences.

### Files

- **`grafo.txt`**  
  Contains the edge list for each instance. Each line includes the instance ID, the list of edges (student conflicts), and the repetition index (0–4) corresponding to one of five instances generated under the same configuration.

- **`grafo_tras.txt`**  
  Lists students who should be seated in the back rows.

- **`grafo_frente.txt`**  
  Lists students who should be seated in the front rows.

- **`grafo_info.txt`**  
  Summarizes the graph properties: instance ID, total number of students, percentage of students involved in conflicts, percentage of edges created, number of conflict nodes and edges, graph density, and average degree. Also includes the repetition index (0–4), corresponding to one of five instances generated under the same configuration.

- **`grafo_vet.txt`**  
  Describes the physical layout of the classroom with a vector showing the number of seats per row (i.e., desks per row).

Each file shares a consistent instance ID so they can be easily cross-referenced.

**Note**: Instances for which the solver reported infeasible solutions were removed from the dataset. As a result, out of the 135 originally generated instances, 131 were used in the experiments.
