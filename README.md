# Plant Health Tracker

A backend-first, configuration-driven plant care system that models plant biological rhythms, care events, and health diagnostics.

## Features

- **User Authentication**: Secure JWT-based login and registration
- **Plant Management**: CRUD operations for personal plant collections
- **Care Event Logging**: Track watering, fertilizing, repotting, and pruning events
- **Care Templates**: Species-based care instructions with configurable intervals
- **Watering Schedules**: Automated scheduling for plant watering reminders
- **Issue Diagnostics**: Symptom-based plant health diagnosis with AI-powered analysis
- **Plant Information**: Detailed plant care information lookup

## Tech Stack

- **Backend**: Python, FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Authentication**: JWT tokens
- **Task Queue**: Celery + Redis (planned)
- **AI**: Gemini 2.5 Flash (planned)
- **Notifications**: Twilio (planned)

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update user profile

### Plants
- `GET /api/v1/plants` - List user's plants
- `POST /api/v1/plants` - Add a new plant
- `GET /api/v1/plants/{plant_id}` - Get plant details
- `PUT /api/v1/plants/{plant_id}` - Update plant
- `DELETE /api/v1/plants/{plant_id}` - Delete plant

### Care Events
- `GET /api/v1/plants/{plant_id}/events` - Get plant care history
- `POST /api/v1/plants/{plant_id}/events` - Log a care event
- `DELETE /api/v1/events/{event_id}` - Delete a care event

### Care Templates
- `GET /api/v1/care-templates` - List all care templates
- `GET /api/v1/care-templates/{species}` - Get care template for species

### Watering Schedules
- `GET /api/v1/plants/{plant_id}/watering-schedule` - Get watering schedule
- `POST /api/v1/plants/{plant_id}/watering-schedule` - Create/update watering schedule

### Diagnostics
- `POST /api/v1/diagnoses` - Get diagnosis based on symptoms
- `GET /api/v1/diagnoses` - Get diagnosis history

## Key Design Principles

### 1. Configuration-Driven Species Templates
Species definitions are stored as structured data and loaded at runtime. Care intervals and sensitivities are defined per species, allowing separation of data from logic.

### 2. Stateless Authentication
API endpoints are stateless. Auth tokens must be included in the `Authorization` header for each request:
```
Authorization: Bearer <token>
```

### 3. Rule-Based Diagnosis
- Issues contain references to diagnoses
- Diagnoses contain symptoms and treatments
- Users submit symptoms, system returns likelihood-weighted diagnoses

## Database Schema

### Core Models

| Model | Description |
|-------|-------------|
| User | Registered user accounts |
| UserPlant | User's plant collection (many-to-many) |
| Plant | Plant definitions with species info |
| CareTemplate | Species-specific care instructions |
| WateringSchedule | Automated watering schedules |
| Event | Care event history (watered, fertilized, etc.) |
| Issue | Plant health issues |
| Diagnosis | Diagnosis definitions with symptoms |
| DiagnosisLog | Diagnosis history per request |

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis (for Celery)

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database and API credentials

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload

# Start Celery worker (optional)
celery -A app.celery worker --loglevel=info
```

## Development

### Running Tests

```bash
pytest
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Project Structure

```
plant_care/
├── app/
│   ├── main.py           # FastAPI application
│   ├── auth.py          # Authentication utilities
│   ├── database.py      # Database configuration
│   ├── enums.py         # Enum definitions
│   ├── models/          # SQLAlchemy models
│   │   ├── user.py
│   │   ├── plant.py
│   │   ├── event.py
│   │   ├── diagnosis.py
│   │   └── issues.py
│   ├── routers/         # API endpoints
│   │   ├── auth.py
│   │   ├── plants.py
│   │   ├── users.py
│   │   ├── diagnoses.py
│   │   └── care_template.py
│   ├── schemas/         # Pydantic schemas
│   └── services/       # Business logic
├── alembic/             # Database migrations
├── tests/               # Test suite
└── requirements.txt
```

## Remaining Work

1. Watering service implementation
2. Celery + scheduler setup
3. Watering schedule API endpoints
4. OIDC authentication
5. Rate limiting
6. React frontend

## License

MIT