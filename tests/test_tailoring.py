from job_agent.models import CandidateProfile, Job
from job_agent.tailoring import create_draft


def test_tailoring_does_not_add_unverified_job_skills() -> None:
    profile = CandidateProfile(name="Ana", target_roles=("Developer",), skills=("Python",))
    job = Job(
        id="one",
        title="Developer",
        company="Example",
        location="Remote",
        url="https://example.com",
        description="",
        skills=("Python", "Kubernetes"),
    )

    draft = create_draft(job, profile, "# CV")

    assert "Python" in draft.cover_letter
    assert "Kubernetes" not in draft.cover_letter
    assert "conserva únicamente afirmaciones" in draft.tailored_resume
