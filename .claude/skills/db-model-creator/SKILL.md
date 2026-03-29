# SQLAlchemy Models Skill

## Overview
This skill guides Claude through creating or updating SQLAlchemy models for a FastAPI + PostgreSQL project.

## Critical Rules
These rules override all other instructions in this skill.

- NEVER modify a model without showing the user the full updated model first and receiving explicit approval
- NEVER remove existing columns without explicit permission from the user
- NEVER change a primary key or foreign key without explicit permission
- ALWAYS generate a migration after a model change — never modify a model and leave the DB out of sync
- If anything looks ambiguous about the change, STOP and ask before proceeding
- ALWAYS make sure there is a detailed schema provided by the user, including each field and its data types, primary/foreign keys, constraints, and any other relationships are defined.

---

## Project Context
- **Models location:** `app/models/`
- **Base class:** `from app.database import Base`
- **Enums location:** `app/enums.py`
- **Python version:** 3.12+
- **Database:** PostgreSQL

---

## Critical Patterns

### Timestamps — ALWAYS use this pattern
```python
from datetime import datetime, timezone

# CORRECT
created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
updated_at = Column(DateTime, 
    default=lambda: datetime.now(timezone.utc), 
    onupdate=lambda: datetime.now(timezone.utc))

# NEVER use these — deprecated in Python 3.12
created_at = Column(DateTime, default=datetime.utcnow)       # WRONG
created_at = Column(DateTime, default=datetime.utcnow())     # WRONG
```

The `lambda` wrapper is required because `default` is evaluated at row insertion time, not at class definition time.

### Enums
```python
# Define in app/enums.py using UPPERCASE values
from enum import Enum

class EventType(str, Enum):
    WATERED = "WATERED"
    FERTILIZED = "FERTILIZED"

# Use in models
from sqlalchemy import Enum as SQLEnum
from app.enums import EventType

event_type = Column(SQLEnum(EventType), nullable=False)
```

**Important:** Always define enum values in UPPERCASE to match Alembic autogenerate output and avoid case mismatch errors during migrations.

### Relationships
```python
# Always define both sides of a relationship
# Parent side
user_plants = relationship("UserPlant", back_populates="user")

# Child side
user = relationship("User", back_populates="user_plants")
```

### Unique Constraints
```python
from sqlalchemy import UniqueConstraint

class UserPlant(Base):
    __tablename__ = "user_plants"
    # ... columns ...

    __table_args__ = (
        UniqueConstraint('user_id', 'plant_id', name='uq_user_plant'),
    )
```

`__table_args__` always goes at the bottom of the class, after columns and relationships. Always a tuple — note the trailing comma if only one constraint.

### JSON columns
```python
# For lists
symptoms = Column(JSON, default=list)   # CORRECT
symptoms = Column(JSON, default=[])     # WRONG — mutable default

# For dicts
metadata = Column(JSON, default=dict)   # CORRECT
```

### Nullable vs non-nullable
```python
# Required fields
name = Column(String, nullable=False)

# Optional fields
nickname = Column(String, nullable=True)   # explicit is better
notes = Column(String)                     # nullable=True by default
```

---

## Model Template
Use this as a starting point for new models:

```python
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class MyModel(Base):
    __tablename__ = "my_models"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    
    # Fields
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    notes = Column(String, nullable=True)
    
    # Timestamps — always use this pattern
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="my_models")

    # Constraints — always at the bottom
    # __table_args__ = (
    #     UniqueConstraint('user_id', 'name', name='uq_user_name'),
    # )
```

---

## Checklist for every model change
- [ ] Timestamps use `lambda: datetime.now(timezone.utc)` pattern
- [ ] Enums defined in `app/enums.py` with UPPERCASE values
- [ ] Both sides of every relationship are defined
- [ ] `__table_args__` is at the bottom of the class if constraints are needed
- [ ] JSON columns use `default=list` or `default=dict`, not mutable defaults
- [ ] New model is imported in `alembic/env.py`
- [ ] Migration generated and reviewed after every change