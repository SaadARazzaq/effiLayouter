# 🧠 EffiLayouter — AI-Powered PDF Text Replacement & Layout Preservation Engine

EffiLayouter is a **FastAPI and ReactJS-based** engine designed to handle intelligent **PDF text removal, reconstruction, and translation** — all while preserving **the original graphics, colors, and vector layout** perfectly.

This system provides an **end-to-end pipeline** to:
✅ Upload a PDF
✅ Remove only the text layer (preserving visuals)
✅ Extract character or line-level data
✅ Translate text (Arabic or English supported)
✅ Reconstruct the PDF with translated text aligned exactly in its original layout
✅ Visualize line bounding boxes for debugging and layout inspection

No other open-source implementation removes text from PDFs **without disturbing their graphical or vector components** — EffiLayouter does it efficiently, layer by layer.

---

## 🚀 Features

| Function                               | Description                                                                      |
| -------------------------------------- | -------------------------------------------------------------------------------- |
| 🗂️ Upload                             | Upload any input PDF for processing                                              |
| ✂️ Text Removal                        | Removes all text streams while preserving layout, color, and vectors             |
| 🔠 Character Extraction                | Extracts character-level metadata and positional info                            |
| 🧩 English Reconstruction              | Rebuilds English text layer on top of the preserved background                   |
| 🕌 Arabic Translation & Reconstruction | Extracts lines, translates to Arabic, and reconstructs text layout right-to-left |
| 🎨 Visualization                       | Draws line bounding boxes for debugging and layout analysis                      |
| ♻️ Cleanup & Status                    | Check processing status or clean generated artifacts                             |
| 🧱 Frontend Integration                | Built for seamless connection with React (Vite-based) frontend                   |

---

## 🧩 Architecture Overview

EffiLayouter follows a **modular microservice-like pipeline** powered by FastAPI:

```
          ┌────────────┐
          │ Upload PDF │
          └─────┬──────┘
                │
                ▼
        ┌──────────────┐
        │ Remove Text   │  ← text_remover.py
        └─────┬────────┘
              │
              ▼
 ┌────────────────────┐
 │ Extract Characters │ ← text_extractor.py
 └────────┬───────────┘
          │
          ▼
 ┌────────────────────┐
 │ Reconstruct (EN)   │ ← pdf_reconstructor.py
 └────────┬───────────┘
          │
          ▼
 ┌────────────────────┐
 │ Extract Lines      │ ← contour_mapper.py
 └────────┬───────────┘
          │
          ▼
 ┌────────────────────┐
 │ Translate Arabic   │ ← integrated via PDFLineExtractor
 └────────┬───────────┘
          │
          ▼
 ┌────────────────────┐
 │ Reconstruct (AR)   │ ← ar_pdf_reconstructor.py
 └────────────────────┘
```

---

## ⚙️ API Endpoints

| Method   | Endpoint                   | Description                             |
| -------- | -------------------------- | --------------------------------------- |
| `POST`   | `/api/upload`              | Upload PDF file                         |
| `POST`   | `/api/remove-text`         | Remove all text from the PDF            |
| `POST`   | `/api/extract-characters`  | Extract character-level data from PDF   |
| `POST`   | `/api/reconstruct/english` | Rebuild English text layer              |
| `POST`   | `/api/extract-lines`       | Extract line-level layout and text      |
| `POST`   | `/api/translate/arabic`    | Translate extracted lines to Arabic     |
| `POST`   | `/api/reconstruct/arabic`  | Rebuild Arabic PDF with translated text |
| `POST`   | `/api/visualize-lines`     | Visualize detected line boxes           |
| `POST`   | `/api/workflow`            | Run complete English or Arabic pipeline |
| `DELETE` | `/api/cleanup`             | Remove all generated files except input |
| `GET`    | `/api/download?file=`      | Download any generated file             |
| `GET`    | `/api/status`              | Check all file statuses                 |
| `GET`    | `/api/_routes`             | List all available routes               |

---

## 🧠 Core Logic Explained

EffiLayouter’s brilliance lies in how it separates and reconstructs the **PDF text layer** while maintaining the original visual fidelity:

### 🩻 Step-by-step Processing Logic:

1. **Text Removal (`text_remover.py`)**

   * Parses PDF’s `/Contents` stream.
   * Identifies and removes only **text-related operators** (`Tj`, `TJ`, `Tf` etc.).
   * Keeps all **vector drawings, images, and fills** untouched.
   * Outputs `input_text_removed.pdf`.

2. **Text Extraction (`text_extractor.py`)**

   * Extracts each character’s position (`x`, `y`), font size, and Unicode content.
   * Serializes all pages into a structured JSON (`extracted_data.json`).

3. **Reconstruction (English)**

   * Reads the extracted JSON and re-draws characters at exact coordinates.
   * Outputs `english_reconstructed_input.pdf`.

4. **Arabic Pipeline (via `countour_mapper.py` + `ar_pdf_reconstructor.py`)**

   * Extracts **line segments** and sentence boundaries.
   * Translates them into Arabic (via `translate_to_arabic` API using async workers).
   * Reconstructs a new text layer respecting **RTL alignment** and original line structure.

5. **Visualization**

   * Draws bounding boxes over lines to visually inspect extraction accuracy.
   * Optionally triggers a non-blocking Arabic reconstruction for preview.

6. **Output**

   * The system produces 3 major outputs:

     * `input_text_removed.pdf` — visuals only
     * `english_reconstructed_input.pdf` — re-rendered English
     * `arabic_reconstructed_input.pdf` — re-rendered Arabic

---

## 🎥 Demo Video

Complete DEMO video Available here:

https://customer-qzr02zkeqcppma24.cloudflarestream.com/3db58402182ab21d28097d3bb2ec0b65/watch

---

## 🧰 Installation

```bash
# Clone the repo
git clone https://github.com/SaadARazzaq/effilayouter.git
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # (on Windows: venv\Scripts\activate)

# Install dependencies
pip install -r requirements.txt
```

---

## 🧪 Running the Server

```bash
uvicorn main:app --reload --port 8008
```

Your backend will be available at
📍 **[http://localhost:8008](http://localhost:8008)**

---

## 🔗 Frontend Integration

EffiLayouter is designed to pair with a **React (Vite)** frontend.
Example routes are automatically CORS-enabled, so you can call:

```javascript
POST http://localhost:8008/api/upload
POST http://localhost:8008/api/remove-text
POST http://localhost:8008/api/workflow?language=en
POST http://localhost:8008/api/workflow?language=ar
```

```bash
cd frontend

# Install dependencies
npm install

npm run dev
```

---

## 👨‍💻 Author

**Saad Abdur Razzaq**
AI & ML Engineer | Effixly

📫 [LinkedIn](https://linkedin.com/in/saadarazzaq)
📧 [sabdurrazzaq124@gmail.com](mailto:sabdurrazzaq124@gmail.com)

---

## 🧠 Future Enhancements

* ✨ Add support for multi-language translation beyond Arabic
* 🧩 Integrate OCR fallback for image-based PDFs
* 🕵️ Include AI-based layout refinement for overlapping text areas
* ⚙️ Optimize multiprocessing for high-resolution documents
