# 🚗 Call Analytics Dashboard

AI-powered information extraction and analysis system for automobile service center call transcripts.

[![Live Dashboard](https://img.shields.io/badge/Live-Dashboard-blue?style=for-the-badge)](https://your-username.github.io/your-repo/dashboard.html)
[![Success Rate](https://img.shields.io/badge/Success_Rate-99%25-success?style=for-the-badge)](outputs/extracted_calls.csv)
[![Calls Analyzed](https://img.shields.io/badge/Calls-100-orange?style=for-the-badge)](outputs/extracted_calls.csv)

---

## 🎯 Project Overview

This project implements an end-to-end pipeline for extracting structured information from customer service call transcripts for automobile dealerships and service centers (Tata, Mahindra, etc.).

### 🤖 Powered by Google Gemini 2.0 Flash

The system uses **Gemini 2.0 Flash (Experimental)** for intelligent information extraction from multilingual call transcripts.

---

## 📊 Key Statistics

| Metric | Value |
|--------|-------|
| **Total Calls Analyzed** | 100 |
| **Successful Extractions** | 99 (99%) |
| **Languages Supported** | 6 (Hindi, Tamil, Kannada, Marathi, Malayalam, Punjabi) |
| **Leads Identified** | 71 (71% conversion) |
| **High Priority Calls** | 9 |
| **Negative Sentiment Calls** | 9 |
| **Fields Extracted** | 28 per call |

---

## ✨ Features

### 📋 Interactive Dashboard
- **Real-time data visualization** with interactive charts
- **Advanced filtering** by language, sentiment, priority, lead status
- **Global search** across all 28 columns
- **Export functionality** - download filtered data as CSV
- **Responsive design** - works on desktop, tablet, mobile

### 🔍 Extracted Information (28 Fields)
- Call summary & customer intent
- Sentiment analysis (positive/neutral/negative)
- Entity extraction (names, locations, car models, amounts, dates, phone numbers)
- Lead identification & priority scoring
- Agent performance evaluation
- Business insights & recommended actions

### 📈 Analytics Tabs
1. **CSV Data View** - Complete data table with all columns
2. **Overview** - Language, category, priority, urgency distributions
3. **Lead Analysis** - Conversion metrics, hot leads identification
4. **Sentiment Analysis** - Sentiment trends, negative calls requiring action
5. **Performance** - Agent performance tracking and training needs

---

## 🛠️ Technology Stack

### Core Technologies
- **AI Model**: Google Gemini 2.0 Flash (Experimental)
- **Language**: Python 3.8+
- **LLM Integration**: google-generativeai SDK
- **Data Processing**: Pandas, OpenPyXL
- **Pattern Matching**: Regex (phones, amounts, car models, dates)

### Dashboard
- **Frontend**: HTML5, JavaScript, CSS3
- **Charts**: Chart.js
- **Tables**: DataTables (search, sort, pagination, export)
- **CSV Parsing**: PapaParse



## 🚀 How It Works

### 1. **Data Input**
- Input: Excel file with call transcripts
- Columns: Language, Transcript, Romanized Transcript
- Uses: Romanized Transcript (English version) for better LLM performance

### 2. **Text Preprocessing**
```python
- Normalize whitespace
- Standardize speaker tags (Agent:/Customer:)
- Remove noise and formatting issues
```

### 3. **LLM Extraction**
```python
- Model: Gemini 2.0 Flash (gemini-2.0-flash)
- Temperature: 0.1 (low for consistent extraction)
- Output: Structured JSON with 23 fields
- Retry Logic: 3 attempts with exponential backoff
- Rate Limiting: 4-second delay between requests
```

### 4. **Regex Enhancement**
Pattern matching for validation and additional extraction:
- **Phone Numbers**: Indian format (10 digits)
- **Amounts**: ₹, lakhs, thousands, crores
- **Car Models**: Dictionary matching (Nexon, Punch, Tiago, etc.)
- **Dates**: DD/MM/YYYY patterns

### 5. **Output Generation**
- Flatten JSON to CSV row
- Merge LLM + regex extractions
- 28 total columns per call
- Save to `outputs/extracted_calls.csv`

---

## 📊 Extraction Schema

### Core Fields (23 from LLM)

**Call Analysis**
- `call_summary` - 2-line summary
- `intent` - Customer's primary purpose
- `issue_category` - sales, technical, booking, complaint, etc.
- `outcome` - Call resolution
- `sentiment` - positive/neutral/negative
- `sentiment_score` - 0.0 to 1.0

**Entity Extraction**
- `customer_name`, `agent_name`
- `showroom_name`, `location`
- `car_model` - Vehicle(s) discussed
- `date_mentioned`, `amount`
- `booking_id`, `phone_number`

**Business Intelligence**
- `is_lead` - Boolean: potential sales opportunity
- `priority` - high/medium/low
- `urgency` - high/medium/low
- `next_action` - Recommended follow-up
- `agent_performance` - good/average/poor
- `additional_insights` - Business context

### Regex Validation Fields (5)
- `regex_phone_numbers` - Phones found via pattern
- `regex_amounts` - Monetary values found
- `regex_car_models` - Models detected
- `regex_dates` - Dates extracted



