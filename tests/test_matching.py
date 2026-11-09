from job_agent.matching import rank_jobs
from job_agent.models import CandidateProfile, Job


def test_rank_explains_skill_and_location_matches() -> None:
    profile = CandidateProfile(
        name="Test",
        target_roles=("Data Engineer",),
        skills=("Python", "SQL"),
        preferred_locations=("Remote",),
    )
    job = Job(
        id="one",
        title="Data Engineer",
        company="Example",
        location="Remote",
        url="https://example.com",
        description="",
        skills=("Python", "SQL", "Airflow"),
    )

    result = rank_jobs([job], profile)[0]

    assert result.score == 83.33
    assert result.matched_skills == ("python", "sql")
    assert "la ubicación coincide" in result.reasons
