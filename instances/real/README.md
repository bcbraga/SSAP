# Real Dataset Format

This folder contains real instances collected. Each instance is described using five files, which together represent classroom structure, student conflicts, and seat preferences.

### Files

- **`grafo.txt`**  
  Contains the edge list for each instance. Each line includes the instance ID and the list of edges (student conflicts).

- **`grafo_tras.txt`**  
  Lists students who should be seated in the back rows.

- **`grafo_frente.txt`**  
  Lists students who should be seated in the front rows.

- **`grafo_info.txt`**  
  Contains a summary of the classroom and conflict graph properties for each instance. Each line includes the following fields, in order:
  
  1. **Instance ID**  
  2. **Total number of students** (`|S|`)  
  3. **Number of conflicts** (`∑ c_{ij}`)  
  4. **Number of students with front-seat preference** (`∑ max{rᵢ, 0}`)  
  5. **Number of students with back-seat preference** (`∑ |min{rᵢ, 0}|`)  
  6. **Number of rows** (`|Λ|`)  

- **`grafo_vet.txt`**  
  Describes the physical layout of the classroom with a vector showing the number of seats per row.

Each file shares a consistent instance ID so they can be easily cross-referenced.
