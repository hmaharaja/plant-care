from enum import Enum
class DiagnosisSource(Enum):
    LLM = "LLM"
    RULE_ENGINE = "DB_RULE_ENGINE"