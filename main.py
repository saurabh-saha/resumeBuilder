import json
import argparse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

# Constants for Styling
PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN_TOP = 50
MARGIN_BOTTOM = 50
MARGIN_LEFT = 50
MARGIN_RIGHT = 50

INDENT_SMALL = 20
INDENT_LARGE = 40
MAX_TEXT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
LINE_HEIGHT = 14
SECTION_SPACING = 25
JOB_SPACING = 15

# Font sizes
FONT_HEADER = 18
FONT_SECTION_TITLE = 14
FONT_JOB_TITLE = 12
FONT_BODY = 10

# Fonts
FONT_BOLD = "Helvetica-Bold"
FONT_NORMAL = "Helvetica"
FONT_ITALIC = "Helvetica-Oblique"

### 📌 DATA MODELS
class Education:
    def __init__(self, data):
        self.institution = data.get("institution", "")
        self.degree = data.get("degree", "")
        self.year = data.get("year", "")

class Contribution:
    def __init__(self, data):
        if isinstance(data, dict):
            self.title = list(data.keys())[0]
            self.points = data[self.title]
        else:
            self.title = None
            self.points = [data]

class Experience:
    def __init__(self, data):
        self.company_name = data.get("company_name", "")
        self.title = data.get("title", "")
        self.date = data.get("date", "")
        self.description = [Contribution(desc) if isinstance(desc, dict) else desc for desc in data.get("description", [])]
        self.contribution = [Contribution(contrib) for contrib in data.get("contribution", [])] if "contribution" in data else []

class Skill:
    def __init__(self, data):
        self.management_skills = data.get("management_skills", [])
        self.technical_skills = data.get("technical_skills", {})

class Resume:
    def __init__(self, data):
        self.name = data.get("name", "")
        self.location = data.get("location", "")
        self.phone = data.get("phone", "")
        self.email = data.get("email", "")
        self.links = data.get("links", {})
        self.headline = data.get("headline", "")
        self.summary = data.get("summary", [])
        self.experience = [Experience(exp) for exp in data.get("experience", [])]
        self.skills = Skill(data.get("skills", {}))
        self.education = [Education(edu) for edu in data.get("education", [])]

