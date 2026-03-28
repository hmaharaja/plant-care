from enum import Enum


class DiagnosisSource(str, Enum):
    LLM = "LLM"
    RULE_ENGINE = "DB_RULE_ENGINE"


class LightRequirement(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    BRIGHT_INDIRECT = "bright_indirect"
    FULL_SUN = "full_sun"


class SoilCondition(str, Enum):
    SANDY = "sandy"
    LOAM = "loam"
    CLAY = "clay"
    PEAT = "peat"
    WELL_DRAINING = "well_draining"
    WELL_DRAINING_AERATED = "well_draining_aerated"
    CACTI_MIX = "cacti"


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
    NORTHERN = "northern"
    SOUTHERN = "southern"