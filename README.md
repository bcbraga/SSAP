# Conflict-Aware Seat Assignment in Classroom Environments

Welcome to the GitHub repository for our research paper entitled **"Conflict-Aware Seat Assignment in Classroom Environments"**. This repository contains the code to solve the **Student Seat Allocation Problem (SSAP)**, introduced and implemented by
**Charytitsch and Nascimento (2025)**.

## Overview

Classroom dynamics are largely shaped by how students are distributed in the environment. The Student Seat Allocation Problem (SSAP) seeks to determine an effective seating plan that minimizes interpersonal conflicts by maximizing the physical 
distance between students with known conflicts, while respecting the spatial constraints of the classroom layout.

To tackle this problem, we propose:

* An **Integer Linear Programming** (ILP) formulation;
* An efficient **Iterated Local Search (ILS)** heuristic for large and complex instances.

The ILS heuristic is capable of generating near-optimal or relaxed solutions by assigning students to specific desks within a traditional classroom setting, where desks are arranged in parallel rows. This approach supports teachers by offering 
practical student-to-desk assignments that minimize interpersonal conflicts while respecting spatial and distance constraints.

## Cite

To use or reference the resources in this repository, please cite the following work:

> Bruna Cristina Braga Charytitsch and Mariá Cristina Vasconcelos Nascimento (2025). *Conflict-Aware Seat Assignment in Classroom Environments*. Submitted to \[Journal/Conference Name ???].

## Repository Contents

* **/instances/**: Real and synthetic datasets used in the experiments
* **/heuristic/**: Implementation of the ILS metaheuristic
* **/results/**: Computational results obtained using the Gurobi solver. Since Gurobi provides optimal (or near-optimal) solutions for most instances, these results serve as a reference benchmark. Results from the ILS metaheuristic are are discussed in detail in the associated publication.


## Getting Started

To reproduce our experiments:

1. Clone this repository.
2. Install required dependencies listed in `requirements.txt`.
3. Run the desired module:

   * `python heuristic/ssap_ils.py` for ILS heuristic

4. Sample input and output data are available in `/instances` and `/results`.

## Method and Implementation

The ILS heuristic was implemented in pure Python and was designed with future integration into an educational decision-support system in mind.

The ILS searches through the solution space allowing minor constraint violations but penalizing them in the cost function. This provides flexibility and fast approximate solutions suitable for large instances.

## Experimental Results

* **Benchmarking**: Optimal solutions were obtained for several instances using the Gurobi solver.

* **Heuristic Comparison**: ILS was evaluated against these optimal results on runtime and quality.

* **Performance**: ILS heuristic produced high-quality solutions across all datasets.

## Future Work

We are developing a scalable decision support tool based on the ILS heuristic, with future extensions including:

* Constraint tuning via user preferences
* Machine Learning-based conflict estimation

## Contact

For questions or contributions, please contact:

* **Bruna Cristina Braga Charytitsch** – [bruna.braga@ga.ita.br](mailto:bruna.braga@ga.ita)
* **Mariá Cristina Vasconcelos Nascimento** – [mariah@ita.br](mailto:mariah@ita.br)
