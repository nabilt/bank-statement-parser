import fitz  # PyMuPDF
import sys
import os

def find_keyword_position(page, keyword):
    blocks = page.get_text("dict")["blocks"]
    for block in blocks:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                if keyword in span["text"]:
                    return span["bbox"]
    return None

def find_line_coords(page, line_type='s', stroke_opacity=1.0, color=(0.0, 0.0, 0.0), min_width=1, min_length=200):
    drawing_elements = page.get_drawings()
    
    for element in drawing_elements:
        if (
            element["type"] == line_type and
            element.get("stroke_opacity") == stroke_opacity and
            element.get("color") == color and
            abs(element.get("width", 0)) >= min_width
        ):
            for item in element["items"]:
                if item[0] == 'l':  # Line type
                    p1, p2 = item[1], item[2]
                    if p1.y == p2.y:  # Horizontal line
                        length = abs(p2.x - p1.x)
                        if length >= min_length:
                            return p1.x, p1.y, p2.x, p2.y
    
    return None

def detect_row_dividers(page, region, threshold=50):
    drawing_elements = page.get_drawings()
    y_coords = {}
    x0, y0, x1, y1 = region

    for element in drawing_elements:
        if element["type"] == "s" and element.get("dashes") == '[] 0':
            for item in element["items"]:
                if item[0] == 'l':
                    p1, p2 = item[1], item[2]
                    if p1.y == p2.y and y0 <= p1.y <= y1:  # Horizontal line within the y bounds of the region
                        if x0 <= p1.x <= x1 and x0 <= p2.x <= x1:  # Horizontal line within the x bounds of the region
                            y_coord = p1.y
                            if y_coord in y_coords:
                                y_coords[y_coord] += 1
                            else:
                                y_coords[y_coord] = 1

    row_dividers = [y for y, count in y_coords.items() if count >= threshold]
    return sorted(row_dividers)

def extract_text_with_positions(pdf_path, exclude_pages=None, keywords=("TRANSACTION")):
    if exclude_pages is None:
        exclude_pages = []

    pdf_document = fitz.open(pdf_path)
    pages_text_positions = []

    for page_num in range(len(pdf_document)):
        if page_num in exclude_pages:
            continue

        page = pdf_document.load_page(page_num)

        top_left = find_keyword_position(page, keywords[0])
        bottom_right = find_line_coords(page)

        if not top_left or not bottom_right:
            continue

        x0, y0, x01, y01 = top_left
        word_height = abs(y01 - y0)
        y0 += word_height
        
        _, _, x1, y1 = bottom_right
        margin = 2  # Adding a margin to ensure no content is excluded
        x0 -= margin
        region = (x0, y0, x1, y1)

        text_positions = []
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    sx0, sy0, sx1, sy1 = span["bbox"]

                    # Check if the text position is within the specified region
                    rx0, ry0, rx1, ry1 = region
                    if not (rx0 <= sx0 <= rx1 and ry0 <= sy0 <= ry1):
                        continue

                    text_positions.append({
                        "text": span["text"],
                        "bbox": span["bbox"],  # Bounding box
                        "page_num": page_num + 1
                    })

        row_dividers = detect_row_dividers(page, region)
        row_dividers = [y0] + row_dividers
        #last_row = len(row_dividers)-1
        row_dividers.append(y1)
        
        pages_text_positions.append((text_positions, row_dividers))

    return pages_text_positions

def group_text_by_rows(text_positions, row_dividers, margin=0):
    grouped_rows = {row_divider: [] for row_divider in row_dividers}
    grouped_text = []

    for item in sorted(text_positions, key=lambda x: x["bbox"][1]):
        text = item["text"]
        y0 = item["bbox"][1]
        
        # Find the row divider that this text belongs to
        for i in range(len(row_dividers) - 1):
            if row_dividers[i] < y0 <= row_dividers[i + 1] + margin:
                grouped_rows[row_dividers[i]].append(item)
                break

    for row_divider in row_dividers[:-1]:
        if grouped_rows[row_divider]:
            # Sort current row by x-coordinate before adding
            current_row = sorted(grouped_rows[row_divider], key=lambda x: x["bbox"][0])
            grouped_text.append(" ".join([word["text"] for word in current_row]))

    return grouped_text

def contains_excluded_word(text, excluded_words):
    for word in excluded_words:
        if word in text:
            return True
    return False

def process_pdfs_in_folder(folder_path, exclude_pages=None, excluded_words=None):
    if excluded_words is None:
        excluded_words = [
            "PREVIOUS STATEMENT BALANCE",
            "Continued",
            "NET ACTIVITY AMOUNT OF MONTHLY"
        ]

    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            # Extract month and year from filename
            parts = filename.split('_')
            month = parts[5]
            year = parts[6].split("-")[1].split('.pdf')[0]
            
            print(f"Date: {month} {year}")
            
            text_positions = extract_text_with_positions(pdf_path, exclude_pages)
            for page_text_positions in text_positions:
                text_positions, row_dividers = page_text_positions
                grouped_text = group_text_by_rows(text_positions, row_dividers)
                for row in grouped_text:
                    if not contains_excluded_word(row, excluded_words):
                        print(row)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_pdfs.py <folder_path>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    process_pdfs_in_folder(folder_path)
