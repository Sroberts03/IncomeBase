import unittest
from pydantic import ValidationError
from models.file_review_schema import IndividualFileResult

class TestModels(unittest.TestCase):
    def test_individual_file_result_confidence_validation(self):
        # Valid confidence
        result = IndividualFileResult(
            file_id="f1",
            status="approved",
            borrower_message="Good",
            reasoning="Passed",
            confidence=0.9
        )
        self.assertEqual(result.confidence, 0.9)
        
        # Too low
        with self.assertRaises(ValidationError):
            IndividualFileResult(
                file_id="f1",
                status="approved",
                borrower_message="Good",
                reasoning="Passed",
                confidence=-0.1
            )
            
        # Too high
        with self.assertRaises(ValidationError):
            IndividualFileResult(
                file_id="f1",
                status="approved",
                borrower_message="Good",
                reasoning="Passed",
                confidence=1.1
            )

    def test_individual_file_result_status_literal(self):
        # Invalid status
        with self.assertRaises(ValidationError):
            IndividualFileResult(
                file_id="f1",
                status="pending", # Only approved/rejected allowed
                borrower_message="Good",
                reasoning="Passed",
                confidence=0.5
            )

if __name__ == "__main__":
    unittest.main()
