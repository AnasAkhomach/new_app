**SRD Updates Based on the "Optimizing Surgery Scheduling with SDST using Tabu Search" Report:**

**Section 1: Introduction**

**1.1 Purpose** *(Suggested update in bold)* The purpose of this document is to specify the software requirements for the Surgery Scheduling System App. This system is designed to manage and optimize the scheduling of elective and emergency surgical operations within a hospital or clinic setting. The primary goals are to improve operating room (OR) utilization, reduce patient waiting times, enhance resource management (surgeons, staff, equipment), **and critically, to address the complexities of sequence-dependent setup times (SDST) between surgeries.** The system aims to provide a robust decision-support tool for schedulers. This system is being developed as part of a final thesis project to demonstrate the application of optimization techniques, **such as Tabu Search, tailored for scheduling problems with SDST,** in healthcare logistics.

**1.4 Project Scope**

**1.4.1 In Scope:** *(Updates/additions in bold)*

* FR-SCOPE-001: Support the scheduling of both elective and emergency surgeries.  
* FR-SCOPE-002: Manage key resources including surgeons, operating rooms (ORs), specialized nursing staff, anesthesiologists, and critical surgical equipment.  
* **FR-SCOPE-002.1: The system shall specifically model and incorporate sequence-dependent setup times (SDST) into all scheduling and optimization processes.**  
* FR-SCOPE-003: Provide role-based access control for different user types (e.g., Schedulers, Surgeons, Nurses, Administrators).  
* FR-SCOPE-004: Implement advanced optimization algorithms (e.g., inspired by heuristic methods like Tabu Search, as detailed in supporting research for this thesis, specifically targeting problems with SDST) to generate efficient and conflict-minimized schedules.  
* FR-SCOPE-005: Allow for manual adjustments and overrides to the optimized schedule by authorized personnel.  
* FR-SCOPE-006: Integrate with existing hospital Electronic Health Record (EHR) systems via a defined API to retrieve necessary patient data and potentially update schedules (read-only for patient data initially, with clear data mapping for integration).  
* FR-SCOPE-007: Generate reports on OR utilization, surgeon workload, patient wait times, **impact of setup times,** and other key performance indicators.  
* FR-SCOPE-008: Provide a notification system for schedule changes, confirmations, and alerts.  
* FR-SCOPE-009: Be designed for on-premises deployment within a hospital's IT infrastructure.  
* FR-SCOPE-010: Maintain an audit trail of significant system events and data modifications.  
* **FR-SCOPE-011: The system shall allow for the definition and management of SDST data (e.g., a matrix based on preceding/succeeding surgery types and/or OR characteristics).**

**1.5 References** *(Addition in bold)*

* Bouguerra, Afef. "Optimisation et aide à la décision pour la programmation des opérations électives et urgentes." (Thesis providing foundational concepts and context).  
* **\[Report-TS-SDST-01\] \[Your Name/ID Here\], "Optimizing Surgery Scheduling with Sequence-Dependent Setup Times using Tabu Search in Python.txt," \[Date of that report, or reference as 'Project Working Document'\]. (Key reference for optimization algorithm approach and SDST handling).**  
* IEEE Std 830-1998 \- IEEE Recommended Practice for Software Requirements Specifications (or a more current relevant standard if specified by your institution).  
* Relevant hospital guidelines or existing scheduling protocols (if applicable and available for reference during the thesis).  
* \[Your Name/ID Here\] \- Project Proposal Document for Surgery Scheduling System App, \[Date\].  
* RFC 2119: Key words for use in RFCs to Indicate Requirement Levels.  
* Morocco: Law No. 09-08 on the protection of individuals with regard to the processing of personal data (as a reference for data privacy principles in the local context, alongside GDPR/HIPAA general principles for academic demonstration).

---

**Section 2: Overall Description**

**2.2 Product Features (Summary)** *(Update in bold)* The system will provide the following key features:

