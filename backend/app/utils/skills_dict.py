"""
utils/skills_dict.py
---------------------
Static skills taxonomy used for keyword-matching against resume text.

Organised by category so the analysis response can group skills
(e.g. "Programming Languages", "Cloud & DevOps") without any ML.

Design principles:
- All entries are lowercase; matching normalises to lowercase too.
- Multi-word skills (e.g. "machine learning") are matched before
  single-word ones so "machine" isn't double-counted.
- Easy to extend: just add strings to the relevant list.
"""

from typing import Dict, List

# ---------------------------------------------------------------------------
# Master taxonomy
# ---------------------------------------------------------------------------
SKILLS_TAXONOMY: Dict[str, List[str]] = {
    "Programming Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "c",
        "go", "golang", "rust", "ruby", "php", "swift", "kotlin", "scala",
        "r", "matlab", "perl", "bash", "shell", "powershell",
        "objective-c", "dart", "lua", "haskell", "elixir",
    ],
    "Web & Frontend": [
        "react", "vue", "angular", "next.js", "nuxt", "svelte",
        "html", "css", "sass", "less", "tailwind", "bootstrap",
        "jquery", "webpack", "vite", "redux", "graphql", "rest api",
        "restful", "websocket", "responsive design",
    ],
    "Backend & APIs": [
        "fastapi", "django", "flask", "express", "spring boot", "spring",
        "node.js", "nodejs", "rails", "laravel", "asp.net", ".net",
        "microservices", "grpc", "soap", "oauth", "jwt",
    ],
    "Databases": [
        "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis",
        "elasticsearch", "cassandra", "dynamodb", "oracle", "sql server",
        "mssql", "mariadb", "neo4j", "firebase", "supabase",
        "sql", "nosql", "orm", "sqlalchemy",
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "terraform", "ansible", "jenkins", "github actions", "gitlab ci",
        "ci/cd", "linux", "nginx", "apache", "serverless", "lambda",
        "s3", "ec2", "rds", "cloudformation", "helm", "prometheus",
        "grafana", "datadog", "splunk",
    ],
    "Data & ML": [
        "machine learning", "deep learning", "nlp", "natural language processing",
        "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn",
        "pandas", "numpy", "matplotlib", "seaborn", "jupyter",
        "data analysis", "data science", "data engineering",
        "etl", "apache spark", "hadoop", "airflow", "dbt",
        "power bi", "tableau", "looker", "excel",
    ],
    "Testing & QA": [
        "unit testing", "integration testing", "pytest", "jest", "mocha",
        "selenium", "cypress", "playwright", "tdd", "bdd",
        "test automation", "load testing", "qa",
    ],
    "Tools & Practices": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence",
        "agile", "scrum", "kanban", "code review", "pair programming",
        "solid principles", "design patterns", "system design",
        "microservices", "event-driven", "api design",
    ],
    "Soft Skills": [
        "leadership", "communication", "teamwork", "problem solving",
        "critical thinking", "time management", "mentoring", "coaching",
        "project management", "stakeholder management", "presentation",
        "collaboration", "adaptability",
    ],
}

# Flat sorted list: longest phrases first so multi-word terms are matched
# before their constituent words.
ALL_SKILLS: List[str] = sorted(
    (skill for skills in SKILLS_TAXONOMY.values() for skill in skills),
    key=len,
    reverse=True,
)
