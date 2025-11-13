import os
import re
import json
import time
from typing import Dict, Any, Optional
import pandas as pd
from tqdm import tqdm
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


CAR_MODELS = [
    'Nexon', 'Punch', 'Tiago', 'Tigor', 'Altroz', 'Harrier', 'Safari',
    'Curvv', 'Tata EV', 'Nexon EV', 'Punch EV', 'Mahindra', 'Rolls Royce',
    'XUV', 'Scorpio', 'Thar', 'Bolero'
]


def clean_transcript(transcript: str) -> str:
    if not transcript or not isinstance(transcript, str):
        return ""
    

    text = re.sub(r'\s+', ' ', transcript)
    text = re.sub(r'(Agent|Customer)\s*:', r'\1:', text)
    
    return text.strip()


def extract_with_regex(transcript: str) -> Dict[str, Any]:
    regex_data = {}
    phone_pattern = r'\b\d{10}\b|\b\d{5}\s?\d{5}\b|\b\d{3}\s?\d{3}\s?\d{4}\b'
    phones = re.findall(phone_pattern, transcript)
    regex_data['phone_numbers_found'] = ', '.join(set(phones)) if phones else ''
    

    amount_pattern = r'₹\s?\d+[,\d]*|\b\d+[,\d]*\s?(?:rupees|lakhs|thousands|crores)\b'
    amounts = re.findall(amount_pattern, transcript, re.IGNORECASE)
    regex_data['amounts_mentioned'] = ', '.join(amounts[:5]) if amounts else ''
    

    found_models = []
    for model in CAR_MODELS:
        if re.search(rf'\b{model}\b', transcript, re.IGNORECASE):
            found_models.append(model)
    regex_data['car_models_detected'] = ', '.join(set(found_models)) if found_models else ''
    
    date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
    dates = re.findall(date_pattern, transcript)
    regex_data['dates_found'] = ', '.join(dates) if dates else ''
    
    return regex_data


def build_extraction_prompt(transcript: str, language: str) -> str:

    prompt = f"""You are an expert at analyzing customer service call transcripts from automobile showrooms and service centers.

The following is a transcript from a call originally in {language} (now romanized/translated to English):

TRANSCRIPT:
{transcript}

Extract the following information and return ONLY a valid JSON object (no markdown, no extra text):

{{
  "call_summary": "A 2-line summary of the call",
  "intent": "Primary intent/purpose of the customer's call",
  "issue_category": "One of: technical, sales, booking, complaint, general_inquiry, service_related, test_drive, price_inquiry, other",
  "sentiment": "One of: positive, neutral, negative",
  "sentiment_score": 0.5,
  "customer_name": "Customer's name if mentioned",
  "agent_name": "Agent's name if mentioned",
  "showroom_name": "Showroom or service center name if mentioned",
  "car_model": "Car model(s) discussed (e.g., Tata Nexon, Punch, etc.)",
  "location": "Location/city mentioned",
  "date_mentioned": "Any dates mentioned in the call",
  "amount": "Any price/amount discussed (numeric value only)",
  "booking_id": "Booking or order ID if mentioned",
  "phone_number": "Phone number if mentioned",
  "is_lead": true,
  "priority": "One of: high, medium, low",
  "urgency": "One of: high, medium, low",
  "next_action": "Recommended or mentioned next action",
  "outcome": "Outcome of the call if evident",
  "agent_performance": "One of: good, average, poor",
  "additional_insights": "Any other relevant business insights"
}}

Rules:
- Use empty string "" for missing text fields
- Use null for missing numeric fields
- Use false for missing boolean fields
- Ensure all field names match exactly as shown
- Return ONLY valid JSON, no markdown formatting
"""
    return prompt


def call_gemini_api(prompt: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY not found in environment variables")
        return None
    
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.1,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                }
            )
            
            response_text = response.text.strip()
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'^```\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
            

            data = json.loads(response_text)
            return data
            
        except json.JSONDecodeError as e:
            print(f"Attempt {attempt + 1}/{max_retries}: JSON parsing error - {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"Failed to parse JSON after {max_retries} attempts")
                return None
                
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries}: API error - {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"Failed API call after {max_retries} attempts")
                return None
    
    return None


