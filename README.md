# AI Report Generator

## Description
This project is an AI-powered report generator that uses OpenAI's GPT-4 and Mistral AI to create customized reports based on user input. It features a Streamlit interface for easy interaction, allows for custom styling, and includes image integration with AI-generated captions.

## Features
- Dynamic report generation based on user-defined sections
- Custom styling options (font, color)
- Image upload and integration into the report
- AI-generated content using OpenAI's GPT-4
- Content enhancement using Mistral AI to meet word count requirements
- Automatic table of contents generation
- Citation and reference management

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-report-generator.git
   cd ai-report-generator
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following content:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   MISTRAL_API_KEY=your_mistral_api_key_here
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and go to the URL provided by Streamlit (usually `http://localhost:8501`).

3. Follow the on-screen instructions to:
   - Enter your project name
   - Upload images
   - Select report sections
   - Provide descriptions for each section
   - Set word limits
   - Choose styling options
   - Add citations

4. Click "Generate Report" to create your customized report.

5. Download the generated report as a Word document.

## File Structure
- `app.py`: Main Streamlit application
- `report_generator.py`: Core logic for report generation
- `requirements.txt`: List of Python dependencies
- `.env`: Environment variables (API keys)


