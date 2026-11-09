from dataclasses import dataclass, field


@dataclass(frozen=True)
class Job:
    id: str
    title: str
    company: str
    location: str
    url: str
    description: str
    skills: tuple[str, ...] = ()


@dataclass(frozen=True)
class CandidateProfile:
    name: str
    target_roles: tuple[str, ...]
    skills: tuple[str, ...]
    years_experience: int = 0
    preferred_locations: tuple[str, ...] = ()


@dataclass(frozen=True)
class MatchResult:
    job: Job
    score: float
    matched_skills: tuple[str, ...] = ()
    missing_skills: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class ApplicationDraft:
    job_id: str
    tailored_resume: str
    cover_letter: str
    matched_keywords: tuple[str, ...] = field(default_factory=tuple)
