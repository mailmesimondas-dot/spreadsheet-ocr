import os
import tempfile
import uuid
from typing import List
from fastapi import FastAPI, File, UploadFile, Query, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Import our scanner backend
from scanner import TableScanner

app = FastAPI(
    title="Spreadsheet OCR Scanner API",
    description="REST API to extract tables from images and convert them to Excel spreadsheets.",
    version="1.0.0"
)

# Initialize and cache the scanner on CPU
# By default, use CPU for API to maintain compatibility across diverse hosting platforms
try:
    scanner = TableScanner(gpu=False, lang=["en"])
except Exception as e:
    print(f"Error loading OCR Engine: {e}")
    scanner = None

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Spreadsheet OCR Scanner API is running.",
        "ocr_engine": "EasyOCR (en)"
    }

@app.post("/scan")
async def scan_spreadsheet_image(
    file: UploadFile = File(...),
    detect_rotation: bool = Query(True, description="Enable rotation and skew correction"),
    min_confidence: int = Query(50, description="Minimum character confidence threshold"),
    borderless_tables: bool = Query(True, description="Enable detection of borderless tables"),
    implicit_rows: bool = Query(True, description="Enable implicit row calculation"),
    implicit_cols: bool = Query(True, description="Enable implicit column calculation")
):
    """
    Upload an image of a spreadsheet to scan it and download the formatted Excel file (.xlsx).
    """
    if scanner is None:
        raise HTTPException(status_code=500, detail="OCR engine is not initialized.")
        
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".png", ".jpg", ".jpeg"]:
        raise HTTPException(status_code=400, detail="Only JPEG and PNG image formats are supported.")
        
    # Write uploaded file to temp file
    temp_dir = tempfile.gettempdir()
    unique_id = str(uuid.uuid4())
    temp_image_path = os.path.join(temp_dir, f"input_{unique_id}{file_ext}")
    temp_excel_path = os.path.join(temp_dir, f"output_{unique_id}.xlsx")
    
    try:
        # Save image locally
        contents = await file.read()
        with open(temp_image_path, "wb") as f:
            f.write(contents)
            
        # Run table scanning
        extracted_tables, doc = scanner.scan_image(
            image_path=temp_image_path,
            detect_rotation=detect_rotation,
            implicit_rows=implicit_rows,
            implicit_columns=implicit_cols,
            borderless_tables=borderless_tables,
            min_confidence=min_confidence
        )
        
        if not extracted_tables:
            raise HTTPException(
                status_code=422, 
                detail="No tabular structures could be identified in the uploaded image. Try turning on rotation correction or adjusting crop angles."
            )
            
        # Export tables to Excel
        scanner.export_to_excel(doc, temp_excel_path)
        
        # Verify excel file was created
        if not os.path.exists(temp_excel_path):
            raise HTTPException(status_code=500, detail="Failed to write Excel spreadsheet.")
            
        # Return Excel file to client
        return FileResponse(
            path=temp_excel_path,
            filename=f"extracted_{os.path.splitext(file.filename)[0]}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error processing scan: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        # Clean up input image file, keeping the excel output for response stream
        # Excel file response handles cleanup or we can let OS cleanup temporary directories periodically
        try:
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
        except Exception:
            pass

if __name__ == "__main__":
    import uvicorn
    # Start FastAPI server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
