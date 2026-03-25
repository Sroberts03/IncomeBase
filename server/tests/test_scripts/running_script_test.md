# Running Tests Scripts

## to run file_review_classifier_pipeline.py
### make sure to first run this in your terminal to get test files:
python tests/test_scripts/create_test_files.py  
### after that run this in your terminal:
python tests/test_scripts/file_review_classifier_pipeline.py

### Expected output:
🚀 Sending 3 files for Batch Review...

--- Result for: blurry_file.jpg ---
Status: REJECTED
Message: Document is blank or unreadable.
🛑 Skipping Classification for blurry_file.jpg.

--- Result for: perfect_statement.jpg ---
Status: APPROVED
Message: Document is clear and relevant for analysis.
🔍 Document approved. Running Classifier for perfect_statement.jpg...
Classification: bank_statement
Source: bank

--- Result for: wrong_type_w2.jpg ---
Status: REJECTED
Message: Document is outdated with a date from the previous year.
🛑 Skipping Classification for wrong_type_w2.jpg.
