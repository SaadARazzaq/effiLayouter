# main.py
# FastAPI backend exposing routes for:
# - upload PDF
# - remove text (preserve images/layout)
# - English pipeline: extract chars → reconstruct
# - Arabic pipeline: extract lines → translate → reconstruct
# - visualize line bounding boxes
# - download generated files
#
# Requires your existing modules in the same folder:
# text_extractor.py, text_remover.py, pdf_reconstructor.py,
# ar_pdf_reconstructor.py, countour_mapper.py
#
# Example React calls (default dev):
#   POST http://localhost:8008/api/upload
#   POST http://localhost:8008/api/remove-text
#   POST http://localhost:8008/api/extract-characters
#   POST http://localhost:8008/api/reconstruct/english
#   POST http://localhost:8008/api/extract-lines
#   POST http://localhost:8008/api/translate/arabic
#   POST http://localhost:8008/api/reconstruct/arabic
#   POST http://localhost:8008/api/visualize-lines
#   GET  http://localhost:8008/api/download?file=input_text_removed.pdf

import os
import io
import json
import traceback
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# === Your existing modules ===
from text_extractor import extract_pdf_to_json
from text_remover import remove_text
from pdf_reconstructor import reconstruct_pdf
from ar_pdf_reconstructor import reconstruct_pdf_from_line_db
from countour_mapper import PDFLineExtractor

# ---------- Config ----------
APP_TITLE = "PDF Text Replacement API"
STORAGE_DIR = os.path.abspath("./storage")
INPUT_PDF_NAME = "input.pdf"
TEXT_REMOVED_NAME = "input_text_removed.pdf"
EN_JSON_NAME = "extracted_data.json"
LINE_DB_NAME = "line_db.json"
AR_LINE_DB_NAME = "ar_line_db.json"
EN_OUTPUT_PDF = "english_reconstructed_input.pdf"
AR_OUTPUT_PDF = "arabic_reconstructed_input.pdf"
VISUALIZED_PDF = "input_visualized.pdf"

os.makedirs(STORAGE_DIR, exist_ok=True)

def _p(*parts):
    return os.path.join(STORAGE_DIR, *parts)

def _exists(path: str) -> bool:
    return os.path.exists(path) and os.path.isfile(path)

def _safe_name(name: str) -> str:
    """Normalize any filename to a safe basename inside STORAGE_DIR."""
    return os.path.basename((name or "").strip())


def _json_ok(**payload):
    # Uniform JSON envelope
    return JSONResponse({"ok": True, **payload})

def _json_err(message: str, detail: Optional[str] = None, status_code: int = 400):
    return JSONResponse({"ok": False, "message": message, "detail": detail}, status_code=status_code)

# ---------- FastAPI ----------
app = FastAPI(title=APP_TITLE, version="1.0.0")

# CORS for Vite + local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*",  # loosen if you prefer; keep while developing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# put this anywhere after app = FastAPI(...)
@app.get("/api/_routes")
def _routes():
    return {
        "routes": [
            {"path": getattr(r, "path", None), "methods": list(getattr(r, "methods", []))}
            for r in app.router.routes
            if hasattr(r, "path")
        ]
    }


# ---------- Schemas ----------
class ExtractCharactersReq(BaseModel):
    input_pdf: str = Field(default=INPUT_PDF_NAME, description="PDF filename in storage to read")
    json_output: str = Field(default=EN_JSON_NAME, description="Output JSON filename")

class ReconstructEnglishReq(BaseModel):
    json_input: str = Field(default=EN_JSON_NAME)
    text_removed_pdf: str = Field(default=TEXT_REMOVED_NAME)
    output_pdf: str = Field(default=EN_OUTPUT_PDF)

class ExtractLinesReq(BaseModel):
    input_pdf: str = Field(default=INPUT_PDF_NAME)
    line_db_output: str = Field(default=LINE_DB_NAME)