def extract_call_info(transcript: str, language: str, row_index: int = 0) -> Dict[str, Any]:

    result = {
        'row_index': row_index,
        'original_language': language,
        'call_summary': '',
        'intent': '',
        'issue_category': '',
        'sentiment': 'neutral',
        'sentiment_score': 0.5,
        'customer_name': '',
        'agent_name': '',
        'showroom_name': '',
        'car_model': '',
        'location': '',
        'date_mentioned': '',
        'amount': None,
        'booking_id': '',
        'phone_number': '',
        'is_lead': False,
        'priority': 'medium',
        'urgency': 'medium',
        'next_action': '',
        'outcome': '',
        'agent_performance': 'average',
        'additional_insights': '',
        'extraction_status': 'failed',
        'error_message': ''
    }
    

    if not transcript or transcript.strip() == '':
        result['error_message'] = 'Empty transcript'
        return result
    
    try:

        cleaned = clean_transcript(transcript)
        

        regex_data = extract_with_regex(cleaned)
        

        prompt = build_extraction_prompt(cleaned, language)
        llm_data = call_gemini_api(prompt)
        
        if llm_data:

            for key, value in llm_data.items():
                if key in result:
                    result[key] = value
            
            result['extraction_status'] = 'success'
        else:
            result['extraction_status'] = 'llm_failed'
            result['error_message'] = 'LLM extraction failed'
        
        result['regex_phone_numbers'] = regex_data.get('phone_numbers_found', '')
        result['regex_amounts'] = regex_data.get('amounts_mentioned', '')
        result['regex_car_models'] = regex_data.get('car_models_detected', '')
        result['regex_dates'] = regex_data.get('dates_found', '')
        
    except Exception as e:
        result['extraction_status'] = 'error'
        result['error_message'] = str(e)
    
    return result


def main():

    INPUT_FILE = 'transcripts.xlsx'
    OUTPUT_DIR = 'outputs'
    OUTPUT_FILE = f'{OUTPUT_DIR}/extracted_calls.csv'

    if not os.getenv('GEMINI_API_KEY'):
        print("ERROR: GEMINI_API_KEY not found!")
        return
    
    print("="*80)
    print("CALL TRANSCRIPT INFORMATION EXTRACTION")
    print("="*80)
    print(f"\nUsing Gemini 2.0 Flash API")
    print(f"Input file: {INPUT_FILE}")
    print(f"Output file: {OUTPUT_FILE}\n")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"Loading data from {INPUT_FILE}...")
    try:
        df = pd.read_excel(INPUT_FILE)
        print(f"Loaded {len(df)} call transcripts")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Languages: {df['Language'].value_counts().to_dict()}\n")
    except Exception as e:
        print(f"ERROR loading Excel file: {e}")
        return
    

    print(f"Processing {len(df)} transcripts...\n")
    results = []
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Extracting"):
        transcript = row['Romanized Transcript']
        language = row['Language']
        

        result = extract_call_info(transcript, language, row_index=idx)
        results.append(result)
        
        # Add delay to avoid rate limiting (15 requests per minute = 4 seconds)
        time.sleep(4)
    
    print(f"\nProcessed all {len(results)} transcripts!\n")
    

    output_df = pd.DataFrame(results)
    

    print("="*80)
    print("EXTRACTION STATISTICS")
    print("="*80)
    print(f"\nTotal transcripts: {len(output_df)}")
    print(f"Successful extractions: {(output_df['extraction_status'] == 'success').sum()}")
    print(f"Failed extractions: {(output_df['extraction_status'] != 'success').sum()}")
    
    if len(output_df) > 0:
        success_rate = (output_df['extraction_status'] == 'success').sum() / len(output_df) * 100
        print(f"Success rate: {success_rate:.1f}%")
    
    print(f"\nSentiment distribution:")
    print(output_df['sentiment'].value_counts())
    
    print(f"\nIssue categories:")
    print(output_df['issue_category'].value_counts())
    
    print(f"\nLeads identified: {output_df['is_lead'].sum()}")
    print(f"High priority calls: {(output_df['priority'] == 'high').sum()}")
    

    output_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n{'='*80}")
    print(f"Results saved to: {OUTPUT_FILE}")
    print(f"  File size: {os.path.getsize(OUTPUT_FILE) / 1024:.2f} KB")
    print(f"  Total columns: {len(output_df.columns)}")
    print(f"  Total rows: {len(output_df)}")
    print(f"{'='*80}\n")
    

    print("Sample extracted data (first 3 rows):\n")
    sample_cols = ['row_index', 'original_language', 'call_summary', 'intent', 
                   'sentiment', 'car_model', 'is_lead', 'priority']
    print(output_df[sample_cols].head(3).to_string())
    
    print("\nExtraction complete!")


if __name__ == "__main__":
    main()
