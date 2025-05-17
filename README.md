# AI-Powered Surgical Scheduling Optimizer

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4%2B-green.svg)](https://www.mongodb.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A capstone project aimed at solving the complex problem of surgical scheduling in healthcare environments using Python, MongoDB, and a Tabu Search metaheuristic.

This system considers crucial factors such as operating room availability, equipment, surgeon specializations and preferences, surgery urgency, and overall efficiency. Key integrations include **Google Calendar** for real-time updates and an **automated email notification system**.

---

## Features

* **Automated Surgery Scheduling**
  Optimizes surgery assignments to time slots, operating rooms, and surgeons based on multi-objective criteria.

* **Tabu Search Optimization**
  Uses Tabu Search to find near-optimal schedules while minimizing conflicts and maximizing utilization.

* **Resource Management**
  Tracks OR availability, equipment, and staff.

* **Constraint Handling**
  Handles availability, room suitability, setup/cleanup times, and equipment needs.

* **KPI-Based Evaluation**
  Evaluates schedules using:

  * Room Utilization Efficiency
  * Equipment Utilization
  * Surgeon Workload Balance
  * Surgeon Preference Satisfaction
  * Operational Cost Minimization

* **MongoDB Backend**
  Stores scheduling entities, constraints, and preferences.

* **Google Calendar Integration**
  Syncs schedules to surgeons’ calendars.

* **Notification System**
  Sends email alerts on changes and daily summaries.

* **Modular Architecture**
  Service-oriented structure for maintainability.

* **Data Seeding & Setup**
  Scripts included for sample data and database index creation.

---

## Technologies Used

* **Language:** Python 3.9+
* **Database:** MongoDB 4.4+
* **Algorithm:** Tabu Search
* **Libraries:**

  * `Flask`
  * `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`
  * `python-dotenv`
  * `requests`

---

## Project Structure

```
├── services/                      # Domain logic (appointments, notifications, etc.)
├── utils/                         # KPI calculators and helper utilities
├── .env.example                   # Template for environment variables
├── consent_handeller.py          # Google OAuth flow
├── daily_notifications.py        # Daily email summary script
├── db_config.py                  # MongoDB config and connection
├── initialize_data.py            # Initial data population
├── manage_duplicates.py          # Duplicate record handler
├── models.py                     # MongoDB document models
├── mongodb_transaction_manager.py# MongoDB transaction context manager
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── scheduling_optimizer.py       # Tabu Search execution script
├── scheduling_services.py        # Scheduling notification logic
├── scheduling_utils.py           # Availability checks and constraints
├── seed_database.py              # DB seeding script
├── setup_database.py             # DB index creation
├── solution.py                   # Evaluation logic and solution structure
└── tabu_list.py                  # Tabu list implementation
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites

* Python 3.9+
* MongoDB instance (local or Atlas)
* Git

### 2. Clone the Repository

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

### 3. Set Up a Virtual Environment (Recommended)

```bash
python -m venv venv
# Activate:
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

* Copy `.env.example` to `.env`
* Add/update the following:

```dotenv
MONGO_URI=mongodb://localhost:27017/
MONGO_DATABASE_NAME=surgery_scheduling_db

# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_app_password
```

### 6. Google Calendar API Setup

* Go to [Google Cloud Console](https://console.cloud.google.com/)
* Create a project and enable the **Google Calendar API**
* Create **OAuth 2.0 credentials** (Desktop)
* Download the `credentials.json` and place it in the root directory

#### Authorize the Application

```bash
python consent_handeller.py
```

> This opens a browser to authenticate and generate `token.json`

> **Security Note**: Add `credentials.json` and `token.json` to `.gitignore`

---

## Database Initialization

Ensure your MongoDB is running and `MONGO_URI` is set correctly in `.env`.

### 1. Create Indexes

```bash
python setup_database.py
```

### 2. Seed Sample Data

```bash
python seed_database.py
```

---

## How to Run

### Run the Scheduler

```bash
python scheduling_optimizer.py
```

#### Output:

* Console logs showing:

  * Initialization steps
  * Tabu Search progress
  * Final schedule metrics
* MongoDB updates (e.g., surgery assignments)
* Calendar events created if Google API is configured

---

## Run Daily Notifications

```bash
python daily_notifications.py
```

> Ensure SMTP settings are correct in `.env`.

---

## Algorithm Spotlight: Tabu Search

A metaheuristic approach tailored for complex scheduling:

* **Solution Representation**: Surgery-room-time-surgeon assignments
* **Neighbor Moves**:

  * Reassign surgery to another time/room
  * Swap surgeries
  * Shift start times
* **Tabu List**: Prevents short-term cycles
* **Evaluation Function**:

  * Room/Equipment Utilization
  * Surgeon Idle Time
  * Preference Satisfaction
  * Cost Minimization
* **Termination**: Iteration count or stagnation

---



As the primary developer, I contributed to:

* **Algorithm Design**: Tabu Search core logic and constraints handling
* **Backend Structure**: Modular service-oriented architecture
* **MongoDB Schema & Integration**: Including seeding and indexing
* **Google Calendar Sync**: OAuth + real-time updates
* **Notification System**: Email alerts and daily summaries

---

## Future Enhancements

* Web UI with Flask/Django + React/Vue
* Real-time conflict detection
* ML models for duration prediction
* Advanced constraint configurations
* Dockerization
* Comprehensive test suite with `pytest`

---

## Author

* **LinkedIn:** [Your LinkedIn](https://linkedin.com/in/your-profile)
* **GitHub:** [Your GitHub](https://github.com/your-username)

---

## License

This project is licensed under the **MIT License**. See the `LICENSE.md` file for details.

