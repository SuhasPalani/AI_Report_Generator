import streamlit as st
import time
from report_generator import generate_report

openai_api_key = st.secrets["OPENAI_API_KEY"]
mistral_api_key = st.secrets["MISTRAL_API_KEY"]

def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        st.info(f"Report generation completed in {execution_time:.2f} seconds.")
        return result

    return wrapper


@measure_execution_time
def generate_report_with_timing(*args, **kwargs):
    return generate_report(*args, **kwargs)


def main():
    st.title("AI Report Generator")

    # Project Name
    project_name = st.text_input("Enter Project Name")

    # Upload images
    st.header("Upload Images")
    uploaded_images = st.file_uploader(
        "Choose images", accept_multiple_files=True, type=["png", "jpg", "jpeg"]
    )

    # Select sections
    st.header("Select Report Sections")
    sections = st.multiselect(
        "Choose sections for your report",
        [
            "Introduction",
            "Problem Statement",
            "Methodology",
            "Results",
            "Discussion",
            "Conclusion",
        ],
    )

    # Input section descriptions
    st.header("Section Descriptions")
    section_descriptions = {}
    for section in sections:
        section_descriptions[section] = st.text_area(f"Brief description for {section}")

    # Set word limit
    total_word_limit = st.number_input(
        "Set total word limit for the report", min_value=100, value=1000, step=100
    )

    # Match images to sections
    st.header("Match Images to Sections")
    image_section_mapping = {}
    for i, image in enumerate(uploaded_images):
        section = st.selectbox(f"Select section for Image {i + 1}", [""] + sections)
        if section:
            image_section_mapping[image.name] = section

    # Custom styling options
    st.header("Custom Styling")
    font = st.selectbox("Choose font", ["Calibri", "Arial", "Times New Roman"])
    color = st.color_picker("Choose accent color", "#000000")

    # Table of Contents
    include_toc = st.checkbox("Include Table of Contents")

    # Citations
    citations = st.text_area("Enter citations (one per line)")

    if st.button("Generate Report"):
        if project_name and sections and all(section_descriptions.values()):
            doc = generate_report_with_timing(
                project_name,
                sections,
                section_descriptions,
                total_word_limit,
                image_section_mapping,
                uploaded_images,
                font,
                color,
                include_toc,
                citations,
            )
            st.success("Report generated successfully!")
            st.download_button(
                label="Download Report",
                data=doc,
                file_name=f"{project_name}_report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        else:
            st.error("Please fill in all required fields, including the project name.")


if __name__ == "__main__":
    main()
