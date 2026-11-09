import re

from .models import CandidateProfile, Job, MatchResult


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9+#.]+", " ", value.lower()).strip()


def rank_jobs(jobs: list[Job], profile: CandidateProfile) -> list[MatchResult]:
    """Rank jobs with transparent, deterministic criteria."""
    candidate_skills = {_normalize(skill) for skill in profile.skills}
    target_roles = {_normalize(role) for role in profile.target_roles}
    locations = {_normalize(location) for location in profile.preferred_locations}
    results: list[MatchResult] = []

    for job in jobs:
        job_skills = {_normalize(skill) for skill in job.skills}
        matched = tuple(sorted(candidate_skills & job_skills))
        missing = tuple(sorted(job_skills - candidate_skills))
        score = 0.0
        reasons: list[str] = []

        if _normalize(job.title) in target_roles or any(
            role in _normalize(job.title) for role in target_roles
        ):
            score += 30
            reasons.append("el título coincide con el rol objetivo")
        if job_skills:
            score += 50 * len(matched) / len(job_skills)
            if matched:
                reasons.append(f"{len(matched)} habilidad(es) coinciden")
        if locations and _normalize(job.location) in locations:
            score += 20
            reasons.append("la ubicación coincide")

        results.append(
            MatchResult(
                job=job,
                score=round(min(score, 100), 2),
                matched_skills=matched,
                missing_skills=missing,
                reasons=tuple(reasons),
            )
        )

    return sorted(results, key=lambda result: (-result.score, result.job.company, result.job.title))
