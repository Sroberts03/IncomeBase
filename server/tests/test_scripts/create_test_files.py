import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

def create_test_docs():
    os.makedirs("tests/test_docs", exist_ok=True)
    
    # 1. THE "PERFECT" BANK STATEMENT
    img_perfect = Image.new('RGB', (800, 1000), color=(255, 255, 255))
    d = ImageDraw.Draw(img_perfect)
    d.text((50, 50), "CHASE BANK - MONTHLY STATEMENT", fill=(0, 0, 0))
    d.text((50, 100), "Account Holder: John Doe", fill=(0, 0, 0))
    d.text((50, 200), "DATE         DESCRIPTION         AMOUNT", fill=(0, 0, 0))
    d.text((50, 230), "2026-03-01   STRIPE PAYOUT       $500.00", fill=(0, 0, 0))
    img_perfect.save("tests/test_docs/perfect_statement.jpg")

    # 2. THE "BLURRY" REJECTION
    img_blurry = Image.new('RGB', (800, 1000), color=(240, 240, 240))
    d = ImageDraw.Draw(img_blurry)
    d.text((50, 450), "THIS TEXT IS TOO BLURRY TO READ", fill=(100, 100, 100))
    # Apply a heavy blur filter
    img_blurry = img_blurry.filter(ImageFilter.GaussianBlur(radius=10))
    img_blurry.save("tests/test_docs/blurry_file.jpg")

    # 3. THE "WRONG TYPE" (W2)
    img_w2 = Image.new('RGB', (800, 1000), color=(255, 255, 255))
    d = ImageDraw.Draw(img_w2)
    d.rectangle([40, 40, 760, 150], outline=(0, 0, 0)) # Box 1 lookalike
    d.text((50, 50), "Form W-2: Wage and Tax Statement 2025", fill=(0, 0, 0))
    d.text((50, 100), "Employer: Summit West Tech LLC", fill=(0, 0, 0))
    img_w2.save("tests/test_docs/wrong_type_w2.jpg")

    print("✅ Created 3 test files in tests/test_docs/")

if __name__ == "__main__":
    create_test_docs()