class TranslateArabicReq(BaseModel):
    line_db_input: str = Field(default=LINE_DB_NAME)
    ar_line_db_output: str = Field(default=AR_LINE_DB_NAME)
    max_workers: int = Field(default=2, ge=1, le=8)
    timeout_seconds: int = Field(default=120, ge=30, le=600)

class ReconstructArabicReq(BaseModel):
    ar_line_db_input: str = Field(default=AR_LINE_DB_NAME)
    base_pdf: str = Field(default=TEXT_REMOVED_NAME)
    output_pdf: str = Field(default=AR_OUTPUT_PDF)

class VisualizeLinesReq(BaseModel):
    input_pdf: str = Field(default=INPUT_PDF_NAME)
    line_db_input: str = Field(default=LINE_DB_NAME)
    visualized_pdf: str = Field(default=VISUALIZED_PDF)

# ---------- Helpers ----------
def _assert_file_exists(name: str):
    name = _safe_name(name)
    path = _p(name)
    if not _exists(path):
        raise HTTPException(status_code=404, detail=f"File not found: {name}")
    return path


def _public_file_info(name: str):
    return {
        "filename": name,
        "path": f"/api/download?file={name}",
        "absPath": _p(name),
        "size": os.path.getsize(_p(name)) if _exists(_p(name)) else 0,
        "modifiedAt": datetime.fromtimestamp(os.path.getmtime(_p(name))).isoformat() if _exists(_p(name)) else None
    }

# ---------- Routes ----------

@app.post("/api/workflow")
def api_workflow(language: str = Form("en")):
    """
    Unified workflow that handles both English and Arabic processing in one call
    """
    try:
        # Common steps
        remove_text(_p(INPUT_PDF_NAME), _p(TEXT_REMOVED_NAME))
        
        if language.lower() in ["ar", "arabic"]:
            # Arabic workflow
            extractor = PDFLineExtractor()
            line_db = extractor.extract_lines_from_pdf(_p(INPUT_PDF_NAME), _p(LINE_DB_NAME))
            ar_line_db = extractor.translate_to_arabic(line_db, _p(AR_LINE_DB_NAME))
            reconstruct_pdf_from_line_db(_p(AR_LINE_DB_NAME), _p(TEXT_REMOVED_NAME), _p(AR_OUTPUT_PDF))
            output_file = AR_OUTPUT_PDF
        else:
            # English workflow
            extract_pdf_to_json(_p(INPUT_PDF_NAME), _p(EN_JSON_NAME))
            reconstruct_pdf(_p(EN_JSON_NAME), _p(TEXT_REMOVED_NAME), _p(EN_OUTPUT_PDF))
            output_file = EN_OUTPUT_PDF
        
        return _json_ok(
            message=f"{'Arabic' if language == 'ar' else 'English'} workflow completed",
            output=_public_file_info(output_file)
        )
        
    except Exception as e:
        return _json_err("Workflow failed", detail=str(e), status_code=500)

