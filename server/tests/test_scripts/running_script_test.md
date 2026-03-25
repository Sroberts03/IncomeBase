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

## To run analysis test
run:
python tests/test_scripts/stress_test_analysis.py
and
python tests/test_scripts/analysis_pipeline.py

### Expected output:
🚨 Running Stress Test on High-Risk Borrower...

[Verdict] 

Trend: Volatile

[Burn Rate] Net Burn: $-33000.0

[NSF Check] Count: 0

🚩 Risk Factors Found:
  - Income decreased by 50% from November to December
  - Stripe as largest deposit source indicates dependency on freelance or variable income
  - Volatile income trend with large fluctuations

🔍 Anomalous Deposits:
  - Transfer from Unknown: $15000.0

📝 Summary: The borrower's primary income source is Stripe, averaging $9,833.33 over the reviewed 3-month period. Notable risk factors include volatile income with a significant unexplained deposit in January and a dependency on Stripe payouts. Given the income volatility and anomalous transactions, further investigation is recommended before extending credit.

and 

🧹 Cleaning and grouping data...
🤖 Sending to Analysis Agent (gpt-4o)...


VERDICT: Increasing Trend

Monthly Average: $5,500.00

Net Burn Rate: $-8,865.00

📈 6-MONTH CHART DATA:
  
  2025 October    | Income: $3,000.00

  2025 November   | Income: $3,200.00

  2025 December   | Income: $3,500.00

  2026 January    | Income: $3,800.00

  2026 February   | Income: $4,200.00

  2026 March      | Income: $16,500.00

🚩 RISK ASSESSMENT:
  NSF Count: 0
  - 12000% income spike in March 2026
  - Dominant income source from Stripe and Amazon sales disbursement

🔍 ANOMALOUS DEPOSITS DETECTED:
  - AMAZON SALES DISBURSEMENT: $12000.0

📝 UNDERWRITER SUMMARY:
The primary income source is from Stripe with an average monthly volume of $5,500. Notable risks include a 12000% income spike due to a one-time Amazon sales disbursement in March 2026. Despite these anomalies, the income trend is increasing, warranting a recommendation for approval with caution due to variability in income sources.