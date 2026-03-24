import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from app.services.diagnosis_service import MAX_SYMPTOMS_FOR_RULE_ENGINE, rule_based_diagnose, llm_based_diagnose, diagnose, DiagnosisSource


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
        self.assertEqual(result[0]["name"], "Root Rot")

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



class TestLLMBasedDiagnose(unittest.TestCase):
    pass


class TestDiagnose(unittest.TestCase):
    
    @patch(f"{diagnose.__module__}.rule_based_diagnose")
    @patch(f"{diagnose.__module__}.llm_based_diagnose")
    def test_should_use_rule_engine(self, mock_llm_based_diagnose, mock_rule_based_diagnose):
        """Test when the rule engine is sufficient"""
        mock_plant_id = 1
        mock_plant_name = "snakeplant"
        mock_species = "sanseveria"
        mock_symptoms = ["yellow leaves", "mushy roots", "slow growth"]
        mock_db_session = MagicMock(spec=Session)
        
        mock_rule_based_diagnose.return_value = [{
            "id": mock_plant_id,
            "name": "Overwatering",
            "description": "Snake plants (sanseveria) are native to drier climates and dont like too much water",
            "treatments": ["Let the soil dry out from the top 1-2 inches before watering", "repotting"],
            "precision": 0.67,
            "likelihood": 90,
            "score": 0.67 * 90,
            "source": DiagnosisSource.RULE_ENGINE,
            "verified": True
        }]
        
        result = diagnose(mock_plant_id, mock_plant_name, mock_species, mock_symptoms, mock_db_session)
        
        assert result == mock_rule_based_diagnose.return_value
        mock_rule_based_diagnose.assert_called_once_with(mock_plant_id, mock_symptoms, mock_db_session)
        mock_llm_based_diagnose.assert_not_called()
    
    
    @patch(f"{diagnose.__module__}.rule_based_diagnose")
    @patch(f"{diagnose.__module__}.llm_based_diagnose")
    def test_boundary_symptom_count(self, mock_llm_based_diagnose, mock_rule_based_diagnose):
        """Test that MAX_SYMPTOMS_FOR_RULE_ENGINE symptoms still uses rule engine"""
        mock_plant_id = 1
        mock_plant_name = "snakeplant"
        mock_species = "sanseveria"
        mock_symptoms = ["symptom"] * MAX_SYMPTOMS_FOR_RULE_ENGINE
        
        mock_db_session = MagicMock(spec=Session)
        
        mock_rule_based_diagnose.return_value = [{
            "id": mock_plant_id,
            "name": "Overwatering",
            "description": "Snake plants (sanseveria) are native to drier climates and dont like too much water",
            "treatments": ["Let the soil dry out from the top 1-2 inches before watering", "repotting"],
            "precision": 0.67,
            "likelihood": 90,
            "score": 0.67 * 90,
            "source": DiagnosisSource.RULE_ENGINE,
            "verified": True
        }]
        
        result = diagnose(mock_plant_id, mock_plant_name, mock_species, mock_symptoms, mock_db_session)

        assert result == mock_rule_based_diagnose.return_value
        mock_rule_based_diagnose.assert_called_once_with(mock_plant_id, mock_symptoms, mock_db_session)
        mock_llm_based_diagnose.assert_not_called()
    
    
    @patch(f"{diagnose.__module__}.rule_based_diagnose")
    @patch(f"{diagnose.__module__}.llm_based_diagnose")
    def test_should_use_llm_too_many_symptoms(self, mock_llm_based_diagnose, mock_rule_based_diagnose):
        """Test when the llm based diagnosis should be called 
        because there are too many symptoms the user input"""
        mock_plant_id = 1
        mock_plant_name = "snakeplant"
        mock_species = "sanseveria"
        mock_symptoms = ["yellow leaves", "mushy roots", "slow growth",
                         "dying leaves", "wet soil", "spots on leaves", "weak stems"
                         "drooping"]
        
        mock_db_session = MagicMock(spec=Session)
        
        mock_llm_based_diagnose.return_value = [{
            "id": mock_plant_id,
            "name": "Overwatering",
            "description": "Snake plants (sanseveria) are native to drier climates and dont like too much water",
            "treatments": ["Let the soil dry out from the top 1-2 inches before watering", "repotting"],
            "likelihood": 90,
            "source": DiagnosisSource.LLM,
            "verified": False
        }]
        
        
        result = diagnose(mock_plant_id, mock_plant_name, mock_species, mock_symptoms, mock_db_session)
        assert result == mock_llm_based_diagnose.return_value
        mock_llm_based_diagnose.assert_called_once_with(mock_plant_name, mock_species, mock_symptoms, None)
        mock_rule_based_diagnose.assert_not_called()
    
    
    @patch(f"{diagnose.__module__}.rule_based_diagnose")
    @patch(f"{diagnose.__module__}.llm_based_diagnose")
    def test_should_use_llm_no_rule_based_match(self, mock_llm_based_diagnose, mock_rule_based_diagnose):
        """Test when the rule engine fails and the llm fallback is needed"""
        mock_plant_id = 1
        mock_plant_name = "snakeplant"
        mock_species = "sanseveria"
        mock_symptoms = ["yellow leaves", "mushy roots", "drooping"]
        
        mock_db_session = MagicMock(spec=Session)
        
        mock_rule_based_diagnose.return_value = []
        mock_llm_based_diagnose.return_value = [{
            "id": mock_plant_id,
            "name": "Overwatering",
            "description": "Snake plants (sanseveria) are native to drier climates and dont like too much water",
            "treatments": ["Let the soil dry out from the top 1-2 inches before watering", "repotting"],
            "likelihood": 90,
            "source": DiagnosisSource.LLM,
            "verified": False
        }]
        
        result = diagnose(mock_plant_id, mock_plant_name, mock_species, mock_symptoms, mock_db_session)
        assert result == mock_llm_based_diagnose.return_value
        mock_llm_based_diagnose.assert_called_once_with(mock_plant_name, mock_species, mock_symptoms, None)
        mock_rule_based_diagnose.assert_called_once_with(mock_plant_id, mock_symptoms, mock_db_session)

    
if __name__ == '__main__':
    unittest.main()