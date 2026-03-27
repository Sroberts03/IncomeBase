import random
import os
from datetime import date, timedelta
from PIL import Image, ImageDraw, ImageFont

def generate_financial_records():
    start_date = date(2025, 4, 1)
    end_date = date(2026, 3, 27)
    
    records_by_month = {}
    current_date = start_date
    nsf_fees_injected = 0
    
    # 1. GENERATE THE DATA
    while current_date <= end_date:
        month_key = current_date.strftime("%Y_%m")
        if month_key not in records_by_month:
            records_by_month[month_key] = []
            
        month_records = records_by_month[month_key]
            
        # Fixed Expenses
        if current_date.day == 1:
            month_records.append([current_date.isoformat(), "OAK TREE APARTMENTS", -1850.00])
            month_records.append([current_date.isoformat(), "STATE FARM AUTO", -124.50])
            
        # Bi-weekly Payroll
        if current_date.weekday() == 4 and current_date.day % 14 < 7:  
            month_records.append([current_date.isoformat(), "ADP PAYROLL DIR DEP", 2450.00])
            
        # Stripe Payouts
        if random.random() < 0.05:
            month_records.append([current_date.isoformat(), "STRIPE PAYOUT", round(random.uniform(150.0, 850.0), 2)])

        # Daily Living
        if random.random() < 0.15:
            month_records.append([current_date.isoformat(), random.choice(["WHOLE FOODS", "TRADER JOE'S", "KROGER"]), round(random.uniform(-40.0, -180.0), 2)])
        if random.random() < 0.30:
            month_records.append([current_date.isoformat(), random.choice(["STARBUCKS", "CHIPOTLE", "DOORDASH"]), round(random.uniform(-4.50, -35.00), 2)])

        # NSF Fees (Max 2 per year)
        if nsf_fees_injected < 2 and random.random() < 0.01:
            month_records.append([current_date.isoformat(), "OVERDRAFT/NSF FEE", -35.00])
            nsf_fees_injected += 1

        current_date += timedelta(days=1)

    # 2. DRAW THE JPEGS
    output_dir = "mock_statements"
    os.makedirs(output_dir, exist_ok=True)
    
    # Try to load a standard font, fallback to default if missing
    try:
        # Mac standard font
        font_title = ImageFont.truetype("Helvetica.ttc", 24)
        font_body = ImageFont.truetype("Helvetica.ttc", 14)
        font_bold = ImageFont.truetype("Helvetica-Bold.ttc", 14)
    except IOError:
        try:
            # Windows standard font
            font_title = ImageFont.truetype("arial.ttf", 24)
            font_body = ImageFont.truetype("arial.ttf", 14)
            font_bold = ImageFont.truetype("arialbd.ttf", 14)
        except IOError:
            # Universal fallback
            font_title = font_body = font_bold = ImageFont.load_default()

    for month_key, records in records_by_month.items():
        # Create a standard 8.5x11 ratio white canvas
        img = Image.new('RGB', (850, 1100), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        y_text = 50
        
        # Draw Headers
        draw.text((50, y_text), "CHASE BANK - MONTHLY STATEMENT", font=font_title, fill=(30, 58, 138)) # Dark Blue
        y_text += 40
        draw.text((50, y_text), f"Account Holder: John Doe", font=font_body, fill=(0, 0, 0))
        y_text += 20
        draw.text((50, y_text), f"Statement Period: {month_key.replace('_', '/')}", font=font_body, fill=(0, 0, 0))
        y_text += 60
        
        # Draw Table Columns
        draw.text((50, y_text), "DATE", font=font_bold, fill=(100, 100, 100))
        draw.text((200, y_text), "DESCRIPTION", font=font_bold, fill=(100, 100, 100))
        draw.text((650, y_text), "AMOUNT", font=font_bold, fill=(100, 100, 100))
        y_text += 30
        
        # Draw Line Items
        for record in records:
            date_str, desc, amount = record
            # Format amount to 2 decimal places with $
            amt_str = f"${amount:,.2f}" if amount > 0 else f"-${abs(amount):,.2f}"
            
            draw.text((50, y_text), date_str, font=font_body, fill=(0, 0, 0))
            draw.text((200, y_text), desc, font=font_body, fill=(0, 0, 0))
            
            # Right-align the amount (rough estimation based on string length)
            x_amt = 720 - (len(amt_str) * 7) 
            # Make income green, expenses black
            color = (22, 163, 74) if amount > 0 else (0, 0, 0)
            
            draw.text((x_amt, y_text), amt_str, font=font_body, fill=color)
            y_text += 25
            
        # Save the file
        filename = f"{output_dir}/Statement_{month_key}.jpg"
        img.save(filename, "JPEG", quality=90)
        print(f"Generated: {filename}")

    print(f"\n✅ All 12 statement JPEGs saved in the '{output_dir}' folder!")

if __name__ == "__main__":
    generate_financial_records()