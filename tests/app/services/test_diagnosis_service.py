import unittest
from unittest.mock import MagicMock

from app.services.diagnosis_service import rule_based_diagnose


def create_mock_db(diagnoses):
    """Helper to create a mock db that simulates .contains() filter"""
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.all.side_effect = lambda: [
        d for d in diagnoses if d._plant_id_match
    ]

    mock_query.filter.return_value = mock_filter
    mock_db = MagicMock()
    mock_db.query.return_value = mock_query
    return mock_db


class TestRuleBasedDiagnose(unittest.TestCase):
    # Test case 1: Plant id isn't in the db
    def test_plant_id_not_in_db(self):
        mock_diagnosis = MagicMock()
        mock_diagnosis._plant_id_match = False  # Won't match plant_id=999
        mock_diagnosis.id = 1
        mock_diagnosis.name = "Root Rot"
        mock_diagnosis.description = "Too much water"
        mock_diagnosis.symptoms = ["yellow leaves", "mushy roots"]
        mock_diagnosis.treatments = ["Reduce watering"]
        mock_diagnosis.plant_ids = [1]

        mock_db = create_mock_db([mock_diagnosis])
        result = rule_based_diagnose(plant_id=999, symptoms=["yellow leaves"], db=mock_db)
        self.assertEqual(result, [])

    # Test case 2: Plant id doesn't match (diagnoses have different plant_ids)
    def test_plant_id_doesnt_match(self):
        mock_diagnosis = MagicMock()
        mock_diagnosis._plant_id_match = False  # Won't match plant_id=1
        mock_diagnosis.id = 1
        mock_diagnosis.name = "Root Rot"
        mock_diagnosis.description = "Too much water"
        mock_diagnosis.symptoms = ["yellow leaves", "mushy roots"]
        mock_diagnosis.treatments = ["Reduce watering"]
        mock_diagnosis.plant_ids = [5, 10]  # Different from plant_id=1

        mock_db = create_mock_db([mock_diagnosis])
        result = rule_based_diagnose(plant_id=1, symptoms=["yellow leaves"], db=mock_db)
        self.assertEqual(result, [])

    # Test case 3: Multiple plant id matches but none of the same symptoms
    def test_multiple_plant_matches_no_symptom_match(self):
        mock_diagnosis1 = MagicMock()
        mock_diagnosis1._plant_id_match = True
        mock_diagnosis1.id = 1
        mock_diagnosis1.name = "Root Rot"
        mock_diagnosis1.description = "Too much water"
        mock_diagnosis1.symptoms = ["yellow leaves", "mushy roots"]
        mock_diagnosis1.treatments = ["Reduce watering"]
        mock_diagnosis1.plant_ids = [1, 2]

        mock_diagnosis2 = MagicMock()
        mock_diagnosis2._plant_id_match = True
        mock_diagnosis2.id = 2
        mock_diagnosis2.name = "Spider Mites"
        mock_diagnosis2.description = "Pest infestation"
        mock_diagnosis2.symptoms = ["webbing", "tiny bugs"]
        mock_diagnosis2.treatments = ["Insecticide"]
        mock_diagnosis2.plant_ids = [1, 3]

        mock_db = create_mock_db([mock_diagnosis1, mock_diagnosis2])
        result = rule_based_diagnose(plant_id=1, symptoms=["brown spots"], db=mock_db, min_matches=1)
        self.assertEqual(result, [])

    # Test case 4: Plant id matches and symptoms match exactly out of one result
    def test_exact_match_one_result(self):
        mock_diagnosis = MagicMock()
        mock_diagnosis._plant_id_match = True
        mock_diagnosis.id = 1
        mock_diagnosis.name = "Root Rot"
        mock_diagnosis.description = "Too much water"
        mock_diagnosis.symptoms = ["yellow leaves", "mushy roots"]
        mock_diagnosis.treatments = ["Reduce watering"]
        mock_diagnosis.plant_ids = [1]

        mock_db = create_mock_db([mock_diagnosis])
        result = rule_based_diagnose(
            plant_id=1,
            symptoms=["yellow leaves", "mushy roots"],
            db=mock_db
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Root Rot")
        self.assertEqual(result[0]["precision"], 1.0)
        self.assertEqual(result[0]["likelihood"], 1.0)
        self.assertEqual(result[0]["score"], 1.0)

    # Test case 5: Plant id and symptoms match exactly out of multiple results
    def test_exact_match_multiple_results(self):
        mock_diagnosis1 = MagicMock()
        mock_diagnosis1._plant_id_match = True
        mock_diagnosis1.id = 1
        mock_diagnosis1.name = "Root Rot"
        mock_diagnosis1.description = "Too much water"
        mock_diagnosis1.symptoms = ["yellow leaves", "mushy roots"]
        mock_diagnosis1.treatments = ["Reduce watering"]
        mock_diagnosis1.plant_ids = [1]

        mock_diagnosis2 = MagicMock()
        mock_diagnosis2._plant_id_match = True
        mock_diagnosis2.id = 2
        mock_diagnosis2.name = "Nitrogen Deficiency"
        mock_diagnosis2.description = "Lack of nutrients"
        mock_diagnosis2.symptoms = ["yellow leaves", "stunted growth"]
        mock_diagnosis2.treatments = ["Add fertilizer"]
        mock_diagnosis2.plant_ids = [1]

        mock_db = create_mock_db([mock_diagnosis1, mock_diagnosis2])
        result = rule_based_diagnose(
            plant_id=1,
            symptoms=["yellow leaves", "mushy roots"],
            db=mock_db
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Root Rot")  # Higher precision (2/2 vs 1/2)

    # Test case 6: Match out of partial matches
    def test_partial_matches(self):
        mock_diagnosis1 = MagicMock()
        mock_diagnosis1._plant_id_match = True
        mock_diagnosis1.id = 1
        mock_diagnosis1.name = "Root Rot"
        mock_diagnosis1.description = "Too much water"
        mock_diagnosis1.symptoms = ["yellow leaves", "mushy roots", "foul smell"]
        mock_diagnosis1.treatments = ["Reduce watering"]
        mock_diagnosis1.plant_ids = [1]

        mock_diagnosis2 = MagicMock()
        mock_diagnosis2._plant_id_match = True
        mock_diagnosis2.id = 2
        mock_diagnosis2.name = "Underwatering"
        mock_diagnosis2.description = "Lack of water"
        mock_diagnosis2.symptoms = ["drooping leaves", "crispy edges"]
        mock_diagnosis2.treatments = ["Water more"]
        mock_diagnosis2.plant_ids = [1]

        mock_db = create_mock_db([mock_diagnosis1, mock_diagnosis2])
        result = rule_based_diagnose(
            plant_id=1,
            symptoms=["yellow leaves", "mushy root"],  # "mushy root" fuzzy matches "mushy roots"
            db=mock_db,
            min_matches=1
        )

        self.assertGreaterEqual(len(result), 1)
        self.assertIn(result[0]["name"], ["Root Rot", "Underwatering"])

    # Test case 7: Trap diagnosis with too many symptoms fails precision check
    def test_trap_diagnosis_fails_precision(self):
        # This diagnosis has 10 symptoms - submitting 1 symptom won't meet precision threshold
        mock_diagnosis1 = MagicMock()
        mock_diagnosis1._plant_id_match = True
        mock_diagnosis1.id = 1
        mock_diagnosis1.name = "Trap Diagnosis"
        mock_diagnosis1.description = "Too many symptoms"
        mock_diagnosis1.symptoms = [
            "yellow leaves", "brown tips", "drooping", "spots", "wilting",
            "curling", "holes", "discoloration", "stunted", "falling"
        ]
        mock_diagnosis1.treatments = ["Various"]
        mock_diagnosis1.plant_ids = [1]

        mock_diagnosis2 = MagicMock()
        mock_diagnosis2._plant_id_match = True
        mock_diagnosis2.id = 2
        mock_diagnosis2.name = "Simple Issue"
        mock_diagnosis2.description = "Simple problem"
        mock_diagnosis2.symptoms = ["yellow leaves"]
        mock_diagnosis2.treatments = ["Simple fix"]
        mock_diagnosis2.plant_ids = [1]

        mock_db = create_mock_db([mock_diagnosis1, mock_diagnosis2])

        result = rule_based_diagnose(
            plant_id=1,
            symptoms=["yellow leaves"],  # Only 1 symptom
            db=mock_db,
            min_matches=1
        )

        # Trap diagnosis: 1 match / 10 symptoms = 0.1 precision (< MIN_PRECISION, filtered out)
        # Simple issue: 1 match / 1 symptom = 1.0 precision
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Simple Issue")


if __name__ == '__main__':
    unittest.main()