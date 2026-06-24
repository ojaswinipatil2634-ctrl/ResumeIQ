"""
services/roadmap_service.py
----------------------------
Career roadmap generator.

Based on the skills and experience detected in the resume, this service
generates a personalised learning roadmap including:
- Recommended next technologies
- Certifications to pursue
- Online courses
- Next job titles to target
- A sequential learning plan

All logic is rule-based — no external APIs.

Public API
----------
generate_roadmap(text: str) -> RoadmapResult
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from app.utils.skills_dict import ALL_SKILLS, SKILLS_TAXONOMY
from app.utils.resume_parser import parse_sections


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class RoadmapStep:
    order: int
    title: str
    description: str
    estimated_time: str


@dataclass
class RoadmapResult:
    current_level: str
    target_role: str
    recommended_technologies: List[str]
    certifications: List[str]
    courses: List[str]
    next_roles: List[str]
    learning_roadmap: List[RoadmapStep]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_skills(text: str) -> Set[str]:
    normalised = text.lower()
    found: Set[str] = set()
    for skill in ALL_SKILLS:
        escaped = re.escape(skill)
        if re.search(rf"(?<!\w){escaped}(?!\w)", normalised):
            found.add(skill)
    return found


_YEAR_RANGE_RE = re.compile(
    r"\b(19|20)\d{2}\b\s*[-–—to]+\s*(\b(19|20)\d{2}\b|present|current|now)",
    re.IGNORECASE,
)


def _estimate_years(text: str) -> int:
    """Return best-effort total years of experience (0 if not found)."""
    total = 0
    current_year = 2025
    for m in _YEAR_RANGE_RE.finditer(text):
        start_m = re.search(r"\b(19|20)\d{2}\b", m.group())
        end_m   = re.search(r"present|current|now|\b(19|20)\d{2}\b", m.group()[4:], re.IGNORECASE)
        if not start_m:
            continue
        start = int(start_m.group())
        end_raw = end_m.group() if end_m else None
        if end_raw and re.match(r"present|current|now", end_raw, re.IGNORECASE):
            end = current_year
        elif end_raw:
            end = int(end_raw)
        else:
            continue
        if end >= start:
            total += end - start
    return total


def _infer_level(years: int, skills: Set[str]) -> str:
    """Infer seniority level from experience and skill breadth."""
    skill_count = len(skills)
    if years >= 7 or (years >= 5 and skill_count >= 20):
        return "Senior"
    if years >= 3 or (years >= 1 and skill_count >= 12):
        return "Mid-Level"
    return "Junior"


# ---------------------------------------------------------------------------
# Domain-specific roadmap data
# ---------------------------------------------------------------------------

# Tech tracks — keyed by dominant skill category
_TRACK_DATA: Dict[str, Dict] = {
    "data": {
        "target_role": "Senior Data Engineer / ML Engineer",
        "next_roles": [
            "Data Engineer", "ML Engineer", "Data Scientist",
            "AI/ML Lead", "Head of Data",
        ],
        "recommended_technologies": [
            "Apache Spark", "dbt", "Airflow", "MLflow", "Ray",
            "Snowflake", "BigQuery", "Kafka", "Flink",
        ],
        "certifications": [
            "AWS Certified Machine Learning – Specialty",
            "Google Professional Data Engineer",
            "Databricks Certified Associate Developer for Apache Spark",
            "Microsoft Certified: Azure Data Scientist Associate",
            "Coursera Deep Learning Specialization (Andrew Ng)",
        ],
        "courses": [
            "fast.ai – Practical Deep Learning for Coders (free)",
            "Coursera Machine Learning Specialization (Andrew Ng)",
            "DataCamp Data Engineering track",
            "Udemy – The Complete SQL Bootcamp",
            "Google's Machine Learning Crash Course (free)",
        ],
        "roadmap_steps": [
            RoadmapStep(1, "Master SQL & Data Modelling",
                "Strengthen SQL with window functions, CTEs, and optimisation. "
                "Learn star schema and data warehouse patterns.",
                "3–4 weeks"),
            RoadmapStep(2, "Learn Apache Spark",
                "Build ETL pipelines with PySpark. Understand partitioning, "
                "lazy evaluation, and optimisation.",
                "4–6 weeks"),
            RoadmapStep(3, "Workflow Orchestration with Airflow",
                "Schedule and monitor data pipelines using Apache Airflow DAGs.",
                "2–3 weeks"),
            RoadmapStep(4, "ML Fundamentals",
                "Cover supervised learning, model evaluation, and cross-validation "
                "with scikit-learn.",
                "4–6 weeks"),
            RoadmapStep(5, "Deep Learning & Neural Networks",
                "Build and train neural networks with PyTorch or TensorFlow. "
                "Work through a real project.",
                "6–8 weeks"),
            RoadmapStep(6, "Cloud Data Platform",
                "Deploy pipelines on AWS (S3, Glue, Redshift) or GCP (BigQuery, Dataflow).",
                "3–4 weeks"),
            RoadmapStep(7, "MLOps Fundamentals",
                "Learn model serving, monitoring, and versioning with MLflow or BentoML.",
                "2–3 weeks"),
        ],
    },
    "fullstack": {
        "target_role": "Senior Full-Stack Engineer",
        "next_roles": [
            "Full-Stack Engineer", "Software Engineer II", "Tech Lead",
            "Engineering Manager", "Principal Engineer",
        ],
        "recommended_technologies": [
            "Next.js", "TypeScript", "GraphQL", "PostgreSQL",
            "Redis", "Docker", "Kubernetes", "AWS",
        ],
        "certifications": [
            "AWS Certified Developer – Associate",
            "Meta Front-End Developer Certificate (Coursera)",
            "Google Professional Cloud Developer",
        ],
        "courses": [
            "The Odin Project – Full-Stack JavaScript (free)",
            "Fullstackopen.com – University of Helsinki (free)",
            "Scrimba Frontend Developer Career Path",
            "Udemy – React & Node.js by Maximilian Schwarzmüller",
            "Frontend Masters – Complete Intro to Databases",
        ],
        "roadmap_steps": [
            RoadmapStep(1, "TypeScript Mastery",
                "Convert a JavaScript project to TypeScript. Learn generics, "
                "utility types, and strict mode.",
                "2–3 weeks"),
            RoadmapStep(2, "Advanced React Patterns",
                "Study Server Components, hooks patterns, Suspense, and performance "
                "optimisation techniques.",
                "3–4 weeks"),
            RoadmapStep(3, "Backend API Design",
                "Build a production-grade REST or GraphQL API. Focus on auth, "
                "pagination, and error handling.",
                "3–4 weeks"),
            RoadmapStep(4, "Database Design & Optimisation",
                "Learn PostgreSQL indexing, query planning, transactions, and ORMs.",
                "2–3 weeks"),
            RoadmapStep(5, "Docker & Containerisation",
                "Dockerise a full-stack app. Learn Docker Compose for local dev.",
                "1–2 weeks"),
            RoadmapStep(6, "Cloud Deployment",
                "Deploy to AWS or GCP. Set up load balancing, auto-scaling, and RDS.",
                "3–4 weeks"),
            RoadmapStep(7, "System Design",
                "Study distributed systems concepts: caching, queues, databases at scale. "
                "Practice design interview problems.",
                "4–6 weeks"),
        ],
    },
    "backend": {
        "target_role": "Senior Backend Engineer",
        "next_roles": [
            "Backend Engineer", "Software Engineer II", "API Engineer",
            "Platform Engineer", "Tech Lead",
        ],
        "recommended_technologies": [
            "Kafka", "gRPC", "Redis", "Elasticsearch",
            "Kubernetes", "Terraform", "PostgreSQL", "Prometheus",
        ],
        "certifications": [
            "AWS Certified Developer – Associate",
            "Google Professional Cloud Architect",
            "Certified Kubernetes Application Developer (CKAD)",
        ],
        "courses": [
            "Designing Data-Intensive Applications (book by Martin Kleppmann)",
            "Hussein Nasser – Fundamentals of Backend Engineering (Udemy)",
            "MIT OpenCourseWare – Distributed Systems (free)",
            "Coursera – Cloud Computing Specialization",
            "Pluralsight – Microservices Architecture",
        ],
        "roadmap_steps": [
            RoadmapStep(1, "Deep Dive into Databases",
                "Master SQL query optimisation, indexing, ACID transactions, "
                "and connection pooling.",
                "3–4 weeks"),
            RoadmapStep(2, "Distributed Systems Basics",
                "Study CAP theorem, consistency models, and distributed consensus. "
                "Read DDIA chapters 1–6.",
                "4–5 weeks"),
            RoadmapStep(3, "Messaging & Event Streaming",
                "Build an event-driven service with Kafka or RabbitMQ. "
                "Understand consumer groups, offsets, and at-least-once delivery.",
                "3–4 weeks"),
            RoadmapStep(4, "Containerisation & Orchestration",
                "Dockerise your services and deploy with Kubernetes. "
                "Learn Helm charts and rolling deployments.",
                "3–4 weeks"),
            RoadmapStep(5, "Observability",
                "Add Prometheus metrics, Grafana dashboards, and structured logging "
                "to a production service.",
                "2–3 weeks"),
            RoadmapStep(6, "Infrastructure as Code",
                "Provision cloud resources with Terraform. Practice the "
                "plan/apply/destroy workflow.",
                "2–3 weeks"),
            RoadmapStep(7, "System Design Practice",
                "Solve 10+ system design problems (URL shortener, rate limiter, "
                "news feed) and review solutions.",
                "4–6 weeks"),
        ],
    },
    "devops": {
        "target_role": "Senior DevOps / Platform Engineer",
        "next_roles": [
            "DevOps Engineer", "Site Reliability Engineer (SRE)",
            "Platform Engineer", "Cloud Architect", "Infrastructure Lead",
        ],
        "recommended_technologies": [
            "Terraform", "ArgoCD", "Helm", "Prometheus", "Grafana",
            "Vault", "Ansible", "Pulumi",
        ],
        "certifications": [
            "AWS Certified DevOps Engineer – Professional",
            "Certified Kubernetes Administrator (CKA)",
            "Certified Kubernetes Application Developer (CKAD)",
            "HashiCorp Certified: Terraform Associate",
            "Google Professional Cloud DevOps Engineer",
        ],
        "courses": [
            "KodeKloud – CKA Certified Kubernetes Administrator",
            "Linux Foundation – LFS258 Kubernetes Fundamentals",
            "Udemy – HashiCorp Certified Terraform Associate",
            "A Cloud Guru – AWS DevOps Pro Certification",
            "The DevOps Handbook (book)",
        ],
        "roadmap_steps": [
            RoadmapStep(1, "Kubernetes Fundamentals",
                "Deploy multi-tier applications on Kubernetes. Learn Pods, "
                "Deployments, Services, and ConfigMaps.",
                "4–5 weeks"),
            RoadmapStep(2, "CI/CD Pipelines",
                "Build end-to-end CI/CD with GitHub Actions or GitLab CI. "
                "Include test, build, scan, and deploy stages.",
                "2–3 weeks"),
            RoadmapStep(3, "Infrastructure as Code with Terraform",
                "Provision multi-region infrastructure with Terraform modules, "
                "state backends, and workspaces.",
                "3–4 weeks"),
            RoadmapStep(4, "Observability Stack",
                "Set up Prometheus + Grafana + Loki for metrics, dashboards, "
                "and log aggregation.",
                "2–3 weeks"),
            RoadmapStep(5, "Security & Secret Management",
                "Integrate HashiCorp Vault for secrets. Scan containers with "
                "Trivy. Harden cluster RBAC.",
                "2–3 weeks"),
            RoadmapStep(6, "SRE Principles",
                "Define SLOs, error budgets, and on-call runbooks. "
                "Study the Google SRE book.",
                "3–4 weeks"),
        ],
    },
    "frontend": {
        "target_role": "Senior Frontend Engineer",
        "next_roles": [
            "Frontend Engineer", "UI Engineer", "React Engineer",
            "Full-Stack Engineer", "Frontend Tech Lead",
        ],
        "recommended_technologies": [
            "TypeScript", "Next.js", "Tailwind CSS", "Storybook",
            "Vitest", "Playwright", "GraphQL", "React Query",
        ],
        "certifications": [
            "Meta Front-End Developer Certificate (Coursera)",
            "W3Schools Front End Development Certificate",
            "Google UX Design Certificate",
        ],
        "courses": [
            "Scrimba Frontend Developer Career Path",
            "Kent C. Dodds – EpicReact.dev",
            "Theo's T3 Stack course (free, YouTube)",
            "CSS for JavaScript Developers (Josh Comeau)",
            "Testing JavaScript (Kent C. Dodds)",
        ],
        "roadmap_steps": [
            RoadmapStep(1, "TypeScript Essentials",
                "Add TypeScript to an existing React project. Learn interfaces, "
                "generics, and common utility types.",
                "2–3 weeks"),
            RoadmapStep(2, "Advanced React",
                "Master hooks (useReducer, useContext, custom hooks), "
                "React Query, and concurrent features.",
                "3–4 weeks"),
            RoadmapStep(3, "Testing Frontend Code",
                "Write unit tests with Vitest + Testing Library. "
                "Add end-to-end tests with Playwright.",
                "2–3 weeks"),
            RoadmapStep(4, "Performance Optimisation",
                "Audit and fix Core Web Vitals: LCP, CLS, FID. "
                "Implement code splitting and lazy loading.",
                "2–3 weeks"),
            RoadmapStep(5, "Component Design Systems",
                "Build a Storybook component library. Document props and variants. "
                "Publish to npm.",
                "3–4 weeks"),
            RoadmapStep(6, "Micro-Frontend Architecture",
                "Study Module Federation. Split a monolith into independently "
                "deployable frontend modules.",
                "3–4 weeks"),
        ],
    },
}

_DEFAULT_TRACK = "fullstack"


# ---------------------------------------------------------------------------
# Track inference
# ---------------------------------------------------------------------------

def _infer_track(skills: Set[str], categories: Dict[str, List[str]]) -> str:
    """Determine the most relevant career track from skill categories."""
    score: Dict[str, int] = {
        "data":       len(categories.get("Data & ML", [])) * 3,
        "devops":     len(categories.get("Cloud & DevOps", [])) * 3,
        "backend":    len(categories.get("Backend & APIs", [])) * 2,
        "frontend":   len(categories.get("Web & Frontend", [])) * 2,
        "fullstack":  (
            len(categories.get("Backend & APIs", [])) +
            len(categories.get("Web & Frontend", []))
        ),
    }
    # Boost data track if ML skills present
    if any(s in skills for s in ["machine learning", "tensorflow", "pytorch", "pandas"]):
        score["data"] += 5
    # Boost devops if infra keywords present
    if any(s in skills for s in ["kubernetes", "terraform", "ansible", "helm"]):
        score["devops"] += 5

    return max(score, key=lambda k: score[k]) if any(score.values()) else _DEFAULT_TRACK


def _categorize_skills(skills: Set[str]) -> Dict[str, List[str]]:
    result: Dict[str, List[str]] = {}
    for category, cat_skills in SKILLS_TAXONOMY.items():
        matched = [s for s in cat_skills if s in skills]
        if matched:
            result[category] = sorted(matched)
    return result


# ---------------------------------------------------------------------------
# Personalise roadmap steps based on level
# ---------------------------------------------------------------------------

def _adapt_steps_for_level(
    steps: List[RoadmapStep], level: str
) -> List[RoadmapStep]:
    """
    Junior users get full roadmap.
    Mid-level skip the first 2 foundational steps.
    Senior get only the advanced steps.
    """
    if level == "Junior":
        return steps
    if level == "Mid-Level":
        # Skip step 1, renumber
        advanced = steps[1:]
        return [
            RoadmapStep(i + 1, s.title, s.description, s.estimated_time)
            for i, s in enumerate(advanced)
        ]
    # Senior — last 3 steps
    advanced = steps[-3:]
    return [
        RoadmapStep(i + 1, s.title, s.description, s.estimated_time)
        for i, s in enumerate(advanced)
    ]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_roadmap(text: str) -> RoadmapResult:
    """
    Generate a personalised career roadmap from extracted resume text.

    Steps:
    1. Extract skills.
    2. Infer career track from skill distribution.
    3. Estimate seniority level from years + skill count.
    4. Look up track-specific roadmap data.
    5. Adapt roadmap depth to current level.
    """
    skills     = _extract_skills(text)
    categories = _categorize_skills(skills)
    years      = _estimate_years(text)
    level      = _infer_level(years, skills)
    track      = _infer_track(skills, categories)

    data = _TRACK_DATA.get(track, _TRACK_DATA[_DEFAULT_TRACK])

    # Filter out technologies the candidate already has
    new_techs = [
        t for t in data["recommended_technologies"]
        if t.lower() not in {s.lower() for s in skills}
    ]

    steps = _adapt_steps_for_level(data["roadmap_steps"], level)

    return RoadmapResult(
        current_level=level,
        target_role=data["target_role"],
        recommended_technologies=new_techs[:8],
        certifications=data["certifications"],
        courses=data["courses"],
        next_roles=data["next_roles"],
        learning_roadmap=steps,
    )
