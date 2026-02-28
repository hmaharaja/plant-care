# Plant Care App

A web application for managing your plant collection and tracking their care schedules.

## Features

- **Plant Management**: Store and manage your plant collection with detailed information
- **Care Notes**: Track watering, fertilizing, repotting, and other care activities
- **User Authentication**: Secure login to personalize your experience
- **Saved Plants**: Keep a personal list of your plants
- **Notifications**: Reminders for plant care tasks (coming soon)

## Tech Stack

- **Backend**: Node.js with Express
- **Database**: PostgreSQL
- **Frontend**: [To be determined]

## Database Schema

### Plants Table

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique identifier |
| name | VARCHAR(255) | Plant name |
| species | VARCHAR(255) | Plant species |
| location | VARCHAR(255) | Where the plant is located |
| image_url | TEXT | URL to plant image |
| created_at | TIMESTAMP | When the plant was added |

### Care Notes Table

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique identifier |
| plant_id | INTEGER | Foreign key to plants |
| care_type | VARCHAR(50) | Type of care (water, fertilize, etc.) |
| notes | TEXT | Additional notes |
| performed_at | TIMESTAMP | When the care was performed |

### Users Table

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique identifier |
| email | VARCHAR(255) | User email (unique) |
| password_hash | VARCHAR(255) | Hashed password |
| created_at | TIMESTAMP | When the user registered |

## API Endpoints

[To be determined - endpoints pending decision]

## Getting Started

1. Clone the repository
2. Set up PostgreSQL database
3. Configure environment variables
4. Install dependencies and run

### Prerequisites

- Node.js
- PostgreSQL

### Installation

```bash
# Install dependencies
npm install

# Set up database
# (database setup instructions pending)

# Start the server
npm start
```

## License

MIT