@app.delete("/api/cleanup")
def api_cleanup(keep_original: bool = Query(True)):
    """
    Clean up generated files while keeping the original uploaded PDF
    """
    try:
        files_to_remove = [
            TEXT_REMOVED_NAME, EN_JSON_NAME, LINE_DB_NAME, 
            AR_LINE_DB_NAME, EN_OUTPUT_PDF, AR_OUTPUT_PDF, VISUALIZED_PDF
        ]
        
        removed = []
        for filename in files_to_remove:
            filepath = _p(filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                removed.append(filename)
        
        return _json_ok(
            message="Cleanup completed",
            removed_files=removed,
            kept_original=keep_original
        )
        
    except Exception as e:
        return _json_err("Cleanup failed", detail=str(e), status_code=500)

@app.get("/api/status")
def api_status():
    """
    Check status of all processing files
    """
    files_status = {}
    all_files = [
        INPUT_PDF_NAME, TEXT_REMOVED_NAME, EN_JSON_NAME, 
        LINE_DB_NAME, AR_LINE_DB_NAME, EN_OUTPUT_PDF, AR_OUTPUT_PDF, VISUALIZED_PDF
    ]
    
    for filename in all_files:
        filepath = _p(filename)
        exists = os.path.exists(filepath)
        files_status[filename] = {
            "exists": exists,
            "size": os.path.getsize(filepath) if exists else 0,
            "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat() if exists else None
        }
    
    return _json_ok(files=files_status)

@app.get("/api/health")
def health():
    return {"ok": True, "service": APP_TITLE, "time": datetime.utcnow().isoformat()}

@app.get("/api/list")
def list_storage():
    files = []
    for fname in sorted(os.listdir(STORAGE_DIR)):
        fpath = _p(fname)
        if os.path.isfile(fpath):
            files.append(_public_file_info(fname))
    return {"ok": True, "files": files}

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...), save_as: Optional[str] = Form(None)):
    try:
        filename = _safe_name(save_as) if save_as else INPUT_PDF_NAME
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"
        data = await file.read()
        with open(_p(filename), "wb") as f:
            f.write(data)
        return _json_ok(message="Uploaded", file=_public_file_info(filename))
    except Exception as e:
        return _json_err("Upload failed", detail=str(e), status_code=500)


@app.post("/api/remove-text")
def api_remove_text(input_pdf: str = Form(default=INPUT_PDF_NAME),
                    output_pdf: str = Form(default=TEXT_REMOVED_NAME)):
    try:
        in_path = _assert_file_exists(input_pdf)
        out_path = _p(_safe_name(output_pdf))
        remove_text(in_path, out_path)
        return _json_ok(message="Text removed", input=_public_file_info(_safe_name(input_pdf)), output=_public_file_info(_safe_name(output_pdf)))
    except HTTPException as he:
        return _json_err("Text removal failed", detail=str(he.detail), status_code=he.status_code)
    except Exception as e:
        return _json_err("Text removal failed", detail=str(e), status_code=500)


@app.post("/api/extract-characters")
def api_extract_characters(req: ExtractCharactersReq):
    try:
        in_path = _assert_file_exists(req.input_pdf)
        json_out = _p(_safe_name(req.json_output))
        extract_pdf_to_json(in_path, json_out)
        with open(json_out, "r", encoding="utf-8") as f:
            data = json.load(f)
        preview = {
            "pages": len(data),
            "page_1": {
                "w": data[0].get("page_width") if data else None,
                "h": data[0].get("page_height") if data else None,
                "char_count": len(data[0].get("characters", [])) if data else 0,
            } if data else None
        }
        return _json_ok(message="Character data extracted", output=_public_file_info(_safe_name(req.json_output)), preview=preview)
    except HTTPException as he:
        return _json_err("Character extraction failed", detail=str(he.detail), status_code=he.status_code)
    except Exception as e:
        return _json_err("Character extraction failed", detail=str(e), status_code=500)


@app.post("/api/reconstruct/english")
def api_reconstruct_english(req: ReconstructEnglishReq):
    try:
        _assert_file_exists(req.json_input)
        _assert_file_exists(req.text_removed_pdf)
        out_path = _p(_safe_name(req.output_pdf))
        reconstruct_pdf(_p(_safe_name(req.json_input)), _p(_safe_name(req.text_removed_pdf)), out_path)
        return _json_ok(message="English PDF reconstructed", output=_public_file_info(_safe_name(req.output_pdf)))
    except HTTPException as he:
        return _json_err("English reconstruction failed", detail=str(he.detail), status_code=he.status_code)
    except Exception as e:
        return _json_err("English reconstruction failed", detail=str(e), status_code=500)


