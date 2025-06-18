# 🏥 Medical Note Structuring Assistant

## Overview

🏥 **Real-World Use Case:**  
HealthCare+ Clinic has physicians who take unstructured notes during patient visits. These notes are often messy, vary in length, and lack consistency. The clinic needs an AI assistant that can:

- Parse unstructured clinical notes  
- Extract structured fields like **symptoms**, **diagnosis**, **medications**, and **follow-up recommendations**  
- Output a clean, structured summary suitable for **EMR systems** or printing  

---

This project delivers an **AI-powered assistant** designed to solve this exact problem. It converts free-form medical notes into structured, machine-readable data, helping healthcare providers organize clinical information quickly and accurately — ideal for **Electronic Medical Record (EMR)** integration or further analysis.
## Features

* **Intelligent Data Extraction:** Utilizes a Llama2 Large Language Model via Ollama to accurately extract structured fields such as Symptoms, Diagnosis, Medications, and Follow-up Instructions from raw clinical notes. 
* **Batch Processing:** Supports uploading CSV files containing multiple clinical notes for efficient batch extraction. 
* **User-Friendly Interface (Streamlit):**
    * Clean and intuitive design with custom CSS for an enhanced aesthetic.
    * Real-time progress updates during batch processing.
    * Clear error handling and feedback messages.
* **Interactive Data Visualizations:** Provides immediate insights into the extracted data with charts showing:
    * Top 5 Diagnoses.
    * Top 10 Reported Symptoms.
    * Top 10 Prescribed Medications.
* **Structured Output & Export:** Displays extracted data in a clear, tabular format and allows easy export to a CSV file. 
* **Robust Backend (FastAPI):** A high-performance API handles the LLM integration and data processing. 

## Tech Stack

* **Backend:** FastAPI 
* **LLM Hosting:** Ollama + Llama2 
* **Frontend:** Streamlit (with Pandas, Matplotlib, Seaborn for data handling and visualization) 
* **Output:** CSV export 
* **Versioning:** Git + GitHub 

## How to Use

### Prerequisites

Before you begin, ensure you have the following installed:

* **Python 3.8+**
* **Docker** (Recommended for easily running Ollama)

### Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/medical-note-structurer.git](https://github.com/yourusername/medical-note-structurer.git)
    cd medical-note-structurer
    ```

2.  **Install Python Dependencies:**
    It's recommended to create a virtual environment first:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: `venv\Scripts\activate`
    ```
    Then, install the required libraries:
    ```bash
    pip install fastapi uvicorn requests pandas streamlit matplotlib seaborn
    ```
    *(For a production setup, you might want to create separate `requirements.txt` files for `backend` and `frontend`.)*

3.  **Run Ollama and pull the Llama2 model:**
    Ensure your Ollama server is running (e.g., via Docker Desktop or direct installation). Then pull the `llama2` model:
    ```bash
    ollama pull llama2
    ```

 ## ▶️ Running the Application
1.  **Start the Backend API:**
    Navigate to the `backend` directory:
    ```bash
    cd backend
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    This will start the FastAPI server, usually accessible at `http://localhost:8000`.

2.  **Start the Frontend Application:**
    Open a *new* terminal, navigate to the `frontend` directory:
    ```bash
    cd frontend
    streamlit run app.py
    ```
    This will open the Streamlit application in your web browser (typically at `http://localhost:8501`).

3.  **Use the Application:**
    * In the Streamlit app, use the "Upload Your Data" section to select a CSV file.
    * Your CSV file **must** contain two columns: `patient_id` and `doctor_notes`.
    * The app will process the notes, display the structured data, and generate visualizations.
    * You can then download the structured notes as a new CSV file.

### Example Input CSV (`data/example_notes.csv`)

```csv
patient_id,doctor_notes
001,"Patient complains of fatigue and joint pain. Diagnosed with rheumatoid arthritis. Started on Methotrexate. Follow-up in 4 weeks."
002,"Severe cough and shortness of breath. Possible pneumonia. Started azithromycin. Advised rest and hydration. Follow-up in 7 days."
003,"Chronic headaches and sensitivity to light. Suspected migraine. Prescribed Sumatriptan. Review in 2 weeks if symptoms persist."
004,"Fever and body aches. Diagnosed with influenza. Advised plenty of fluids and rest. Contact clinic if condition worsens in 3 days."
 ```

### Screenshots
![image](https://github.com/user-attachments/assets/f87a95fb-7e4d-4376-aed6-d9baf66d9265)
![image](https://github.com/user-attachments/assets/5b212d2a-af70-4d8e-8b1f-b582e02c378b)

