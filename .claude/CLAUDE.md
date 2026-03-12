# Plant Health Tracker

## Overview

Plant Health Tracker is a backend-first, configuration-driven plant care system that models plant biological rhythms, care events, and health diagnostics.

The system enables users to:
- Track plants they own with user authentication
- Log care events (watering, fertilizing, repotting, pruning)
- Receive reminders for scheduled care (watering for v1)
- Get diagnostic information for plant health issues
- Pull up detailed plant care information

This is a REST API-focused project with emphasis on backend system design quality.

---

# Core Problem

Plant care is usually manual and inconsistent.

This system:

- Tracks plant care history per user
- Computes when care is due
- Detects possible health issues
- Provides reminders for scheduled care
- Calculates health metrics

---

# V1 Scope

## Functional Requirements

- User account management with login/authentication
- CRUD operations for saved plants (associated to user)
- Care event logging (watered, fertilized, repotted, pruned)
- Job scheduling for care reminders (watering for v1)
- Issue diagnostics with symptom-based diagnosis
- Plant information lookup

## Non-Functional Requirements

- Low latency
- Eventual consistency is acceptable
- High availability for reminders
- Accurate diagnostics and care calculations
- Stateless API with token-based authentication

---

# Architecture

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- pytest for testing

---

# API Endpoints

All endpoints are stateless and require auth token in header. Missing/expired token returns 401.

| Method | Endpoint | Params | Response |
|--------|----------|--------|----------|
| GET | `/api/v1/plant_info` | plant id or name | HTTP status, plant info object |
| POST | `/api/v1/users/saved_plants` | plant id or name | HTTP status |
| POST | `/api/v1/users/events` | plant id/name, event_type, timestamp | HTTP status |
| GET | `/api/v1/users/events` | plant id/name (optional) | HTTP status, list of event objects |
| POST | `/api/v1/plant_diagnoses` | plant id/name, symptom_list | HTTP status, diagnosis results |
| POST | `/api/v1/login` | username, encrypted_password | HTTP status, auth token |

---

# Data Models

## Plant

- id
- name
- species
- template_object_reference

## Plant Care Template Object

- id
- plant_id (FK to plants)
- template_version
- species
- hardiness_zone
- light_requirements (enum)
- watering_interval_days
- issue_ids (list of issue IDs)
- soil_conditions (enum)

## User

- user_id
- username
- hashed_password
- created_at (timestamp)
- user_timezone

## UserPlant

- id
- user_id
- plant_id
- acquired_at (timestamp, optional)
- nickname (optional str)

## Events

- event_id
- user_id
- user_plant_id (FK to user_plants.id)
- timestamp
- event_type (enum: watered, fertilized, repotted, pruned)
- scheduled (bool)
- completed (bool)
- notes (optional str)
- source (enum: user, system)

## Issue

- id
- name
- description
- diagnosis_ids (list of diagnosis IDs)

## Diagnosis

- id
- name
- description
- symptoms (list of strings or symptom IDs)
- treatments (list of strings)

## DiagnosisLog

- id
- user_plant_id
- user_id
- requested_at (timestamp)
- symptoms_submitted (list of strings)
- results (list of objects with diagnosis_id and likelihood_weight scoped to this log)

---

# Key Design Principles

## 1. Configuration-Driven Species Templates

Species definitions are stored as structured YAML or JSON files.

Example:

```yaml
species: monstera
care:
  watering:
    base_interval_days: 7
    winter_multiplier: 1.5
  fertilizer:
    interval_days: 30
  light:
    type: bright_indirect
  sensitivity:
    overwatering: high
```

Templates are loaded at runtime and interpreted by the care engine.

This allows separation of data from logic.


## 2. Derived State Model

Critical design rule:
Do NOT store `next_watering_date`.

Always compute dynamically: `last_watered + adjusted_interval`

All due dates must be derived from:
- Historical events
- Species config
- Seasonal adjustments

This prevents stale state and improves consistency.


## 3. Stateless Authentication

API endpoints are stateless. Auth token must be included in header for each request.

- POST `/api/v1/login` returns auth token
- Token is validated on each protected request
- Missing or expired token returns 401 (redirect to login client-side)


## 4. Event-Based Care Tracking

Events are logged as immutable records:

- watered
- fertilized
- repotted
- pruned

Each event includes:
- event_id
- user_id
- user_plant_id (FK to user_plants)
- timestamp
- event_type
- scheduled (was this a scheduled reminder?)
- completed (did user complete it?)
- notes (optional)
- source (user or system)

Historical logs enable health scoring and diagnosis.


## 5. Rule-Based Diagnosis

- Issues contain references to diagnoses
- Diagnoses contain symptoms and treatments
- User submits symptoms, system returns likelihood-weighted diagnoses
- Results are logged in DiagnosisLog with likelihood scoped to that request

# Workflow Orchestration

### 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ stops or architectural decisions)
- If something goes sideways, stop and re-plan, don't keep pushing
- Write detailed specs upfront to reduce ambiguity

### 2. Self-Improvement Loop
- After any correction from the user: ask the user if you should update `tasks/lessons.md` with the pattern
- Review lessons at session start for the relevant project

