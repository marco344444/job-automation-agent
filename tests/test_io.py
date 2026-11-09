import io
import json

from job_agent.io import load_jobs, load_jobs_url


def test_load_jobs_does_not_mutate_source(tmp_path) -> None:
    payload = [{"id": "one", "title": "Developer", "company": "Example", "location": "Remote",
                "url": "https://example.com", "description": "Python", "skills": ["Python"]}]
    path = tmp_path / "jobs.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    jobs = load_jobs(path)

    assert jobs[0].skills == ("Python",)
    assert payload[0]["skills"] == ["Python"]


def test_load_jobs_url_reads_json(monkeypatch) -> None:
    payload = b'[{"id":"one","title":"Developer","company":"Example","location":"Remote","url":"https://example.com","description":"Python","skills":["Python"]}]'

    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

    monkeypatch.setattr("job_agent.io.urlopen", lambda request, timeout: Response(payload))

    assert load_jobs_url("https://example.com/jobs.json")[0].id == "one"
