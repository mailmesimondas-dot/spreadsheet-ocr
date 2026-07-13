#!/usr/bin/env python3
"""
Spreadsheet Image OCR Scanner & Excel Exporter
Core scanning functionality and CLI utility.
"""

import os
import sys
import argparse
import logging
from typing import List, Tuple, Optional

import cv2
import pandas as pd
from img2table.document import Image as TableImage
from img2table.ocr import EasyOCR

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class TableScanner:
    def __init__(self, gpu: bool = False, lang: List[str] = ["en"]):
        """
        Initializes the TableScanner with EasyOCR backend.
        """
        logger.info(f"Initializing EasyOCR with language(s): {lang} (GPU={gpu})")
        # EasyOCR will download language models on the first run if they don't exist
        self.ocr = EasyOCR(lang=lang, kw={"gpu": gpu})

    def scan_image(
        self,
        image_path: str,
        detect_rotation: bool = True,
        implicit_rows: bool = True,
        implicit_columns: bool = True,
        borderless_tables: bool = True,
        min_confidence: int = 50
    ) -> Tuple[List, TableImage]:
        """
        Scans an image to detect tables and extract their contents.
        Returns a list of ExtractedTable objects and the img2table Image object.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at: {image_path}")

        logger.info(f"Loading image from: {image_path} (detect_rotation={detect_rotation})")
        doc = TableImage(src=image_path, detect_rotation=detect_rotation)

        logger.info("Extracting tables using OCR...")
        extracted_tables = doc.extract_tables(
            ocr=self.ocr,
            implicit_rows=implicit_rows,
            implicit_columns=implicit_columns,
            borderless_tables=borderless_tables,
            min_confidence=min_confidence
        )
        logger.info(f"Detected {len(extracted_tables)} table(s)")
        return extracted_tables, doc

    def export_to_excel(self, doc: TableImage, output_path: str) -> None:
        """
        Exports the extracted tables from an img2table Image document to an Excel file.
        """
        logger.info(f"Exporting tables to Excel: {output_path}")
        # Note: doc.to_xlsx uses the document layout structure and populates it using OCR content
        doc.to_xlsx(dest=output_path, ocr=self.ocr)
        logger.info("Export completed successfully.")

    def annotate_image(self, image_path: str, extracted_tables, output_path: str) -> bool:
        """
        Draws bounding boxes around detected tables and cells and saves the result.
        """
        logger.info(f"Annotating image and saving to: {output_path}")
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Failed to read image at {image_path} with OpenCV")
            return False

        # Colors (BGR)
        table_color = (0, 128, 255)  # Orange for tables
        cell_color = (0, 200, 0)     # Green for cells

        for t_idx, table in enumerate(extracted_tables):
            # Draw table bounding box
            bbox = table.bbox
            cv2.rectangle(img, (bbox.x1, bbox.y1), (bbox.x2, bbox.y2), table_color, 4)
            
            # Label the table number
            cv2.putText(
                img,
                f"Table {t_idx + 1}",
                (bbox.x1, max(bbox.y1 - 10, 30)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                table_color,
                2
            )

            # Draw cell bounding boxes
            for row in table.content.values():
                for cell in row:
                    c_bbox = cell.bbox
                    cv2.rectangle(img, (c_bbox.x1, c_bbox.y1), (c_bbox.x2, c_bbox.y2), cell_color, 1)

        cv2.imwrite(output_path, img)
        logger.info("Annotation completed.")
        return True

def main():
    parser = argparse.ArgumentParser(description="Scan a spreadsheet image using OCR and export to Excel.")
    parser.add_argument("image", help="Path to the input spreadsheet image")
    parser.add_argument("-o", "--output", help="Path to the output Excel (.xlsx) file", default="output.xlsx")
    parser.add_argument("-a", "--annotate", help="Path to save the annotated image showing detected tables", default=None)
    parser.add_argument("--no-gpu", action="store_true", help="Disable GPU usage for EasyOCR")
    parser.add_argument("--langs", nargs="+", default=["en"], help="Languages to use for OCR (default: en)")
    parser.add_argument("--min-confidence", type=int, default=50, help="Minimum text confidence for OCR (default: 50)")
    parser.add_argument("--no-rotation", action="store_true", help="Disable skew/rotation correction")

    args = parser.parse_args()

    try:
        scanner = TableScanner(gpu=not args.no_gpu, lang=args.langs)
        extracted_tables, doc = scanner.scan_image(
            image_path=args.image,
            detect_rotation=not args.no_rotation,
            min_confidence=args.min_confidence
        )

        if not extracted_tables:
            logger.warning("No tables were detected in the image.")
            return

        # Export to excel
        scanner.export_to_excel(doc, args.output)

        # Annotate if output path provided
        if args.annotate:
            scanner.annotate_image(args.image, extracted_tables, args.annotate)

        print(f"\n[Success] Scanned {len(extracted_tables)} tables.")
        print(f"Excel file saved to: {os.path.abspath(args.output)}")
        if args.annotate:
            print(f"Annotated image saved to: {os.path.abspath(args.annotate)}")

    except Exception as e:
        logger.exception("An error occurred during execution:")
        sys.exit(1)

if __name__ == "__main__":
    main()
