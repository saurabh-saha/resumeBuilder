from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from resume import Resume, Contribution
from constants import *
from templates.two_column_template import LayoutConfig

INDENT_SMALL = 20
INDENT_LARGE = 40


class BaseTemplate:
    def __init__(self, resume: Resume, filename, config: LayoutConfig):
        self.resume = resume
        self.filename = filename
        self.pdf = canvas.Canvas(filename, pagesize=letter)
        self.y = PAGE_HEIGHT - MARGIN_TOP
        self.config = config

    def draw_wrapped_text(self, text, font=FONT_NORMAL, size=FONT_BODY, bold=False, indent=0):
        if self.config.font_body and size == FONT_BODY:
            size = self.config.font_body
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
        """Adds the name, headline, and contact details."""
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
        """Adds section titles (Summary, Experience, etc.)."""
        self.pdf.setFont(FONT_BOLD, FONT_SECTION_TITLE)
        self.y -= SECTION_SPACING
        self.pdf.drawString(MARGIN_LEFT, self.y, title)
        self.y -= LINE_HEIGHT

    def add_summary(self):
        """Adds the Summary section."""
        self.add_section("Summary")
        self.pdf.setFont(FONT_NORMAL, FONT_BODY)
        for line in self.resume.summary:
            self.draw_wrapped_text(f"• {line}")

    def add_experience(self):
        """Adds the Experience section."""
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
        """Adds the Education section."""
        self.add_section("Education")
        self.pdf.setFont(FONT_NORMAL, FONT_BODY)

        for edu in self.resume.education:
            self.draw_wrapped_text(f"{edu.institution}", bold=True)
            self.draw_wrapped_text(f"{edu.degree} ({edu.year})", indent=INDENT_SMALL)
            self.y -= LINE_HEIGHT

    def add_skills(self):
        """Adds the Skills section."""
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
        """Generates the final PDF."""
        self.add_header()
        self.add_summary()
        self.add_experience()
        self.add_skills()
        self.add_education()
        self.pdf.save()
        print(f"Resume saved as {self.filename}")