### 📌 PDF GENERATOR CLASS
class ResumePDF:
    def __init__(self, resume: Resume, filename):
        self.resume = resume
        self.filename = filename
        self.pdf = canvas.Canvas(filename, pagesize=letter)
        self.y = PAGE_HEIGHT - MARGIN_TOP

    def draw_wrapped_text(self, text, font=FONT_NORMAL, size=FONT_BODY, bold=False, indent=0):
        self.pdf.setFont(FONT_BOLD if bold else font, size)
        wrapped_lines = simpleSplit(text, font, size, MAX_TEXT_WIDTH - indent)

        for line in wrapped_lines:
            if self.y < MARGIN_BOTTOM:
                self.pdf.showPage()
                self.y = PAGE_HEIGHT - MARGIN_TOP
                self.pdf.setFont(FONT_BOLD if bold else font, size)

            self.pdf.drawString(MARGIN_LEFT + indent, self.y, line)
            self.y -= LINE_HEIGHT

    def add_header(self):
        self.pdf.setFont(FONT_BOLD, FONT_HEADER)
        self.pdf.drawString(MARGIN_LEFT, self.y, self.resume.name)
        self.y -= SECTION_SPACING

        self.pdf.setFont(FONT_NORMAL, FONT_JOB_TITLE)
        self.draw_wrapped_text(self.resume.headline, size=FONT_JOB_TITLE)

        self.pdf.setFont(FONT_NORMAL, FONT_BODY)
        self.draw_wrapped_text(f"{self.resume.location} | {self.resume.phone} | {self.resume.email}")

        self.pdf.setFont(FONT_ITALIC, FONT_BODY)
        for key, value in self.resume.links.items():
            self.draw_wrapped_text(f"{key.capitalize()}: {value}")

    def add_section(self, title):
        self.pdf.setFont(FONT_BOLD, FONT_SECTION_TITLE)
        self.y -= SECTION_SPACING
        self.pdf.drawString(MARGIN_LEFT, self.y, title)
        self.y -= LINE_HEIGHT

    def add_summary(self):
        self.add_section("Summary")
        self.pdf.setFont(FONT_NORMAL, FONT_BODY)
        for line in self.resume.summary:
            self.draw_wrapped_text(f"• {line}")

    def add_experience(self):
        self.add_section("Experience")

        for job in self.resume.experience:
            self.pdf.setFont(FONT_BOLD, FONT_JOB_TITLE)
            self.y -= JOB_SPACING
            self.draw_wrapped_text(f"{job.company_name} - {job.title} ({job.date})", bold=True)

            self.pdf.setFont(FONT_NORMAL, FONT_BODY)
            for desc in job.description:
                if isinstance(desc, Contribution):
                    if desc.title:
                        self.draw_wrapped_text(f"{desc.title}:", bold=True, indent=INDENT_SMALL)
                    for point in desc.points:
                        self.draw_wrapped_text(f"• {point}", indent=INDENT_LARGE)
                else:
                    self.draw_wrapped_text(f"• {desc}")

            if job.contribution:
                self.pdf.setFont(FONT_BOLD, FONT_BODY)
                self.y -= LINE_HEIGHT
                self.draw_wrapped_text("Key Contributions:", bold=True, indent=INDENT_SMALL)
                self.pdf.setFont(FONT_NORMAL, FONT_BODY)
                for contrib in job.contribution:
                    if contrib.title:
                        self.draw_wrapped_text(f"{contrib.title}:", bold=True, indent=INDENT_SMALL)
                    for point in contrib.points:
                        self.draw_wrapped_text(f"• {point}", indent=INDENT_LARGE)

            self.y -= SECTION_SPACING

    def add_education(self):
        self.add_section("Education")
        self.pdf.setFont(FONT_NORMAL, FONT_BODY)

        for edu in self.resume.education:
            self.draw_wrapped_text(f"{edu.institution}", bold=True)
            self.draw_wrapped_text(f"{edu.degree} ({edu.year})", indent=INDENT_SMALL)
            self.y -= LINE_HEIGHT

    def add_skills(self):
        self.add_section("Skills")

        if self.resume.skills.management_skills:
            self.draw_wrapped_text("Management Skills:", bold=True)
            self.draw_wrapped_text(", ".join(self.resume.skills.management_skills), indent=INDENT_SMALL)

        if self.resume.skills.technical_skills:
            self.y -= LINE_HEIGHT
            self.draw_wrapped_text("Technical Skills:", bold=True)

            for category, items in self.resume.skills.technical_skills.items():
                self.pdf.setFont(FONT_BOLD, FONT_BODY)
                self.pdf.drawString(MARGIN_LEFT + INDENT_SMALL, self.y, f"{category}:")
                self.pdf.setFont(FONT_NORMAL, FONT_BODY)
                self.pdf.drawString(MARGIN_LEFT + INDENT_SMALL + 80, self.y, ", ".join(items))
                self.y -= LINE_HEIGHT

    def generate_pdf(self):
        self.add_header()
        self.add_summary()
        self.add_experience()
        self.add_skills()
        self.add_education()
        self.pdf.save()
        print(f"Resume saved as {self.filename}")

### 📌 COMMAND-LINE ARGUMENTS
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a resume PDF from a JSON file.")
    parser.add_argument("input_file", help="Path to the JSON input file")
    parser.add_argument("output_file", help="Path to the PDF output file")

    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as file:
            resume_data = json.load(file)

        resume_obj = Resume(resume_data)
        resume_pdf = ResumePDF(resume_obj, args.output_file)
        resume_pdf.generate_pdf()
    except Exception as e:
        print(f"Error: {e}")
