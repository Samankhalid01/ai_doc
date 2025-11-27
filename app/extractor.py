import re
from datetime import datetime

def extract_invoice(text):
    """Extract invoice fields with improved patterns."""
    extracted = {}
    
    # Find invoice number - various patterns
    invoice_patterns = [
        r"Invoice\s*(?:number|#|no\.?)[\s:]*([A-Z0-9-]+)",
        r"Involce\s*(?:number|#|no\.?)[\s:]*([A-Z0-9-]+)",  # Handle OCR typo
        r"Invoice[\s:]+([A-Z0-9-]+)",
    ]
    for pattern in invoice_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted["invoice_number"] = match.group(1)
            break
    
    # Find account number
    account_patterns = [
        r"Account\s*(?:number|#|no\.?)[\s:]*([A-Z0-9-]+)",
    ]
    for pattern in account_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted["account_number"] = match.group(1)
            break
    
    # Find total/subtotal - look for dollar amounts
    total_patterns = [
        r"(?:Sub)?total[\s:]*\$?([\d,]+\.?\d*)",
        r"Total[\s:]*\$?([\d,]+\.?\d*)",
        r"Amount[\s:]*\$?([\d,]+\.?\d*)",
    ]
    totals = []
    for pattern in total_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            amount = match.replace(',', '')
            try:
                totals.append(float(amount))
            except:
                pass

    if totals:
        extracted["invoice_total"] = max(totals)  # choose largest as total
        extracted["amounts_found"] = sorted(set(totals), reverse=True)[:5]
    
    # Find dates
    date_patterns = [
        r"\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b",
        r"\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b",
    ]
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text))
    def _parse_date_list(dates_list):
        parsed = []
        for d in dates_list:
            for fmt in ("%m/%d/%Y", "%m/%d/%y", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%B %d, %Y"):
                try:
                    dt = datetime.strptime(d, fmt)
                    parsed.append(dt.date().isoformat())
                    break
                except Exception:
                    continue
        return parsed

    if dates:
        extracted_dates = _parse_date_list(dates)
        if extracted_dates:
            extracted["date"] = extracted_dates[0]
        else:
            extracted["dates_found"] = dates[:3]
    
    # Find labor/hourly rates
    labor_pattern = r"LABOR.*?AMOUNT\s*(.*?)(?:MATERIAL|Subtotal|\Z)"
    labor_match = re.search(labor_pattern, text, re.DOTALL | re.IGNORECASE)
    if labor_match:
        labor_section = labor_match.group(1)
        # Extract amounts from labor section
        labor_amounts = re.findall(r"\$?([\d,]+\.?\d*)", labor_section)
        extracted["labor_costs"] = [amt.replace(',', '') for amt in labor_amounts if amt]
    
    # Find material costs
    material_pattern = r"MATERIAL.*?AMOUNT\s*(.*?)(?:Subtotal|Total|\Z)"
    material_match = re.search(material_pattern, text, re.DOTALL | re.IGNORECASE)
    if material_match:
        material_section = material_match.group(1)
        material_amounts = re.findall(r"\$?([\d,]+\.?\d*)", material_section)
        extracted["material_costs"] = [amt.replace(',', '') for amt in material_amounts if amt]
    
    return extracted

def extract_cv(text):
    """Extract CV/Resume fields."""
    extracted = {}
    
    # Find skills - common programming languages and technologies
    common_skills = ['Python', 'Java', 'JavaScript', 'C++', 'React', 'Node', 'SQL', 'AWS', 
                     'Docker', 'Kubernetes', 'Angular', 'Vue', 'TypeScript', 'Git']
    found_skills = [skill for skill in common_skills if skill.lower() in text.lower()]
    if found_skills:
        extracted["skills"] = found_skills
        extracted["technologies"] = found_skills
    
    # Find years of experience
    experience_patterns = [
        r"(\d+)\+?\s*years?\s*(?:of)?\s*experience",
        r"experience[:\s]*(\d+)\+?\s*years?",
    ]
    for pattern in experience_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # take first match and convert to int if possible
            try:
                extracted["experience"] = int(matches[0])
            except:
                extracted["experience"] = matches
            break
    
    # Find education
    education_keywords = ['Bachelor', 'Master', 'PhD', 'Degree', 'University', 'College']
    education = [keyword for keyword in education_keywords if keyword.lower() in text.lower()]
    if education:
        extracted["education_keywords"] = education
    
    return extracted

def extract_id(text):
    """Extract ID card fields."""
    extracted = {}
    
    # Find name patterns
    name_patterns = [
        r"Name[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
        r"Full\s*Name[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            extracted["name"] = match.group(1)
            break
    
    # Find date of birth
    dob_patterns = [
        r"(?:DOB|Date of Birth|Birth Date)[\s:]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
        r"Born[\s:]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
    ]
    for pattern in dob_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            dob_raw = match.group(1)
            # try to normalize to ISO
            for fmt in ("%m/%d/%Y", "%m/%d/%y", "%d-%m-%Y", "%d/%m/%Y"):
                try:
                    dob_dt = datetime.strptime(dob_raw, fmt)
                    extracted["dob"] = dob_dt.date().isoformat()
                    break
                except Exception:
                    continue
            else:
                extracted["dob"] = dob_raw
            break
    
    # Find ID number
    id_patterns = [
        r"ID[\s#:]*([A-Z0-9-]+)",
        r"(?:Card|License)\s*(?:Number|#)[\s:]*([A-Z0-9-]+)",
    ]
    for pattern in id_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted["id_number"] = match.group(1)
            break

    # Try to extract address
    addr_patterns = [r"Address[:\s]+(.+)", r"Addr[:\s]+(.+)", r"Residence[:\s]+(.+)"]
    for pattern in addr_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted["address"] = match.group(1).strip()
            break
    
    return extracted


def extract_fields(doc_type, text):
    # Return a clean structured JSON depending on document type
    if doc_type == "invoice":
        inv = extract_invoice(text)
        out = {
            "type": "invoice",
            "company": inv.get("company") if inv.get("company") else None,
            "invoice_total": inv.get("invoice_total"),
            "tax": inv.get("tax"),
            "date": inv.get("date"),
        }
        # remove None keys
        return {k: v for k, v in out.items() if v is not None}
    elif doc_type == "cv":
        cv = extract_cv(text)
        out = {
            "type": "cv",
            "skills": cv.get("skills", []),
            "experience": cv.get("experience"),
            "technologies": cv.get("technologies", []),
        }
        # Keep keys that are explicitly set (including experience when 0)
        return {k: v for k, v in out.items() if v is not None}
    elif doc_type == "id_card":
        idc = extract_id(text)
        out = {
            "type": "id_card",
            "name": idc.get("name"),
            "dob": idc.get("dob"),
            "address": idc.get("address"),
        }
        return {k: v for k, v in out.items() if v is not None}
    else:
        return {"message": "No extractor matched"}
