import streamlit as st
import time
from report_generator import generate_report
from improved_code_analysis import generate_detailed_mermaid, analyze_python_code

# openai_api_key = st.secrets["OPENAI_API_KEY"]
# mistral_api_key = st.secrets["MISTRAL_API_KEY"]


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
    st.title("AI Report & Architecture Generator")

    # Add tabs for different functionalities
    tab1, tab2 = st.tabs(["Generate Report", "Generate Architecture Diagram"])

    with tab1:
        # Original Report Generation functionality
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
            section_descriptions[section] = st.text_area(
                f"Brief description for {section}"
            )

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
                st.error(
                    "Please fill in all required fields, including the project name."
                )

    with tab2:
        # Improved Architecture Diagram Generator
        st.header("Code Architecture Diagram Generator")
        st.write("""
        Paste your Python code blocks below, and we'll generate a detailed architecture diagram showing functions, 
        classes, and their relationships. Each block can be a separate file or code section.
        """)

        # Container for code blocks
        code_blocks = []

        # Files/modules option
        num_blocks = st.number_input(
            "Number of code blocks/files", min_value=1, value=2, step=1
        )

        for i in range(num_blocks):
            # Allow the user to provide a filename
            col1, col2 = st.columns([1, 5])
            with col1:
                filename = st.text_input(
                    f"File {i + 1} name (optional)",
                    key=f"filename_{i}",
                    placeholder="e.g. app.py",
                )

            with col2:
                code_block = st.text_area(
                    f"Code Block {i + 1}",
                    height=200,
                    key=f"block_{i}",
                    placeholder="Paste your Python code here...",
                )

            if code_block.strip():
                # Add filename as a comment if provided
                if filename and not code_block.startswith(f"# {filename}"):
                    code_block = f"# {filename}\n{code_block}"
                code_blocks.append(code_block)

        # Diagram generation options
        st.subheader("Diagram Options")

        col1, col2 = st.columns(2)
        with col1:
            show_details = st.checkbox(
                "Show detailed class and function information", value=True
            )
        with col2:
            layout_direction = st.selectbox(
                "Diagram direction",
                options=["Top to Bottom (TD)", "Left to Right (LR)"],
                index=0,
            )

        if st.button("Generate Architecture Diagram"):
            if code_blocks:
                with st.spinner("Analyzing code and generating diagram..."):
                    # Replace TD with LR if needed
                    direction = (
                        "TD" if layout_direction == "Top to Bottom (TD)" else "LR"
                    )

                    try:
                        # Generate the detailed mermaid diagram
                        mermaid_code = generate_detailed_mermaid(code_blocks)

                        # Replace the direction if needed
                        if direction == "LR":
                            mermaid_code = mermaid_code.replace(
                                "flowchart TD", "flowchart LR"
                            )

                        # Display the code analysis results
                        modules = analyze_python_code(code_blocks)

                        # Success message
                        st.success("Architecture diagram generated successfully!")

                        # Display the diagram
                        st.subheader("Architecture Diagram")
                        st.markdown(f"```mermaid\n{mermaid_code}\n```")

                        # Show code structure analysis
                        with st.expander("View Code Structure Analysis"):
                            for i, module in enumerate(modules):
                                st.write(f"**Module {i + 1}: {module['main_name']}**")

                                if module["functions"]:
                                    st.write("Functions:")
                                    for func in module["functions"]:
                                        st.write(
                                            f"- {func['name']}({', '.join(func['args'])})"
                                        )

                                if module["classes"]:
                                    st.write("Classes:")
                                    for cls in module["classes"]:
                                        st.write(f"- {cls['name']}")
                                        if cls["methods"]:
                                            for method in cls["methods"]:
                                                st.write(f"  - {method}()")

                                st.write("---")

                        # Provide download options
                        st.download_button(
                            label="Download Mermaid Code",
                            data=mermaid_code,
                            file_name="architecture_diagram.mmd",
                            mime="text/plain",
                        )

                    except Exception as e:
                        st.error(f"Error generating diagram: {str(e)}")
                        st.error(
                            "Please check your code for syntax errors or try simplifying the code blocks."
                        )
            else:
                st.error("Please add at least one code block to generate a diagram.")


if __name__ == "__main__":
    main()