* **Dynamic Surgery Scheduling with SDST Consideration:** Creation, modification, and cancellation of elective and emergency surgeries, explicitly accounting for sequence-dependent setup times.  
* **Optimization Engine for SDST:** Algorithmic generation of optimized schedules considering various constraints and objectives, with a core focus on minimizing inefficiencies caused by SDST.  
* **Resource Management:** Tracking and allocation of operating rooms, surgeons, staff, and equipment.  
* **Emergency Integration:** Efficient incorporation of urgent cases into the existing schedule, considering SDST implications.  
* **User Role Management:** Differentiated access and functionalities based on user roles.  
* **Reporting & Analytics:** Generation of insightful reports for operational efficiency, including SDST impact analysis, and decision-making.  
* **Notifications & Alerts:** Timely communication of schedule updates and critical events.  
* **EHR Integration Support:** Interface for data exchange with EHR systems.  
* **Audit Trails:** Logging of important system activities for security and accountability.  
* **SDST Data Management:** Tools for defining and managing the data related to sequence-dependent setup times.

**2.5 Design and Implementation Constraints** *(No major change needed here based on the report, as CON-007 already covers the optimization technique. The report reinforces this constraint and provides depth for the design of this aspect, which will be reflected in the SDD.)*

---

**Comments on Further SRD Sections based on the Report:**

**Section 3: System Features (Functional Requirements)** This section will see significant expansion. We'll need to add specific functional requirements related to:

* **SDST Data Management:**  
  * FR-SDST-001: The system shall allow authorized administrators to define, view, modify, and delete sequence-dependent setup time rules/matrix.  
  * FR-SDST-002: Setup times shall be definable based on, at minimum, the type of the preceding surgery and the type of the succeeding surgery.  
  * FR-SDST-003: The system should allow setup times to be potentially dependent on the specific operating room (if this level of detail is in scope for the thesis).  
  * FR-SDST-004: The system shall provide an interface to manage different surgery "types" used for SDST calculations.  
* **Scheduling Operations (enhancements):**  
  * FR-SCHED-ENH-001: When a surgery is scheduled or moved, the system shall automatically calculate and display the required setup time based on the preceding surgery in the sequence for that OR.  
  * FR-SCHED-ENH-002: The system shall clearly visualize total block time for a surgery, including its processing time and the preceding setup time.  
* **Optimization Engine Functionality:**  
  * FR-OPTIM-001: The system's optimization engine shall accept parameters to define the relative importance of various objectives (e.g., minimizing makespan, minimizing overtime, maximizing OR utilization, minimizing total setup times). (Reflects the need for tunable objective functions mentioned in the report).  
  * FR-OPTIM-002: The optimization engine's primary goal shall be to find a near-optimal schedule that minimizes a composite objective function, explicitly including penalties or costs associated with total sequence-dependent setup times.  
  * FR-OPTIM-003: The system shall handle resource constraints (ORs, surgeons, staff, equipment) and temporal constraints (earliest start, due dates) in conjunction with SDST when optimizing schedules.  
  * FR-OPTIM-004: The optimization process should be executable on demand by authorized users.  
* **Reporting (enhancements):**  
  * FR-REPORT-ENH-001: The system shall generate reports detailing the total setup time incurred per OR, per day/week.  
  * FR-REPORT-ENH-002: Reports should allow analysis of how different surgery sequences impact overall setup times and OR efficiency.

**Section 5: Non-Functional Requirements**

* **5.1 Performance Requirements:**  
  * NFR-PERF-ENH-001: Given the complexity of Tabu Search with SDST, the optimization of a typical day's schedule (e.g., X surgeries, Y ORs) shall be completed within Z minutes (where X, Y, Z are defined for the thesis scope, e.g., 20 surgeries, 5 ORs, 5-10 minutes). This needs careful consideration based on the report's discussion on computational complexity.  
* **5.8 Data Integrity:**  
  * NFR-DATA-ENH-001: The system shall ensure the accuracy and consistency of the SDST matrix, as errors here would significantly impact schedule quality.

This detailed report on Tabu Search for SDST provides a strong foundation for these more specific requirements. The SRD will now more accurately reflect the core challenge your thesis aims to solve.

