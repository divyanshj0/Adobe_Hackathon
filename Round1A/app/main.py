import fitz  # PyMuPDF
import json
import re
import os
import argparse
from typing import List, Dict, Optional

class PDFOutlineExtractor:
    def __init__(self):
        self.title = ""
        self.outline = []
        self.font_size_stats = {}
        self.page_count = 0
        self.min_heading_length = 3
        self.ignore_patterns = [
            r"^\d+$",  # Page numbers
            r"^[ivx]+$",  # Roman numerals
            r"^[A-Za-z]\s*$",  # Single letter
            r"^[A-Z]\.\s*$",  # Single letter with dot
            r"^-+$",  # Lines of dashes
            r"^\.+$",  # Lines of dots
            r"^[\W_]+$",  # Only symbols
        ]

    def extract_outline(self, pdf_path: str) -> Dict:
        """Extract title and outline from PDF"""
        doc = fitz.open(pdf_path)
        self.page_count = len(doc)
        self._analyze_font_sizes(doc)
        self._extract_title(doc)
        self._extract_headings(doc)
        doc.close()
        
        return {
            "title": self._clean_text(self.title),
            "outline": self.outline
        }

    def _analyze_font_sizes(self, doc) -> None:
        """Analyze font sizes to determine heading hierarchy"""
        font_sizes = []
        
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if len(text) >= self.min_heading_length:
                                font_sizes.append(span["size"])
        
        if font_sizes:
            unique_sizes = sorted(list(set(font_sizes)), reverse=True)
            self.font_size_stats = {
                "h1": unique_sizes[0] if len(unique_sizes) > 0 else None,
                "h2": unique_sizes[1] if len(unique_sizes) > 1 else None,
                "h3": unique_sizes[2] if len(unique_sizes) > 2 else None,
            }

    def _extract_title(self, doc) -> None:
        """Extract title from first page"""
        first_page = doc[0]
        blocks = first_page.get_text("dict")["blocks"]
        max_size = 0
        title_candidates = []
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        size = span["size"]
                        if len(text) >= self.min_heading_length:
                            if size > max_size:
                                max_size = size
                                title_candidates = [text]
                            elif size == max_size:
                                title_candidates.append(text)
        
        if title_candidates:
            self.title = " ".join(title_candidates)
        
        # Fallback to first line if no title found
        if not self.title.strip():
            text = first_page.get_text()
            if text:
                first_line = text.split("\n")[0].strip()
                if len(first_line) >= self.min_heading_length:
                    self.title = first_line

    def _extract_headings(self, doc) -> None:
        """Extract headings from all pages"""
        for page_num, page in enumerate(doc, start=1):
            # Get all tables on the page
            tables = page.find_tables()
            table_bboxes = [table.bbox for table in tables]
            
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                # Skip blocks that are inside tables
                if self._is_in_table(block["bbox"], table_bboxes):
                    continue
                
                if "lines" in block:
                    current_line = []
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if len(text) >= self.min_heading_length:
                                if not any(re.fullmatch(pattern, text) for pattern in self.ignore_patterns):
                                    current_line.append({
                                        "text": text,
                                        "size": span["size"]
                                    })
                    
                    if current_line:
                        self._process_line(current_line, page_num)

    def _is_in_table(self, bbox, table_bboxes) -> bool:
        """Check if a block is inside any table"""
        x0, y0, x1, y1 = bbox
        for (tx0, ty0, tx1, ty1) in table_bboxes:
            if (x0 >= tx0 and x1 <= tx1 and y0 >= ty0 and y1 <= ty1):
                return True
        return False

    def _process_line(self, words: List, page_num: int) -> None:
        """Process a line of words to determine if it's a heading"""
        if not words:
            return
        
        text = " ".join(word["text"] for word in words).strip()
        text = self._clean_text(text)
        
        # Skip if text is too short or matches ignore patterns
        if len(text) < self.min_heading_length:
            return
            
        if any(re.fullmatch(pattern, text) for pattern in self.ignore_patterns):
            return
        
        avg_size = sum(word["size"] for word in words) / len(words)
        
        # Determine heading level
        level = self._determine_heading_level(avg_size)
        if level:
            self.outline.append({
                "level": level,
                "text": text,
                "page": page_num - 1  # Convert to 0-based index
            })

    def _determine_heading_level(self, size: float) -> Optional[str]:
        """Determine heading level based on font size"""
        if not self.font_size_stats:
            return None
            
        # Use relative size differences to determine heading level
        if self.font_size_stats["h1"] and size >= self.font_size_stats["h1"] * 0.85:
            return "H1"
        elif self.font_size_stats["h2"] and size >= self.font_size_stats["h2"] * 0.85:
            return "H2"
        elif self.font_size_stats["h3"] and size >= self.font_size_stats["h3"] * 0.75:
            return "H3"
        
        return None

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
        text = text.strip()
        return text


def process_pdfs(input_dir: str, output_dir: str) -> None:
    """Process all PDFs in input directory and save JSON outlines to output directory"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            json_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")
            
            extractor = PDFOutlineExtractor()
            result = extractor.extract_outline(pdf_path)
            
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract title and outline from PDFs.")
    parser.add_argument("--input", type=str, default="input", help="Input directory with PDFs")
    parser.add_argument("--output", type=str, default="output", help="Output directory for JSON files")
    args = parser.parse_args()

    process_pdfs(args.input, args.output)