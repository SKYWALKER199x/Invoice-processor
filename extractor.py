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
        "Extract ONLY the following from this invoice: Customer Name, Invoice ID, Invoice Date, Organization. Format it clearly like:\nCustomer Name: ...\nInvoice ID: ...\nInvoice Date: ...\nOrganization: ...",
        {"mime_type": "image/jpeg", "data": image_data}
    ])

    return parse_invoice_data(response.text)

def extract_from_pdf(file_path):
    with open(file_path, "rb") as pdf_file:
        pdf_data = pdf_file.read()

    response = model.generate_content([
        "Extract ONLY the following from this invoice PDF: Customer Name, Invoice ID, Invoice Date, Organization. Format it clearly like:\nCustomer Name: ...\nInvoice ID: ...\nInvoice Date: ...\nOrganization: ...",
        {"mime_type": "application/pdf", "data": pdf_data}
    ])

    return parse_invoice_data(response.text)

def parse_invoice_data(text):
    customer_name = invoice_id = invoice_date = organization = ""
    items = []

    for line in text.split("\n"):
        line = line.strip()
        if "Customer Name" in line:
            customer_name = line.split(":", 1)[1].strip()
        elif "Invoice ID" in line:
            invoice_id = line.split(":", 1)[1].strip()
        elif "Invoice Date" in line:
            invoice_date = line.split(":", 1)[1].strip()
        elif "Organization" in line:
            organization = line.split(":", 1)[1].strip()
        else:
            # Basic item parser (e.g., "Item Name   2   $20")
            match = re.match(r"(.+?)\s+(\d+)\s+\\$?\\d+", line)
            if match:
                item_name = match.group(1).strip()
                quantity = match.group(2).strip()
                items.append((item_name, quantity))

    return {
        "customer_name": customer_name,
        "invoice_id": invoice_id,
        "invoice_date": invoice_date,
        "organization": organization,
        "items": items  # New!
    }



