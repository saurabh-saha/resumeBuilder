from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from resume import Resume, Contribution
from constants import *

INDENT_SMALL = 10
INDENT_LARGE = 20
SUMMARY_Y = 60


class LayoutConfig:
    def __init__(self, education_size=FONT_BODY, line_height=LINE_HEIGHT, font_body=FONT_BODY):
        self.education_size = education_size
        self.line_height = line_height
        self.font_body = font_body


class TwoColumnTemplate:
    def __init__(self, resume: Resume, filename, config: LayoutConfig):
        self.resume = resume
        self.filename = filename
        self.pdf = canvas.Canvas(filename, pagesize=letter)

        self.left_x = MARGIN_LEFT
        self.right_x = MARGIN_LEFT + COLUMN_WIDTH_LEFT + COLUMN_GAP

        self.y_metadata = PAGE_HEIGHT - MARGIN_TOP
        self.y_summary = self.y_metadata - SUMMARY_Y
        self.y_left = self.y_summary - COLUMN_GAP
        self.y_right = self.y_summary - COLUMN_GAP

        self.config = config

    def draw_wrapped_text(self, text, x, y, max_width, font=FONT_NORMAL, size=FONT_BODY, bold=False, indent=0):
        self.pdf.setFont(FONT_BOLD if bold else font, size)
        wrapped_lines = simpleSplit(text, font, size, max_width - indent)

        for line in wrapped_lines:
            if y < MARGIN_BOTTOM:
                self.pdf.showPage()
                y = PAGE_HEIGHT - MARGIN_TOP
                self.pdf.setFont(FONT_BOLD if bold else font, size)

            self.pdf.drawString(x + indent, y, line)
            y -= self.config.line_height

        return y

    def add_metadata(self):
        self.pdf.setFont(FONT_BOLD, FONT_HEADER)
        self.pdf.drawString(self.left_x, self.y_metadata, self.resume.name)
        self.y_metadata -= SECTION_SPACING

        self.pdf.setFont(FONT_NORMAL, FONT_JOB_TITLE)
        self.y_metadata = self.draw_wrapped_text(self.resume.headline, self.left_x, self.y_metadata, COLUMN_WIDTH_LEFT, bold=True)

        self.pdf.setFont(FONT_NORMAL, FONT_BODY)
        self.y_metadata = self.draw_wrapped_text(
            f"{self.resume.location} | {self.resume.phone} | {self.resume.email}",
            self.left_x, self.y_metadata, COLUMN_WIDTH_LEFT
        )

        self.pdf.setFont(FONT_ITALIC, FONT_BODY)
        for key, value in self.resume.links.items():
            self.y_metadata = self.draw_wrapped_text(f"{key.capitalize()}: {value}", self.left_x, self.y_metadata, COLUMN_WIDTH_LEFT)

    def add_section(self, title, x, y, font=FONT_SECTION_TITLE):
        self.pdf.setFont(FONT_BOLD, font)
        y -= SECTION_SPACING
        self.pdf.drawString(x, y, title)
        y -= self.config.line_height
        return y

    def add_summary(self):
        self.y_summary = self.add_section("Summary", self.left_x, self.y_summary)

        for line in self.resume.summary:
            self.y_summary = self.draw_wrapped_text(f"• {line}", self.left_x, self.y_summary, PAGE_WIDTH - 2 * MARGIN_LEFT)

        # Ensure Education & Skills start at the same level as Experience
        self.y_left = self.y_summary - COLUMN_GAP
        self.y_right = self.y_summary - COLUMN_GAP

    def add_experience(self):
        """Adds Experience section on the left column (handles splitting)."""
        self.y_left = self.add_section("Experience", self.left_x, self.y_left)

        for job in self.resume.experience:
            self.y_left -= SECTION_SPACING
            self.y_left = self.draw_wrapped_text(f"{job.company_name} - {job.title} ({job.date})",
                                                 self.left_x, self.y_left, COLUMN_WIDTH_LEFT, bold=True)

            for desc in job.description:
                if isinstance(desc, Contribution):
                    if desc.title:
                        self.y_left = self.draw_wrapped_text(f"{desc.title}:", self.left_x, self.y_left,
                                                             COLUMN_WIDTH_LEFT, bold=True, indent=INDENT_SMALL)
                    for point in desc.points:
                        self.y_left = self.draw_wrapped_text(f"• {point}", self.left_x, self.y_left,
                                                             COLUMN_WIDTH_LEFT, indent=INDENT_LARGE)
                else:
                    self.y_left = self.draw_wrapped_text(f"• {desc}", self.left_x, self.y_left, COLUMN_WIDTH_LEFT)

            if job.contribution:
                self.y_left -= self.config.line_height
                self.y_left = self.draw_wrapped_text("Key Contributions:", self.left_x, self.y_left,
                                                     COLUMN_WIDTH_LEFT, bold=True)

                for contrib in job.contribution:
                    if isinstance(contrib, Contribution):  # Ensure it's a valid contribution object
                        if contrib.title:
                            self.y_left = self.draw_wrapped_text(f"{contrib.title}:", self.left_x, self.y_left,
                                                                 COLUMN_WIDTH_LEFT, bold=True, indent=INDENT_SMALL)
                        for point in contrib.points:
                            self.y_left = self.draw_wrapped_text(f"• {point}", self.left_x, self.y_left,
                                                                 COLUMN_WIDTH_LEFT, indent=INDENT_LARGE)
                    else:
                        self.y_left = self.draw_wrapped_text(f"• {contrib}", self.left_x, self.y_left,
                                                             COLUMN_WIDTH_LEFT, indent=INDENT_SMALL)

            if self.y_left < MARGIN_BOTTOM:
                self.pdf.showPage()
                self.y_left = PAGE_HEIGHT - MARGIN_TOP

    def add_education(self):
        self.y_right = self.add_section("Education", self.right_x, self.y_right,font=FONT_JOB_TITLE)

        for edu in self.resume.education:
            self.y_right = self.draw_wrapped_text(f"{edu.institution}", self.right_x, self.y_right, COLUMN_WIDTH_RIGHT, bold=True, size=self.config.education_size)
            self.y_right = self.draw_wrapped_text(f"{edu.degree} ({edu.year})", self.right_x, self.y_right, COLUMN_WIDTH_RIGHT, indent=INDENT_SMALL,size=self.config.education_size)

        # Space between Education & Skills
        self.y_right -= COLUMN_GAP

    def add_skills(self):
        #self.y_right = self.add_section("Skills", self.right_x, self.y_right, FONT_BODY)

        if self.resume.skills.management_skills:
            self.y_right = self.draw_wrapped_text("Management Skills:", self.right_x, self.y_right, COLUMN_WIDTH_RIGHT, bold=True)
            self.y_right = self.draw_wrapped_text(", ".join(self.resume.skills.management_skills), self.right_x, self.y_right, COLUMN_WIDTH_RIGHT, size=self.config.line_height, indent=INDENT_SMALL)

        if self.resume.skills.technical_skills:
            self.y_right = self.draw_wrapped_text("Technical Skills:", self.right_x, self.y_right, COLUMN_WIDTH_RIGHT, bold=True)

            for category, items in self.resume.skills.technical_skills.items():
                self.y_right = self.draw_wrapped_text(f"{category}:", self.right_x, self.y_right, COLUMN_WIDTH_RIGHT, bold=True, indent=INDENT_SMALL,size=self.config.line_height)
                self.y_right = self.draw_wrapped_text(", ".join(items), self.right_x, self.y_right, COLUMN_WIDTH_RIGHT, indent=INDENT_LARGE,size=self.config.line_height)

    def generate_pdf(self):
        self.add_metadata()
        self.add_summary()
        self.add_education()
        self.add_skills()
        self.add_experience()

        self.pdf.save()
        print(f"Resume saved as {self.filename}")

