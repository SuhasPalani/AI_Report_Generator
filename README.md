# AI Report Generator

## Description
This project is an AI-powered report generator that uses OpenAI's GPT-4 and Mistral AI to create customized reports based on user input. It features a Streamlit interface for easy interaction, allows for custom styling, and includes image integration with AI-generated captions. Additionally, it now includes the ability to generate architecture diagrams based on Python code, providing a visual representation of the code structure and its relationships.

## Features
- Dynamic report generation based on user-defined sections
- Custom styling options (font, color)
- Image upload and integration into the report
- AI-generated content using OpenAI's GPT-4
- Content enhancement using Mistral AI to meet word count requirements
- Automatic table of contents generation
- Citation and reference management
- **Architecture Diagram Generation:** Automatically generates a visual flowchart/architecture diagram from Python code blocks to showcase module relationships, function calls, and class structures.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/SuhasPalani/AI_Report_Generator
   cd directory_name
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
   - **Generate Architecture Diagram:** Optionally, provide Python code blocks to generate an architecture diagram for your project.

4. Click "Generate Report" to create your customized report.

5. Download the generated report as a Word document.

## File Structure
- `app.py`: Main Streamlit application
- `report_generator.py`: Core logic for report generation
- `architecture.py`: Logic for analyzing Python code and generating architecture diagrams
- `requirements.txt`: List of Python dependencies
- `.env`: Environment variables (API keys)