@app.post("/api/extract-lines")
def api_extract_lines(req: ExtractLinesReq):
    try:
        in_path = _assert_file_exists(req.input_pdf)
        out_name = _safe_name(req.line_db_output) or LINE_DB_NAME
        out_path = _p(out_name)

        extractor = PDFLineExtractor()
        line_db = extractor.extract_lines_from_pdf(in_path, out_path)

        # If the extractor returns None/minimal, load the JSON we just wrote
        if not line_db or "metadata" not in line_db:
            with open(out_path, "r", encoding="utf-8") as f:
                line_db = json.load(f)

        meta = line_db.get("metadata", {})
        summary = {
            "pages": meta.get("total_pages", 0),
            "sentences": meta.get("total_sentences", 0),
            "words": meta.get("total_words", 0),
        }

        return _json_ok(
            message="Line DB created",
            output=_public_file_info(out_name),
            summary=summary,
            # 👇 give the next step exactly what it needs
            line_db_input=out_name,
        )
    except HTTPException as he:
        return _json_err("Line extraction failed", detail=str(he.detail), status_code=he.status_code)
    except Exception as e:
        return _json_err("Line extraction failed", detail=str(e), status_code=500)


@app.post("/api/translate/arabic")
@app.post("/api/translate/arabic/")
def api_translate_arabic(req: TranslateArabicReq):
    try:
        print(f"🔍 Arabic translation endpoint called with: {req}")
        
        # normalize and verify file inputs
        line_db_name = _safe_name(req.line_db_input) or LINE_DB_NAME
        ar_out_name  = _safe_name(req.ar_line_db_output) or AR_LINE_DB_NAME
        
        print(f"📁 Looking for line DB file: {line_db_name}")
        print(f"📁 Output Arabic file will be: {ar_out_name}")

        line_db_path = _p(line_db_name)
        
        # If line DB doesn't exist, create it from the input PDF
        if not os.path.exists(line_db_path):
            print(f"⚠️ Line DB file not found, creating it from input PDF...")
            
            input_pdf_path = _p(INPUT_PDF_NAME)
            if not os.path.exists(input_pdf_path):
                # List available files to help debugging
                available_files = os.listdir(STORAGE_DIR)
                return _json_err(
                    "Input PDF not found",
                    detail=f"Cannot create line DB: '{INPUT_PDF_NAME}' not found. Available files: {available_files}",
                    status_code=404
                )
            
            # Extract lines from PDF to create line DB using PDFLineExtractor
            print(f"✅ Input PDF found, creating line DB...")
            extractor = PDFLineExtractor()
            line_db = extractor.extract_lines_from_pdf(input_pdf_path, line_db_path)
            print(f"✅ Line DB created with {len(line_db.get('sentences', []))} sentences")
        else:
            print(f"✅ Line DB file found at: {line_db_path}")
            with open(line_db_path, "r", encoding="utf-8") as f:
                line_db = json.load(f)
            print(f"📊 Line DB loaded with {len(line_db.get('sentences', []))} sentences")

        # Verify the line_db has the correct structure
        if not isinstance(line_db, dict) or "sentences" not in line_db:
            return _json_err(
                "Invalid line database format",
                detail="The line database must be in the correct format with a 'sentences' key",
                status_code=400
            )

        print("🚀 Starting Arabic translation...")
        extractor = PDFLineExtractor()
        
        # Call the translate_to_arabic method from PDFLineExtractor
        ar_db = extractor.translate_to_arabic(
            line_db,
            output_json_path=_p(ar_out_name),
            max_workers=req.max_workers,
            timeout_seconds=req.timeout_seconds
        )
        
        print("✅ Arabic translation completed successfully")
        
        # Prepare summary
        summary = {
            "sentences": len(ar_db.get("sentences", [])),
            "target_language": "ar",
            "translation_service": "GoogleTranslator"
        }

        # Add metadata from the original translation if available
        if "metadata" in ar_db and "translation" in ar_db["metadata"]:
            summary.update(ar_db["metadata"]["translation"])

        print(f"📋 Translation summary: {summary}")
        
        return _json_ok(
            message="Arabic translation complete",
            output=_public_file_info(ar_out_name),
            summary=summary
        )

    except HTTPException as he:
        print(f"❌ HTTP Exception in Arabic translation: {he.detail}")
        return _json_err("Arabic translation failed", detail=str(he.detail), status_code=he.status_code)
    except Exception as e:
        tb = traceback.format_exc()
        print(f"❌ Unexpected error in Arabic translation: {e}\n{tb}")
        return _json_err("Arabic translation failed", detail=f"{e}\n{tb}", status_code=500)



