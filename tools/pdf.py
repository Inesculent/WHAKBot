from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from io import BytesIO
import re
from langchain.tools import tool
from pydantic import BaseModel, Field


def parse_text_to_story(input_text):
    # Define some basic styles
    styles = getSampleStyleSheet()
    story = []

    # Split text by lines
    lines = input_text.split("\n")

    for line in lines:
        line = line.strip()

        # Headers
        if line.startswith("# "):
            story.append(Paragraph(line[2:], styles['Title']))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], styles['Heading2']))
        elif line.startswith("### "):
            story.append(Paragraph(line[4:], styles['Heading3']))

        # Bold and Italic (Basic Handling)
        elif "**" in line:
            formatted_line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)
            story.append(Paragraph(formatted_line, styles['Normal']))
        elif "*" in line:
            formatted_line = re.sub(r"\*(.*?)\*", r"<i>\1</i>", line)
            story.append(Paragraph(formatted_line, styles['Normal']))

        # Unordered List
        elif line.startswith("- "):
            list_items = [ListItem(Paragraph(line[2:], styles['Normal']))]
            story.append(ListFlowable(list_items, bulletType='bullet'))

        # Regular paragraph
        else:
            story.append(Paragraph(line, styles['Normal']))

        # Add some space after each element
        story.append(Spacer(1, 12))

    return story


def create_pdf(input_text, output_pdf_path):
    # Create a PDF document
    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)

    # Convert the text to a story (list of elements)
    story = parse_text_to_story(input_text)

    # Build the PDF
    doc.build(story)

    print(f"PDF created successfully at {output_pdf_path}")


class PDF(BaseModel):
    text: str = Field(
        description="Markown text to convert to PDF, provided in valid markdown format."

    )

@tool("create_pdf", args_schema=PDF)
def create_pdf(text: str) -> str:
    """Create a PDF on the information of the person your client is trying to find by converting markdown text to PDF"""
    create_pdf(text, output_pdf_path="outputtttttttt.pdf")


if __name__ == "__main__":
    # Example usage
    input_text = """
    # Welcome to My Document
    
    This is a **bold** text and this is an *italic* text. Below is a list:
    
    - Item 1
    - Item 2
      - Sub-item 1
      - Sub-item 2
    - Item 3
    
    ## Sub-heading
    
    Some more text with a **bold** emphasis.
    
    """

    output_pdf_path = "AAAAAAAAAAAAAAAAAMKGLJGFL.pdf"
    create_pdf(input_text, output_pdf_path)
