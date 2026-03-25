# Running Tests Scripts

## To run file_review_classifier_pipeline.py
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

## To run extraction_pipeline.py:
### make sure to first run this in your terminal to get the test files:
python tests/test_scripts/create_test_pdf.py    
and 
python tests/test_scripts/create_test_files.py  

### after that run:
 python tests/test_scripts/extraction_pipeline.py

 ### Expected output:
🚀 Extractor Agent starting on 4 files...

--- perfect_statement.jpg ---
Institution: Chase Bank
Reasoning: 
  💰 2026-03-01 | Stripe Payout                  | $500.0

--- digital_statement.pdf ---
Institution: Wells Fargo
Reasoning: 
  💰 2026-02-05 | Stripe Payout                  | $2500.0
  💰 2026-02-15 | Gusto Payroll                  | $4200.0

--- wrong_type_w2.jpg ---
Institution: 
Reasoning: This is a Tax Form, not a transaction statement.