@app.post("/api/reconstruct/arabic")
@app.post("/api/reconstruct/arabic/")
def api_reconstruct_arabic(req: ReconstructArabicReq):
    try:
        print(f"🔍 Arabic reconstruction called with: {req}")
        
        # Check if required files exist
        ar_line_db_path = _assert_file_exists(req.ar_line_db_input)
        base_pdf_path = _assert_file_exists(req.base_pdf)
        
        print(f"✅ Arabic line DB found: {ar_line_db_path}")
        print(f"✅ Base PDF found: {base_pdf_path}")
        
        out_path = _p(_safe_name(req.output_pdf))
        print(f"📁 Output path: {out_path}")
        
        # Load and check the Arabic line DB
        with open(ar_line_db_path, "r", encoding="utf-8") as f:
            ar_line_db = json.load(f)
        print(f"📊 Arabic line DB loaded. Sentences: {len(ar_line_db.get('sentences', []))}")
        
        # Call the reconstruction function
        print("🚀 Starting Arabic PDF reconstruction...")
        reconstruct_pdf_from_line_db(ar_line_db_path, base_pdf_path, out_path)
        
        # Verify the output file was created
        if not os.path.exists(out_path):
            raise Exception(f"Output file was not created: {out_path}")
            
        print(f"✅ Arabic PDF reconstructed successfully: {out_path}")
        print(f"📏 File size: {os.path.getsize(out_path)} bytes")
        
        return _json_ok(
            message="Arabic PDF reconstructed", 
            output=_public_file_info(_safe_name(req.output_pdf))
        )
        
    except HTTPException as he:
        print(f"❌ HTTP Exception in Arabic reconstruction: {he.detail}")
        return _json_err("Arabic reconstruction failed", detail=str(he.detail), status_code=he.status_code)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"❌ Error in Arabic reconstruction: {e}\n{tb}")
        return _json_err("Arabic reconstruction failed", detail=f"{e}\n{tb}", status_code=500)


@app.post("/api/reconstruct/arabic")
@app.post("/api/reconstruct/arabic/")
def api_reconstruct_arabic(req: ReconstructArabicReq):
    try:
        print(f"🔍 Arabic reconstruction called with: {req}")
        
        # Check if required files exist
        ar_line_db_path = _assert_file_exists(req.ar_line_db_input)
        base_pdf_path = _assert_file_exists(req.base_pdf)
        
        print(f"✅ Arabic line DB found: {ar_line_db_path}")
        print(f"✅ Base PDF found: {base_pdf_path}")
        
        out_path = _p(_safe_name(req.output_pdf))
        print(f"📁 Output path: {out_path}")
        
        # Load and check the Arabic line DB
        with open(ar_line_db_path, "r", encoding="utf-8") as f:
            ar_line_db = json.load(f)
        print(f"📊 Arabic line DB loaded. Sentences: {len(ar_line_db.get('sentences', []))}")
        
        # Call the reconstruction function
        print("🚀 Starting Arabic PDF reconstruction...")
        reconstruct_pdf_from_line_db(ar_line_db_path, base_pdf_path, out_path)
        
        # Verify the output file was created
        if not os.path.exists(out_path):
            raise Exception(f"Output file was not created: {out_path}")
            
        print(f"✅ Arabic PDF reconstructed successfully: {out_path}")
        print(f"📏 File size: {os.path.getsize(out_path)} bytes")
        
        return _json_ok(
            message="Arabic PDF reconstructed", 
            output=_public_file_info(_safe_name(req.output_pdf))
        )
        
    except HTTPException as he:
        print(f"❌ HTTP Exception in Arabic reconstruction: {he.detail}")
        return _json_err("Arabic reconstruction failed", detail=str(he.detail), status_code=he.status_code)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"❌ Error in Arabic reconstruction: {e}\n{tb}")
        return _json_err("Arabic reconstruction failed", detail=f"{e}\n{tb}", status_code=500)

        
