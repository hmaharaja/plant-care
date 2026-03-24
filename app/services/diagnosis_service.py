import os
import json
import heapq
import google.generativeai as genai
from typing import Dict, List, Optional
from rapidfuzz import fuzz
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import JSONB

from app.models.diagnosis import Diagnosis
from app.enums import DiagnosisSource


SIMILARITY_THRESHOLD = 80
MIN_PRECISION = 0.5
MAX_SYMPTOMS_FOR_RULE_ENGINE = 7

# configure genai model
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def get_prompt(plant_name: str, species: str, symptoms: list[str], additional_notes: Optional[str] = None) -> str:
    prompt = f"""
    You are a plant disease expert. Given the following plant information, return ONLY a JSON array with no markdown, no backticks, and no explanation.

    Plant name: {plant_name}
    Species: {species}
    Symptoms: {', '.join(symptoms)}
    Additional notes: {additional_notes or 'None'}

    Return a JSON array of the top 3 most likely diagnoses in this exact format:
    [
        {{
            "name": "diagnosis name",
            "likelihood": 0.85,
            "description": "brief description of the condition",
            "treatments": ["treatment 1", "treatment 2"]
        }}
    ]

    likelihood must be a float between 0 and 1. Return only the JSON array, nothing else.
    """
    return prompt


def get_gemini_model() -> genai.GenerativeModel:
    return genai.GenerativeModel(os.getenv("GEMINI_MODEL"))


def llm_based_diagnose(
    plant_id: int,
    plant_name: str,
    species: str,
    symptoms: list[str],
    additional_notes: Optional[str] = None
) -> list[dict]:
    prompt = get_prompt(plant_name, species, symptoms, additional_notes)
    model = get_gemini_model()

    response = model.generate_content(prompt)
    try:
        results = json.loads(response.text)
    except json.JSONDecodeError:
        raise ValueError(f"LLM returned invalid JSON: {response.text}")
    
    for result in results:
        result["id"] = plant_id
        result["source"] = DiagnosisSource.LLM
        result["verified"] = False
    
    return results


def rule_based_diagnose(
    plant_id: int,
    symptoms: List[str],
    db: Session,
    min_matches: int = 1
) -> List[Dict]:
    diagnoses_for_plant = db.query(Diagnosis).filter(
        Diagnosis.plant_ids.cast(JSONB).contains([plant_id])
    ).all()

    # Min-heap to keep top 3 results
    heap = []

    for diagnosis in diagnoses_for_plant:
        diagnosis_symptoms = diagnosis.symptoms or []
        if not diagnosis_symptoms:
            continue

        # Count fuzzy matches
        matches = 0
        for submitted_symptom in symptoms:
            for diagnosis_symptom in diagnosis_symptoms:
                if fuzz.ratio(submitted_symptom.lower(), diagnosis_symptom.lower()) >= SIMILARITY_THRESHOLD:
                    matches += 1
                    break  # Count each submitted symptom once

        if matches < min_matches:
            continue

        precision = matches / len(diagnosis_symptoms)
        likelihood = matches / len(symptoms) if symptoms else 0

        # Skip diagnoses that don't meet minimum precision threshold
        if precision < MIN_PRECISION:
            continue

        result = {
            "id": diagnosis.id,
            "name": diagnosis.name,
            "description": diagnosis.description,
            "treatments": diagnosis.treatments,
            "precision": precision,
            "likelihood": likelihood,
            "score": precision * likelihood,
            "source": DiagnosisSource.RULE_ENGINE,
            "verified": True
        }

        heapq.heappush(heap, (result["score"], result["id"], result))
        if len(heap) > 3:
            heapq.heappop(heap)

    # Extract and sort by score descending
    results = [item[2] for item in sorted(heap, key=lambda x: x[0], reverse=True)]
    return results


def diagnose(
    plant_id: int,
    plant_name: str,
    species: str,
    symptoms: List[str],
    db: Session,
    additional_notes: Optional[str] = None
) -> List[Dict]:
    """Try rule-based diagnosis, fall back to LLM if needed."""

    # Use rule engine if symptoms count is within threshold
    if len(symptoms) <= MAX_SYMPTOMS_FOR_RULE_ENGINE:
        rule_results = rule_based_diagnose(plant_id, symptoms, db)
        if rule_results:
            return rule_results

    # Fall back to LLM-based diagnosis
    return llm_based_diagnose(plant_id, plant_name, species, symptoms, additional_notes)


