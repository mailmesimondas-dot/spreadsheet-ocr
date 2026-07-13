import os
import io
import time
import tempfile
import streamlit as st
import pandas as pd
import numpy as np
import cv2
from PIL import Image as PILImage

# Import the core scanner classes
import importlib
import scanner
importlib.reload(scanner)
from scanner import TableScanner

# ----------------------------------------------------
# Page Configuration
# ----------------------------------------------------
st.set_page_config(
    page_title="Spreadsheet OCR Scanner",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# Premium Styling & CSS Injection
# ----------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Global Font Override */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    font-family: 'Outfit', sans-serif !important;
}

/* Background Adjustments */
[data-testid="stAppViewContainer"] {
    background-color: #0b0f19;
}

[data-testid="stSidebar"] {
    background-color: #111827 !important;
    border-right: 1px solid #1f2937;
}

/* Custom Typography */
.main-title {
    background: linear-gradient(135deg, #a855f7, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
    text-align: center;
}

.sub-title {
    color: #9ca3af;
    font-size: 1.1rem;
    text-align: center;
    margin-bottom: 2rem;
    font-weight: 300;
}

/* Card layout */
.glass-card {
    background: rgba(17, 24, 39, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(5px);
    -webkit-backdrop-filter: blur(5px);
}

.status-badge {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 500;
    display: inline-block;
    margin-bottom: 10px;
}

/* File Uploader Custom styling */
[data-testid="stFileUploader"] {
    background-color: #1f2937;
    border: 2px dashed #4b5563;
    border-radius: 12px;
    padding: 10px;
    transition: all 0.3s ease;
}

[data-testid="stFileUploader"]:hover {
    border-color: #ec4899;
    background-color: #374151;
}

/* Custom styled buttons */
div.stButton > button {
    background: linear-gradient(135deg, #8b5cf6, #ec4899) !important;
    color: white !important;
    border: none !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 15px rgba(236, 72, 153, 0.3) !important;
    transition: all 0.3s ease !important;
}

div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(236, 72, 153, 0.5) !important;
}

div.stButton > button:active {
    transform: translateY(0px) !important;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# Helper to Generate a Sample Spreadsheet Image
# ----------------------------------------------------
def create_sample_image():
    """
    Creates a synthetic spreadsheet image and returns it as a PIL Image.
    """
    # Create a white canvas (800x400)
    img = np.ones((450, 800, 3), dtype=np.uint8) * 255
    
    # Draw horizontal and vertical grid lines
    # Outer Border
    cv2.rectangle(img, (20, 20), (780, 430), (0, 0, 0), 2)
    
    # Table headers row: Y = 70
    cv2.line(img, (20, 70), (780, 70), (0, 0, 0), 2)
    
    # Rows boundaries
    row_heights = [120, 170, 220, 270, 320, 370, 430]
    for y in row_heights:
        cv2.line(img, (20, y), (780, y), (0, 0, 0), 1)
        
    # Columns boundaries
    col_widths = [150, 310, 470, 630]
    for x in col_widths:
        cv2.line(img, (x, 20), (x, 430), (0, 0, 0), 1)
        
    # Add texts
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.55
    color = (30, 30, 30)
    header_color = (0, 0, 0)
    thickness = 1
    
    # Headers
    cv2.putText(img, "Product ID", (35, 50), font, 0.6, header_color, 2)
    cv2.putText(img, "Product Name", (165, 50), font, 0.6, header_color, 2)
    cv2.putText(img, "Unit Price ($)", (325, 50), font, 0.6, header_color, 2)
    cv2.putText(img, "Quantity Sold", (485, 50), font, 0.6, header_color, 2)
    cv2.putText(img, "Total Revenue ($)", (645, 50), font, 0.6, header_color, 2)
    
    # Row 1
    cv2.putText(img, "P-1001", (35, 100), font, font_scale, color, thickness)
    cv2.putText(img, "Wireless Mouse", (165, 100), font, font_scale, color, thickness)
    cv2.putText(img, "25.00", (325, 100), font, font_scale, color, thickness)
    cv2.putText(img, "120", (485, 100), font, font_scale, color, thickness)
    cv2.putText(img, "3000.00", (645, 100), font, font_scale, color, thickness)
    
    # Row 2
    cv2.putText(img, "P-1002", (35, 150), font, font_scale, color, thickness)
    cv2.putText(img, "Mechanical Keyboard", (165, 150), font, font_scale, color, thickness)
    cv2.putText(img, "85.00", (325, 150), font, font_scale, color, thickness)
    cv2.putText(img, "45", (485, 150), font, font_scale, color, thickness)
    cv2.putText(img, "3825.00", (645, 150), font, font_scale, color, thickness)
    
    # Row 3
    cv2.putText(img, "P-1003", (35, 200), font, font_scale, color, thickness)
    cv2.putText(img, "USB-C Hub Adapter", (165, 200), font, font_scale, color, thickness)
    cv2.putText(img, "35.50", (325, 200), font, font_scale, color, thickness)
    cv2.putText(img, "80", (485, 200), font, font_scale, color, thickness)
    cv2.putText(img, "2840.00", (645, 200), font, font_scale, color, thickness)

    # Row 4
    cv2.putText(img, "P-1004", (35, 250), font, font_scale, color, thickness)
    cv2.putText(img, "Full HD Monitor", (165, 250), font, font_scale, color, thickness)
    cv2.putText(img, "149.99", (325, 250), font, font_scale, color, thickness)
    cv2.putText(img, "30", (485, 250), font, font_scale, color, thickness)
    cv2.putText(img, "4499.70", (645, 250), font, font_scale, color, thickness)

    # Row 5
    cv2.putText(img, "P-1005", (35, 300), font, font_scale, color, thickness)
    cv2.putText(img, "Noise Cancel Headphone", (165, 300), font, font_scale, color, thickness)
    cv2.putText(img, "199.00", (325, 300), font, font_scale, color, thickness)
    cv2.putText(img, "15", (485, 300), font, font_scale, color, thickness)
    cv2.putText(img, "2985.00", (645, 300), font, font_scale, color, thickness)
    
    # Row 6 (Totals)
    cv2.putText(img, "Total / Summary", (35, 350), font, 0.55, (0, 0, 255), 2)
    cv2.putText(img, "All items", (165, 350), font, font_scale, color, thickness)
    cv2.putText(img, "-", (325, 350), font, font_scale, color, thickness)
    cv2.putText(img, "290", (485, 350), font, font_scale, color, thickness)
    cv2.putText(img, "17149.70", (645, 350), font, 0.55, (0, 0, 255), 2)

    # Add a title at Y = 405
    cv2.putText(img, "Sales Record Q3 - FY26", (270, 410), font, 0.65, (100, 100, 100), 2)
    
    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return PILImage.fromarray(img_rgb)

# ----------------------------------------------------
# Caching the Scanner Instance
# ----------------------------------------------------
@st.cache_resource
def get_scanner(gpu: bool, lang_str: str) -> TableScanner:
    """
    Initializes and caches the OCR scanner so model files don't reload on each interaction.
    """
    langs = [lang.strip() for lang in lang_str.split(",") if lang.strip()]
    return TableScanner(gpu=gpu, lang=langs)

# ----------------------------------------------------
# Streamlit App Flow
# ----------------------------------------------------
st.markdown('<div class="main-title">Spreadsheet OCR Scanner</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Extract data tables from images directly to Excel with premium OCR technology</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# Sidebar Configuration
# ----------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/120/microsoft-excel-2019--v1.png", width=70)
st.sidebar.markdown("### Scanner Settings")

ocr_engine = st.sidebar.selectbox("OCR Engine Backend", ["EasyOCR (Default)", "Tesseract (System-dependent)"])

# Language configurations (comma separated)
ocr_langs = st.sidebar.text_input("Language Codes (comma-separated)", value="en", help="Example: 'en' for English, 'en,fr' for multiple")

# Hardware Acceleration
use_gpu = st.sidebar.checkbox("Use GPU Acceleration", value=False, help="Enable if GPU with CUDA support is configured.")

# Extraction Parameters
st.sidebar.markdown("### Layout Settings")
detect_rotation = st.sidebar.checkbox("Detect Image Rotation / Skew", value=True, help="Enable if the image is slightly rotated or photographed at an angle.")
min_confidence = st.sidebar.slider("OCR Confidence Threshold (%)", min_value=10, max_value=100, value=50, step=5)
detect_borderless = st.sidebar.checkbox("Detect Borderless Tables", value=True)
implicit_rows = st.sidebar.checkbox("Detect Implicit Rows", value=True)
implicit_cols = st.sidebar.checkbox("Detect Implicit Columns", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### How to use:")
st.sidebar.markdown("""
1. Upload a spreadsheet image (PNG/JPG) or click **Load Sample Image**.
2. Click **Run OCR Scanner** to extract.
3. Review results and **Download Excel**.
""")

# ----------------------------------------------------
# Main Panel Setup
# ----------------------------------------------------
# Initialize variables
temp_img_path = None
uploaded_image_display = None
st_source = None

# Dropzone area
uploader_col, sample_col = st.columns([3, 1])

with uploader_col:
    uploaded_file = st.file_uploader(
        "Drop your spreadsheet image here...",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )

with sample_col:
    st.write("")
    st.write("")
    load_sample = st.button("Load Sample Image")

# Handle image selection (Uploaded or Sample)
if uploaded_file is not None:
    # Save uploaded file to temp file to scan
    temp_dir = tempfile.gettempdir()
    temp_img_path = os.path.join(temp_dir, "temp_uploaded_spreadsheet.png")
    
    # Write the bytes
    with open(temp_img_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    uploaded_image_display = PILImage.open(uploaded_file)
    st_source = "Uploaded Image"
    
elif load_sample:
    # Generate and save sample
    sample_img = create_sample_image()
    temp_dir = tempfile.gettempdir()
    temp_img_path = os.path.join(temp_dir, "temp_sample_spreadsheet.png")
    sample_img.save(temp_img_path)
    
    uploaded_image_display = sample_img
    st_source = "Sample Image Loaded"
    
    # Store in session state to persist between button clicks
    st.session_state["sample_loaded"] = True
    st.session_state["temp_img_path"] = temp_img_path

# Fallback session state check for sample
if uploaded_file is None and st.session_state.get("sample_loaded", False):
    temp_img_path = st.session_state.get("temp_img_path")
    if temp_img_path and os.path.exists(temp_img_path):
        uploaded_image_display = PILImage.open(temp_img_path)
        st_source = "Sample Image Loaded"

# Display Image Preview & Launch Scanner
if uploaded_image_display is not None:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="status-badge">{st_source}</div>', unsafe_allow_html=True)
    
    img_col, action_col = st.columns([2, 1])
    
    with img_col:
        st.markdown("### Image Preview")
        st.image(uploaded_image_display, use_container_width=True)
        
    with action_col:
        st.markdown("### Scanner Control")
        st.write("Ready to perform layout parsing and character recognition.")
        
        run_scan = st.button("🚀 Run OCR Scanner")
        
        if run_scan:
            # 1. Initialize scanner
            with st.spinner("Initializing OCR Engine (This may take a moment on the first run)..."):
                try:
                    scanner = get_scanner(gpu=use_gpu, lang_str=ocr_langs)
                except Exception as e:
                    st.error(f"Error loading OCR Engine: {e}")
                    st.stop()
            
            # Create progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Phase 1
            status_text.text("Phase 1/3: Analyzing table grid and structure...")
            progress_bar.progress(30)
            time.sleep(0.5)
            
            try:
                # 2. Extract tables
                extracted_tables, doc = scanner.scan_image(
                    image_path=temp_img_path,
                    detect_rotation=detect_rotation,
                    implicit_rows=implicit_rows,
                    implicit_columns=implicit_cols,
                    borderless_tables=detect_borderless,
                    min_confidence=min_confidence
                )
                
                # Phase 2
                status_text.text("Phase 2/3: Performing OCR character extraction...")
                progress_bar.progress(70)
                
                # Verify tables were found
                if not extracted_tables:
                    st.warning("No tabular structures could be identified in this image. Try adjusting the layout parameters in the sidebar.")
                    progress_bar.empty()
                    status_text.empty()
                else:
                    # Phase 3
                    status_text.text("Phase 3/3: Exporting tables and formatting Excel file...")
                    progress_bar.progress(90)
                    
                    # Create paths for temp exports
                    temp_excel_path = os.path.join(tempfile.gettempdir(), "extracted_spreadsheet.xlsx")
                    temp_annotated_path = os.path.join(tempfile.gettempdir(), "annotated_spreadsheet.png")
                    
                    # Export excel
                    scanner.export_to_excel(doc, temp_excel_path)
                    
                    # Annotate original image
                    scanner.annotate_image(temp_img_path, extracted_tables, temp_annotated_path)
                    
                    progress_bar.progress(100)
                    time.sleep(0.3)
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success(f"Scanning complete! Detected {len(extracted_tables)} table(s).")
                    
                    # Store results in session state to persist
                    st.session_state["scan_results"] = {
                        "tables": [table.df for table in extracted_tables],
                        "annotated_path": temp_annotated_path,
                        "excel_path": temp_excel_path
                    }
                    
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"Scanning failed: {e}")
                st.exception(e)
                
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# Display OCR Extraction Results
# ----------------------------------------------------
if "scan_results" in st.session_state:
    results = st.session_state["scan_results"]
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## Scanning Results & Export")
    
    res_col1, res_col2 = st.columns([1, 1])
    
    with res_col1:
        st.markdown("### Detected Table Bounds")
        if os.path.exists(results["annotated_path"]):
            st.image(results["annotated_path"], use_container_width=True, caption="Green boxes represent cells, Orange represents the table container.")
            
    with res_col2:
        st.markdown("### Extracted Tables Preview")
        tables = results["tables"]
        
        # Tabs for multiple tables
        tab_titles = [f"Table {i+1}" for i in range(len(tables))]
        tabs = st.tabs(tab_titles)
        
        for idx, tab in enumerate(tabs):
            with tab:
                df = tables[idx]
                st.dataframe(df, use_container_width=True)
                
        # Excel download button
        st.write("")
        st.markdown("### Download Output")
        
        excel_path = results["excel_path"]
        if os.path.exists(excel_path):
            with open(excel_path, "rb") as f:
                excel_bytes = f.read()
                
            st.download_button(
                label="📥 Download Excel Spreadsheet (.xlsx)",
                data=excel_bytes,
                file_name="extracted_spreadsheet.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_excel_btn"
            )
            
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # Place holder card
    if uploaded_image_display is None:
        st.markdown('<div class="glass-card" style="text-align: center; padding: 50px;">', unsafe_allow_html=True)
        st.markdown("### No Image Uploaded")
        st.write("Drag and drop a spreadsheet screenshot or crop of a table, or load the built-in sample table to test the scanner.")
        st.markdown('</div>', unsafe_allow_html=True)