@app.post("/api/visualize-lines")
@app.post("/api/visualize-lines/")
def api_visualize_lines(req: VisualizeLinesReq):
    try:
        input_pdf_path = _assert_file_exists(req.input_pdf)
        data_path = _assert_file_exists(req.line_db_input)
        
        # Load the data
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Check if this is line database format (from contour_mapper)
        if isinstance(data, dict) and "sentences" in data:
            line_db = data
            print(f"Loaded line DB with {len(line_db.get('sentences', []))} sentences")
        else:
            print("Character data format detected, extracting lines first...")
            extractor = PDFLineExtractor()
            line_db = extractor.extract_lines_from_pdf(input_pdf_path, "temp_line_db.json")
            print(f"Extracted {len(line_db.get('sentences', []))} lines from PDF")
        
        output_path = _p(_safe_name(req.visualized_pdf))
        
        # Create visualization using the line database
        extractor = PDFLineExtractor()
        result_path = extractor.visualize_lines(input_pdf_path, line_db, output_path)
        print(f"Visualization created at: {result_path}")
        
        # ==============================================================
        # AUTO-RECONSTRUCT ARABIC PDF (NON-BLOCKING)
        # ==============================================================
        reconstruction_success = False
        reconstruction_error = None
        
        ar_line_db_path = _p(AR_LINE_DB_NAME)
        base_pdf_path = _p(TEXT_REMOVED_NAME)
        arabic_output_path = _p(AR_OUTPUT_PDF)
        
        if os.path.exists(ar_line_db_path) and os.path.exists(base_pdf_path):
            print("🔄 Starting non-blocking Arabic PDF reconstruction...")
            
            try:
                # Use a separate try-catch so reconstruction failure doesn't affect visualization
                with open(ar_line_db_path, "r", encoding="utf-8") as f:
                    ar_line_db = json.load(f)
                
                reconstruct_pdf_from_line_db(ar_line_db_path, base_pdf_path, arabic_output_path)
                
                if os.path.exists(arabic_output_path):
                    reconstruction_success = True
                    print(f"✅ Arabic PDF auto-reconstructed successfully")
                else:
                    reconstruction_error = "Output file was not created"
                    
            except Exception as e:
                reconstruction_error = str(e)
                print(f"❌ Auto Arabic reconstruction failed: {e}")
        
        # Clean up temporary file if created
        if os.path.exists("temp_line_db.json"):
            os.remove("temp_line_db.json")
        
        # Return response with reconstruction status
        response_data = {
            "message": "Visualization created",
            "output": _public_file_info(_safe_name(req.visualized_pdf)),
            "auto_reconstruction": {
                "attempted": os.path.exists(ar_line_db_path) and os.path.exists(base_pdf_path),
                "success": reconstruction_success,
                "error": reconstruction_error,
                "output_file": AR_OUTPUT_PDF if reconstruction_success else None
            }
        }
        
        return JSONResponse(content={"ok": True, **response_data})
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Visualization ERROR: {error_trace}")
        
        if os.path.exists("temp_line_db.json"):
            os.remove("temp_line_db.json")
            
        return _json_err("Visualization failed", detail=f"{e}\n{error_trace}", status_code=500)




@app.get("/api/download")
def api_download(file: str = Query(..., description="Filename in storage")):
    try:
        fpath = _assert_file_exists(file)
        # Security: only serve from STORAGE_DIR
        if os.path.abspath(fpath).startswith(os.path.abspath(STORAGE_DIR)):
            return FileResponse(fpath, filename=os.path.basename(fpath), media_type="application/octet-stream")
        raise HTTPException(status_code=403, detail="Forbidden path")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
