import json
import argparse

from templates.base_template import BaseTemplate
from templates.simple_template import convert_txt_to_pdf
from resume import Resume
from templates.two_column_template import TwoColumnTemplate, LayoutConfig

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a resume PDF.")
    parser.add_argument("input_file", help="Path to the JSON input file")
    parser.add_argument("output_file", help="Path to the PDF output file")
    parser.add_argument("--layout", choices=["two_column","base"], default="single", help="Choose resume layout")
    args = parser.parse_args()
    with open(args.input_file, "r") as file:
        resume_data = json.load(file)

    resume_obj = Resume(resume_data)
    if args.layout == "two_column":
        config = LayoutConfig(education_size=10, line_height=11)
        pdf_generator = TwoColumnTemplate(resume_obj, args.output_file, config)
    elif args.layout == "base":
        config = LayoutConfig(font_body=10)
        pdf_generator = BaseTemplate(resume_obj, args.output_file, config)
    pdf_generator.generate_pdf()
    print(f"Resume saved as {args.output_file}")