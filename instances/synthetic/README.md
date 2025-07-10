# Synthetic Dataset Format

This folder contains synthetic instances generated for the Student Seat Allocation Problem (SSAP). Each instance is described using five files, which together represent classroom structure, student conflicts, and seat preferences.

### Files

- **`grafo.txt`**  
  Contains the edge list for each instance. Each line includes the instance ID, the list of edges (student conflicts), and the repetition index.

- **`grafo_atras.txt`**  
  Lists students who should be seated in the back rows (e.g., personal preference or behavioral considerations).

- **`grafo_info.txt`**  
  Summarizes the graph properties: instance ID, total students, percentage of students in conflict, percentage of edges created, number of conflict nodes and edges, graph density, and average degree.

- **`grafo_vet.txt`**  
  Describes the physical layout of the classroom with a vector showing the number of seats per row (i.e., desks per line).

- **`grafo_frente.txt`**  
  Lists students who should be seated in the front rows (e.g., based on pedagogical needs).

Each file shares a consistent instance ID so they can be easily cross-referenced.
