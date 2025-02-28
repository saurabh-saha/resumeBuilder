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
