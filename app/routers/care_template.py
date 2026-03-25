from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.plant import CareTemplate, Plant
from app.schemas.care_template import CareTemplateCreate, CareTemplatePatch, CareTemplateResponse

router = APIRouter(prefix="/api/v1/care_templates", tags=["care_templates"])

# TODO: Add rate limiting to this endpoint


def get_plant_or_404(db: Session, plant_id: int) -> Plant:
    """Get plant by ID or raise 404."""
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant not found"
        )
    return plant


def get_care_template_or_404(db: Session, plant_id: int) -> CareTemplate:
    """Get care template by plant ID or raise 404."""
    care_template = db.query(CareTemplate).filter(
        CareTemplate.plant_id == plant_id
    ).first()
    if not care_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Care template not found for this plant"
        )
    return care_template


@router.get("/{plant_id}", response_model=CareTemplateResponse)
def get_care_template_by_plant(
    plant_id: int,
    db: Session = Depends(get_db),
):
    get_plant_or_404(db, plant_id)
    care_template = get_care_template_or_404(db, plant_id)
    return care_template


@router.patch("/{plant_id}", response_model=CareTemplateResponse)
def patch_care_template(
    plant_id: int,
    patch_data: CareTemplatePatch,
    db: Session = Depends(get_db),
):
    # TODO: Add admin protection

    get_plant_or_404(db, plant_id)
    care_template = get_care_template_or_404(db, plant_id)

    # Build update dict with only provided (non-None) fields
    update_data = patch_data.model_dump(exclude_unset=True)

    # If no fields to update, return current template
    if not update_data:
        return care_template

    # Auto-increment template_version
    update_data["template_version"] = care_template.template_version + 1

    # Apply updates
    for field, value in update_data.items():
        setattr(care_template, field, value)

    db.commit()
    db.refresh(care_template)

    return care_template


@router.post("", response_model=CareTemplateResponse, status_code=status.HTTP_201_CREATED)
def post_care_template(
    care_template_data: CareTemplateCreate,
    db: Session = Depends(get_db),
):
    # TODO: Add admin protection

    get_plant_or_404(db, care_template_data.plant_id)

    # Check if a template already exists for this plant_id
    existing = db.query(CareTemplate).filter(
        CareTemplate.plant_id == care_template_data.plant_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A care template already exists for this plant"
        )

    # Create the new care template
    care_template = CareTemplate(
        plant_id=care_template_data.plant_id,
        template_version=care_template_data.template_version,
        species=care_template_data.species,
        hardiness_zone=care_template_data.hardiness_zone,
        light_requirements=care_template_data.light_requirements,
        default_watering_interval_days=care_template_data.default_watering_interval_days,
        soil_conditions=care_template_data.soil_conditions,
        issue_ids=care_template_data.issue_ids,
    )

    db.add(care_template)
    db.commit()
    db.refresh(care_template)

    return care_template