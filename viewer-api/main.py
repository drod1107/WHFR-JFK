from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import List
import os

app = FastAPI()

# Allow local frontend to call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Path to your processed files (adjust if needed)
PROCESSED_DOCS_PATH = Path("/app/shared/processed_docs")

@app.get("/search")
def search_text(q: str = Query(..., min_length=1)) -> List[dict]:
    """
    Search all .txt files in processed_docs for the query string.
    """
    results = []

    for txt_file in PROCESSED_DOCS_PATH.rglob("*.txt"):
        try:
            with open(txt_file, "r", encoding="utf-8") as f:
                for i, line in enumerate(f.readlines()):
                    if q.lower() in line.lower():
                        # Get corresponding PNG (same base name)
                        png_path = txt_file.with_suffix(".png")
                        if png_path.exists():
                            png_rel = str(png_path.relative_to(PROCESSED_DOCS_PATH))
                        else:
                            png_rel = None

                        results.append({
                            "file": txt_file.name,
                            "line_number": i + 1,
                            "match_text": line.strip(),
                            "png_file": png_rel,
                        })
        except Exception as e:
            print(f"Error reading {txt_file}: {e}")
            continue

    return results
