import google.generativeai as genai
import base64
import re
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-1.5-flash")

def extract_text_from_file(file_path):
    if file_path.lower().endswith(".pdf"):
        return extract_from_pdf(file_path)
    elif file_path.lower().endswith((".jpg", ".jpeg", ".png")):
        return extract_from_image(file_path)
    else:
        raise ValueError("Unsupported file type")

def extract_from_image(file_path):
    with open(file_path, "rb") as img_file:
        image_data = img_file.read()

    response = model.generate_content([
        """Extract the following from this invoice:
1. Customer Name
2. Invoice ID
3. Invoice Date
4. Organization
5. Total Amount (as a number)
6. List of items with their quantities and prices (in format: Item Name | Quantity | Price)

Format the output like:
Customer Name: ...
Invoice ID: ...
Invoice Date: ...
Organization: ...
Total Amount: ...

Items:
- Item Name 1 | Quantity | Price
- Item Name 2 | Quantity | Price
...""",
        {"mime_type": "image/jpeg", "data": image_data}
    ])

    return parse_invoice_data(response.text)

def extract_from_pdf(file_path):
    with open(file_path, "rb") as pdf_file:
        pdf_data = pdf_file.read()

    response = model.generate_content([
        """Extract the following from this invoice PDF:
1. Customer Name
2. Invoice ID
3. Invoice Date
4. Organization
5. Total Amount (as a number)
6. List of items with their quantities and prices (in format: Item Name | Quantity | Price)

Format the output like:
Customer Name: ...
Invoice ID: ...
Invoice Date: ...
Organization: ...
Total Amount: ...

Items:
- Item Name 1 | Quantity | Price
- Item Name 2 | Quantity | Price
...""",
        {"mime_type": "application/pdf", "data": pdf_data}
    ])

    return parse_invoice_data(response.text)

def parse_invoice_data(text):
    data = {
        "customer_name": "",
        "invoice_id": "",
        "invoice_date": "",
        "organization": "",
        "total_amount": 0.0,
        "items": []
    }

    lines = text.split("\n")
    items_section = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.lower().startswith("items:"):
            items_section = True
            continue

        if items_section:
            if line.startswith("-"):
                parts = [p.strip() for p in line[1:].split("|")]
                if len(parts) >= 3:
                    try:
                        item_data = {
                            "name": parts[0],
                            "quantity": int(parts[1]),
                            "price": float(parts[2].replace(",", "").replace("$", ""))  # Ensure no $ signs
                        }
                        data["items"].append(item_data)
                    except (ValueError, IndexError):
                        continue    
        else:
            if "Customer Name:" in line:
                data["customer_name"] = line.split(":", 1)[1].strip()
            elif "Invoice ID:" in line:
                data["invoice_id"] = line.split(":", 1)[1].strip()
            elif "Invoice Date:" in line:
                data["invoice_date"] = line.split(":", 1)[1].strip()
            elif "Organization:" in line:
                data["organization"] = line.split(":", 1)[1].strip()
            elif "Total Amount:" in line:
                try:
                    data["total_amount"] = float(line.split(":", 1)[1].strip().replace(",", ""))
                except (ValueError, IndexError):
                    pass

    return data