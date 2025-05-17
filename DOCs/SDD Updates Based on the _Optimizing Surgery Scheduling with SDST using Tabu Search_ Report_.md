**SDD Updates Based on the "Optimizing Surgery Scheduling with SDST using Tabu Search" Report:**

**Section 2: System Overview** (from previous SDD draft)

**2.2 Design Goals** *(Addition in bold based on the report's focus)*

* **Modularity (NFR-MAINT-xxx):** The system will be composed of loosely coupled, independently developable, and maintainable modules.  
* **Scalability (NFR-SCALE-xxx):** The architecture and database design will support future growth in data volume and user load, within the context of an on-premises deployment.  
* **Security (NFR-SEC-xxx):** The system will protect sensitive patient and operational data through robust authentication, authorization, data encryption, and adherence to privacy principles (HIPAA, GDPR-like, CNDP awareness).  
* **Usability (NFR-USE-xxx):** The user interface will be intuitive, efficient, and tailored to the needs of different user roles (Schedulers, Surgeons, Nurses, Admins).  
* **Reliability (NFR-REL-xxx):** The system will be designed for stable operation and include mechanisms for error handling and data integrity.  
* **Maintainability (NFR-MAINT-xxx):** The codebase will be well-structured, documented, and easy to modify or extend.  
* **Performance (NFR-PERF-xxx):** The system will provide acceptable response times for user interactions and efficient execution of scheduling optimization algorithms, **specifically addressing the computational aspects of Tabu Search with Sequence-Dependent Setup Times (SDST)** for representative datasets.  
* **Integrability (SRD-SCOPE-006):** The system will be designed to interface with external systems, particularly EHRs, via well-defined APIs.  
* **Optimization Effectiveness:** The system shall effectively optimize surgery schedules by minimizing a composite objective function that includes factors like makespan, resource utilization, overtime, and **critically, the impact of sequence-dependent setup times (SDST).**

**2.3 High-Level Architecture** *(Minor clarification on where the optimization algorithm might reside/execute, in bold)* The Surgery Scheduling System App will employ a **Client-Server architectural model**.

* **Client-Side (Frontend):** React web application.  
* **Server-Side (Backend):** Node.js with Express.js framework. Hosts business logic, and API endpoints. Manages communication with the database. Handles authentication, authorization, and session management. **It will either directly implement or orchestrate calls to the optimization engine (e.g., a Python-based Tabu Search component) for schedule generation.**  
* **Database (Persistence Layer):** PostgreSQL relational database.  
* **Optimization Engine (Potentially Python-based):** A distinct component responsible for executing the Tabu Search algorithm with SDST logic. This could be a microservice, a library called by the Node.js backend, or a script. *(This detail needs to be confirmed based on your implementation plan, but the report strongly suggests Python for the TS algorithm itself).*  
* **External Interfaces:** RESTful API layer.  
* **Deployment Environment:** On-premises.

*(The Mermaid diagram would remain largely the same, but we could add an "Optimization Service (Python)" box interacting with the Backend if we decide on a microservice approach for the algorithm).*

---

**Section 3: Architectural Design** (from previous SDD draft)

**3.4 Technology Stack Justification** *(Addition/Refinement in bold)*

* **Frontend:** React \- Justified by its component-based architecture, virtual DOM for performance, large community, and suitability for building dynamic Single Page Applications (SPAs).  
* **Backend:** Node.js with Express.js \- Chosen for its non-blocking I/O, scalability for I/O bound operations (like handling API requests), JavaScript ecosystem alignment with React, and speed of development. It will serve as the primary orchestrator for business logic and API provision.  
* **Database:** PostgreSQL \- Selected for its robustness, reliability, support for complex queries, ACID compliance, and strong open-source community support. Suitable for structured healthcare data.  
* **Optimization Algorithm Implementation:** **The core optimization logic, particularly the Tabu Search algorithm addressing Sequence-Dependent Setup Times (SDST), is heavily informed by the research detailed in \[Report-TS-SDST-01\]. Given the report's focus on Python implementation (leveraging libraries like NumPy, Pandas, deque), the design will accommodate either:**  
  * **A Python-based microservice/module invoked by the Node.js backend for optimization tasks.** This allows leveraging Python's strengths in numerical computation and existing optimization libraries.  
  * **A direct re-implementation of the core Tabu Search logic within the Node.js environment if deemed feasible and efficient for the project's scope.** (This seems less likely given the detailed Python focus of the report). **The choice will prioritize leveraging the detailed implementation guidance in \[Report-TS-SDST-01\] for effectiveness.**  
* **API:** RESTful principles for client-server and external system communication due to its statelessness, scalability, and widespread adoption. JSON will be the primary data interchange format.

---

Now, let's move to the more significantly impacted sections.

**Section 4: Detailed Module Design**

The report doesn't explicitly define system modules outside the algorithm, but the Tabu Search implementation itself is modular (as described in Section II.A of the report: `generate_initial_solution`, `get_neighbors`, `calculate_objective`, etc.). We can consider an "Optimization Module" or integrate these into the "Scheduling Module."

**4.x Optimization Module (or enhanced Scheduling Module)**

* **4.x.1 Purpose and Responsibilities:**

  * To generate optimized surgery schedules based on user inputs, resource availability, defined constraints, and the objective function.  
  * To specifically incorporate and minimize the impact of Sequence-Dependent Setup Times (SDST).  
  * To implement the Tabu Search metaheuristic as the core optimization engine, following the design principles outlined in \[Report-TS-SDST-01\].  
* **4.x.2 Key Functionalities/Operations (derived from the report's TS structure):**

  * **Initialization:**  
    * `initialize_solution()`: Generates an initial feasible or near-feasible schedule (as per report Section II.A, `generate_initial_solution`). This might use simpler heuristics (e.g., greedy assignment, respecting SDST from an empty OR state).  
    * `initialize_tabu_list()`: Sets up the tabu list (e.g., using `collections.deque` as suggested in report Section II.A, `tabu_list = deque(maxlen=tabu_tenure)`).  
    * `initialize_best_solution_tracking()`: To store `x_best` and `f(x_best)`.  
  * **Iterative Search Loop:**  
    * `generate_neighborhood(current_schedule)`: Implements neighborhood generation operators (e.g., Swap, Insertion as per report Section I.B, Table 1, `get_neighbors`). Must efficiently consider SDST when creating neighbors. May use candidate list strategies for large neighborhoods (report Section I.B).  
    * `evaluate_neighbor(neighbor_schedule)`: Calculates the objective function for a given neighbor schedule. This function is critical and must accurately incorporate SDST (report Section II.C, III.B, `calculate_objective`).  
    * `select_best_admissible_move(neighborhood, tabu_list, aspiration_criteria, current_best_objective)`: Selects the best move that is not tabu or meets aspiration criteria (report Section I.A, `is_tabu`, `check_aspiration_criteria`).  
    * `update_current_solution(selected_move)`.  
    * `update_tabu_list(move_attributes, tabu_tenure)`: Adds attributes of the chosen move to the tabu list (report Section I.C, II.A `update_tabu_list`). The attributes should be chosen to effectively manage SDST implications (report Section III.C).  
    * `apply_aspiration_criteria(move, current_objective, global_best_objective)`: Checks if a tabu move can be accepted (report Section I.D).  
    * `update_best_solution(current_solution, current_objective)`.  
    * `check_stopping_criteria()`: (e.g., max iterations, time limit, no improvement, as per report Section I.E).  
  * **SDST Handling:**  
    * `get_setup_time(prev_surgery_type, next_surgery_type, or_id)`: Retrieves setup time from the SDST matrix/data structure.  
  * **Constraint Handling:**  
    * Integrates penalty functions for soft constraints or uses feasibility-preserving moves/rejection for hard constraints within the neighborhood generation and evaluation (report Section II.D).  
  * **(Optional based on thesis scope) Intensification and Diversification Strategies:**  
    * Implement mechanisms for Path Relinking, restarting from elite solutions, or frequency-based memory for diversification as outlined in report Section I.F, IV.C.  
* **4.x.3 Interfaces:**

  * **Input:** Receives surgery requests, resource availability data, SDST matrix, constraint definitions, and optimization parameters (e.g., objective weights, Tabu Search parameters like tenure, max iterations) from the main backend (Node.js application) or a scheduling data preparation module.  
  * **Output:** Returns the optimized schedule (or a set of good schedules) to the main backend. May also output performance logs of the optimization run.  
  * **Internal:** Follows the Python-based structure suggested in the report \[Report-TS-SDST-01, Section II.A\], with clear functions/classes for each TS component.  
* **4.x.4 Data Structures (within the optimization module, as per report Section II.A, II.B, III.A):**

  * **Schedule Representation:** Custom Python classes for `Surgery`, `OperatingRoom`, and `Schedule` are recommended (report Section II.B).  
    * `Surgery Class`: `id`, `duration`, `type` (for SDST), `earliest_start`, `due_date`, `required_resources` (surgeon, staff, equipment).  
    * `OperatingRoom Class`: `id`, `availability_windows`, `current_schedule_sequence` (list of `Surgery` objects with calculated start/end times incorporating SDST).  
    * `Schedule Class`: Encapsulates the entire schedule (e.g., a dictionary mapping OR IDs to their sequences), methods for objective calculation, neighborhood generation.  
  * **SDST Matrix:** 2D dictionary or NumPy array: `setup_matrix[previous_surgery_type][current_surgery_type]` (report Section III.A).  
  * **Tabu List:** `collections.deque(maxlen=tabu_tenure)` storing move attributes (report Section II.A).  
  * **Elite Solutions List:** For intensification strategies.  
* **4.x.5 Core Logic/Algorithms:**

  * Implementation of the Tabu Search algorithm as detailed in \[Report-TS-SDST-01\]. Key aspects include:  
    * Neighborhood operators: Swap and/or Insertion, adapted for SDST.  
    * Objective function: Weighted sum including makespan, overtime, utilization, and penalties for SDST and constraint violations. Delta evaluation should be considered for efficiency (report Section III.B).  
    * Tabu list management: Based on move attributes, with appropriate tenure (static or dynamic, as per report Section I.C).  
    * Aspiration criteria: Typically, allow a move if it leads to a new global best solution (report Section I.D).  
    * Parameter tuning strategy (as per report Section IV.A) should be noted as an important part of the development/testing process.

---

**Section 5: Data Design**

**5.1 Database Choice Justification (PostgreSQL)** *(Remains the same)*

**5.2 Detailed Database Schema** *(Enhancements in bold based on the need to support SDST and surgery types)* The schema previously outlined needs to ensure it captures `SurgeryType` effectively for SDST calculations.

* **`Patients`** (PatientID, Name, DOB, ContactInfo, MedicalHistory, PrivacyConsent)  
* **`Staff`** (StaffID, Name, Role, Specialization, ContactInfo)  
* **`SurgeryTypes`**  
  * `SurgeryTypeID` (Primary Key)  
  * `TypeName` (e.g., "Orthopedic Hip Replacement", "Neurosurgery Tumor Removal", "General Appendectomy") \- This granularity is needed for accurate SDST.  
  * `Description`  
* **`Surgeries`**  
  * `SurgeryID` (Primary Key)  
  * `PatientID` (Foreign Key to Patients)  
  * `SurgeryTypeID` (Foreign Key to SurgeryTypes) **(Crucial for SDST)**  
  * `ScheduledDateTime` (can be null initially, populated by scheduler)  
  * `ActualStartDateTime` (nullable)  
  * `ActualEndDateTime` (nullable)  
  * `EstimatedDurationMinutes` (processing time only)  
  * `UrgencyLevel` (e.g., Elective, Urgent-Level1, Urgent-Level2)  
  * `Status` (e.g., Requested, Scheduled, In Progress, Completed, Cancelled)  
  * `OperatingRoomID` (Foreign Key to OperatingRooms, nullable until assigned)  
  * `PrimarySurgeonID` (Foreign Key to Staff, nullable until assigned)  
  * `Notes`  
* **`OperatingRooms`**  
  * `RoomID` (Primary Key)  
  * `RoomNameOrNumber`  
  * `Location`  
  * `AvailableFromTime` (e.g., '08:00')  
  * `AvailableToTime` (e.g., '17:00')  
  * `IsSpecializedFor` (e.g., list of SurgeryTypeIDs, or a linking table if many-to-many)  
* **`SequenceDependentSetupTimes (SDST)`**  
  * `SDST_ID` (Primary Key)  
  * `FromSurgeryTypeID` (Foreign Key to SurgeryTypes, can be null for setup from 'empty OR')  
  * `ToSurgeryTypeID` (Foreign Key to SurgeryTypes)  
  * `OperatingRoomID` (Foreign Key to OperatingRooms, optional, if setup times also depend on the OR itself, as mentioned in report Section III.A)  
  * `SetupTimeMinutes` (Integer)  
* **`SurgeryStaffAssignments`** (AssignmentID, SurgeryID, StaffID, RoleInSurgery)  
* **`Equipment`** (EquipmentID, Name, Type, AvailabilityStatus)  
* **`SurgeryEquipmentUsage`** (UsageID, SurgeryID, EquipmentID, RequiredFrom, RequiredTo)  
* **`AuditLog`** (LogID, Timestamp, UserID, Action, Details)  
* **`UserAccounts`** (UserID, Username, HashedPassword, Role, StaffID (if applicable))

**5.3 Data Dictionary** *(Would detail each table and field from 5.2)*

**5.5 Data Validation and Integrity Rules** *(Addition in bold)*

* Standard data type checks, not-null constraints.  
* Referential integrity through foreign keys.  
* Validation for surgery durations (must be positive).  
* Validation for SDST values (must be non-negative).  
* **Ensure that `FromSurgeryTypeID` and `ToSurgeryTypeID` in the `SequenceDependentSetupTimes` table are valid `SurgeryTypeID`s.**  
* **Business rule: A surgeon cannot be assigned to overlapping surgeries.** (This is handled by the scheduling algorithm but also a data integrity concern).

---

**Section 9: Algorithm Design (High-Level)** *(This section gets significantly fleshed out based on the report)*

**9.1 Overview of Scheduling Optimization Approach: Tabu Search for SDST** The core scheduling optimization will be performed by a Tabu Search (TS) algorithm specifically designed to handle Sequence-Dependent Setup Times (SDST), as detailed in \[Report-TS-SDST-01\].

**9.1.1 Solution Representation (Report Section II.B):**

* A solution (schedule) will be represented primarily using custom Python classes:  
  * `Surgery` objects: Storing ID, processing duration, surgery type (critical for SDST), earliest start, due date, required resources.  
  * `OperatingRoom` objects: Storing ID, availability windows, and the current sequence of `Surgery` objects assigned to it, including their calculated start and end times (which incorporate SDST).  
  * `Schedule` object: An overarching class encapsulating the state of all ORs and their surgery sequences. This class will provide methods for evaluation and neighborhood generation.

**9.1.2 Initial Solution Generation (Report Section II.A):**

* An initial feasible or near-feasible schedule will be generated using a constructive heuristic. This could be a greedy approach assigning surgeries to the earliest available valid slots in ORs, considering resource constraints and calculating SDST from an initial "empty OR" state or the previous surgery. (e.g., modified MATCS rule as mentioned in report \[Report-TS-SDST-01, Section III.D citing source 58\]).

**9.1.3 Neighborhood Structure (Report Section I.B, Table 1):**

* The primary neighborhood generation operators will be:  
  * **Insertion (Shift):** Moving a surgery from its current position to another position within the same OR's sequence or to a different OR. This is noted as powerful for SDST.  
  * **Swap (Pairwise):** Exchanging two surgeries, either within the same OR or potentially across different ORs (if resource reassignment is permitted and makes sense for the problem definition).  
* The choice of operator or a mix of operators will be configurable or adapted during the search.  
* Candidate list strategies may be employed if the neighborhood size becomes too large for full evaluation in each iteration (Report Section I.B).

**9.1.4 Objective Function (Report Section II.C, III.B):**

* The objective function will be a weighted sum of several criteria, aiming for minimization:  
  * Minimize total makespan.  
  * Minimize total overtime costs (surgeries extending beyond standard OR hours).  
  * Maximize OR utilization (or minimize OR idle time).  
  * Minimize total patient waiting time or tardiness (if due dates are relevant).  
  * **Minimize total sequence-dependent setup times incurred.**  
  * Penalties for soft constraint violations.  
* The calculation must accurately derive start/end times by summing processing times and the SDST between consecutive surgeries in each OR: `StartTime_j = CompletionTime_i + SetupTime_ij`.  
* Delta evaluation (calculating the change in objective function value due to a move) will be investigated for efficiency.

**9.1.5 Tabu List Management (Report Section I.C, II.A, III.C):**

* **Content:** The tabu list will store attributes of moves to prevent cycling. For SDST, this could include:  
  * The surgery that was moved and its original/new (OR, position) assignment.  
  * The specific pair of surgeries that were swapped.  
  * Attributes related to the sequence (e.g., making `(SurgeryTypeA -> SurgeryTypeB in OR_X)` tabu if this beneficial pairing was just broken).  
* **Structure:** Implemented as a fixed-size FIFO queue using `collections.deque`.  
* **Tabu Tenure:** Initially a static tenure (e.g., related to problem size like `sqrt(N)` or a small constant like 7-15). Dynamic or adaptive tenure mechanisms (Report Section I.C, IV.A) will be considered for future enhancements or if initial tuning proves difficult.

**9.1.6 Aspiration Criteria (Report Section I.D):**

* The primary aspiration criterion will be to allow a tabu move if it leads to a solution with an objective function value better than the best solution found so far in the entire search history (`x_best`).

**9.1.7 Stopping Criteria (Report Section I.E):**

* A hybrid approach will be used:  
  * Maximum number of iterations.  
  * Maximum computational time limit.  
  * Number of iterations without improvement in the best-known solution. The algorithm will terminate when any of these conditions are met.

**9.1.8 Constraint Handling (Report Section II.D):**

* **Hard Constraints** (e.g., surgeon double-booking, OR unavailable, equipment clashes) will be handled by:  
  * Designing neighborhood operators to generate only feasible solutions where possible.  
  * Rejecting moves that lead to violations of these hard constraints.  
* **Soft Constraints** (e.g., surgeon preferences, minimizing overtime by small amounts, preferred surgery order for non-SDST reasons) will be managed using penalty functions integrated into the objective function. The weights of these penalties will be tunable.

**9.1.9 Intensification and Diversification (Report Section I.F, IV.C):**

* **Initial Implementation:** May focus on the core TS loop.  
* **Potential Enhancements (if time permits for the thesis):**  
  * **Intensification:** Restarting from a pool of elite solutions found during the search. Path Relinking if feasible.  
  * **Diversification:** Using frequency-based memory to penalize often-chosen moves/attributes or restarting with deliberately perturbed solutions if stagnation is detected.

**9.1.10 SDST Data Management (Report Section III.A):**

* The algorithm will access a pre-defined SDST matrix/data structure (e.g., Python dictionary `setup_matrix[or_id_optional][prev_surgery_type][next_surgery_type]`). This matrix will be configurable by administrators via the main application.

**9.2 Parameter Tuning (Report Section IV.A)**

* The design acknowledges that TS parameters (tabu tenure, neighborhood definition, objective function weights, penalty weights) are sensitive.  
* A systematic approach to parameter tuning (e.g., experimental design on representative datasets) will be part of the algorithm development and testing phase. Automated tools like `irace` are noted as advanced options beyond initial scope but good for future work.

**9.3 Computational Complexity Management (Report Section V)**

* For the scope of the thesis project, the algorithm will be designed for typical small to medium hospital department scenarios.  
* Strategies like efficient data structures for setup times, considering delta evaluation for the objective function, and potentially candidate list strategies for neighborhood exploration will be employed to manage complexity. Parallel Tabu Search or complex decomposition methods are likely out of scope for initial implementation but noted as future enhancements for very large-scale problems.

