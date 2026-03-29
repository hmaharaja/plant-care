from enum import Enum


class DiagnosisSource(str, Enum):
    LLM = "LLM"
    RULE_ENGINE = "DB_RULE_ENGINE"


class LightRequirement(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    BRIGHT_INDIRECT = "BRIGHT_INDIRECT"
    FULL_SUN = "FULL_SUN"


class SoilCondition(str, Enum):
    SANDY = "SANDY"
    LOAM = "LOAM"
    CLAY = "CLAY"
    PEAT = "PEAT"
    WELL_DRAINING = "WELL_DRAINING"
    WELL_DRAINING_AERATED = "WELL_DRAINING_AERATED"
    CACTI_MIX = "CACTI"


class HardinessZone(str, Enum):
    ZONE_1 = "1"
    ZONE_2 = "2"
    ZONE_3 = "3"
    ZONE_4 = "4"
    ZONE_5 = "5"
    ZONE_6 = "6"
    ZONE_7 = "7"
    ZONE_8 = "8"
    ZONE_9 = "9"
    ZONE_10 = "10"
    ZONE_11 = "11"
    ZONE_12 = "12"
    ZONE_13 = "13"


class Hemisphere(str, Enum):
    NORTHERN = "NORTHERN"
    SOUTHERN = "SOUTHERN"