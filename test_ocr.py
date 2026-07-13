import os
import sys
import pandas as pd
import numpy as np
import cv2

# Import scanner classes
from app import create_sample_image
from scanner import TableScanner

def main():
    print("=== Spreadsheet OCR Scanner Test ===")
    
    # 1. Create a sample image
    sample_img_path = "test_sample_sheet.png"
    print(f"Creating sample spreadsheet image: {sample_img_path}")
    sample_img = create_sample_image()
    sample_img.save(sample_img_path)
    
    if not os.path.exists(sample_img_path):
        print("[ERROR] Failed to create sample image.")
        sys.exit(1)
    print("[SUCCESS] Sample image created.")

    # 2. Instantiate and run scanner
    output_excel = "test_output.xlsx"
    output_annotated = "test_annotated.png"
    
    print("\nInitializing TableScanner...")
    try:
        # EasyOCR runs on CPU by default for testing to avoid GPU memory concerns
        scanner = TableScanner(gpu=False, lang=["en"])
    except Exception as e:
        print(f"[ERROR] Failed to initialize TableScanner: {e}")
        sys.exit(1)
        
    print("\nScanning sample spreadsheet image...")
    try:
        extracted_tables, doc = scanner.scan_image(
            image_path=sample_img_path,
            min_confidence=50
        )
    except Exception as e:
        print(f"[ERROR] Scan image failed: {e}")
        sys.exit(1)

    print(f"[SUCCESS] Scan completed. Detected {len(extracted_tables)} tables.")
    
    # 3. Verify results
    if len(extracted_tables) == 0:
        print("[ERROR] No tables detected in the sample image!")
        sys.exit(1)
        
    table = extracted_tables[0]
    print(f"\nTable Bounding Box: {table.bbox}")
    print(f"Number of columns: {len(table.df.columns)}")
    print(f"Number of rows: {len(table.df)}")
    
    print("\nExtracted Data Preview:")
    print(table.df.head())

    # 4. Export results
    print(f"\nExporting to Excel: {output_excel}")
    try:
        scanner.export_to_excel(doc, output_excel)
    except Exception as e:
        print(f"[ERROR] Exporting to Excel failed: {e}")
        sys.exit(1)
        
    if os.path.exists(output_excel):
        print(f"[SUCCESS] Excel file generated: {os.path.abspath(output_excel)}")
    else:
        print("[ERROR] Excel file was not found after export.")
        sys.exit(1)

    # 5. Annotate image
    print(f"Saving annotated image: {output_annotated}")
    scanner.annotate_image(sample_img_path, extracted_tables, output_annotated)
    if os.path.exists(output_annotated):
        print(f"[SUCCESS] Annotated image generated: {os.path.abspath(output_annotated)}")
    else:
        print("[ERROR] Annotated image was not found after annotation.")
        sys.exit(1)
        
    print("\n=== Verification Successful! ===")

if __name__ == "__main__":
    main()
