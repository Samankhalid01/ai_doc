import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.extractor import extract_fields

text = 'Invoice number: 6312 Account: PATZD32 Subtotal 58,658.00 Date: 11/15/2025\nCompany: ABC Traders'
print(extract_fields('invoice', text))

text_cv = 'Experienced developer with 5 years of experience. Skills: Python, Docker, AWS'
print(extract_fields('cv', text_cv))

text_id = 'Name: John Doe\nDOB: 02/14/1990\nAddress: 123 Main St, Cityville'
print(extract_fields('id_card', text_id))