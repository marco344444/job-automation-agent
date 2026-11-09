import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import CandidateProfile, Job


def load_jobs(path: Path) -> list[Job]:
    return _jobs_from_data(json.loads(path.read_text(encoding="utf-8")))


def load_jobs_url(url: str) -> list[Job]:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "job-agent/0.1"})
    try:
        with urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"No se pudo descargar la fuente de ofertas (HTTP {exc.code}).") from exc
    except URLError as exc:
        raise RuntimeError(f"No se pudo conectar con la fuente de ofertas: {exc.reason}.") from exc
    except json.JSONDecodeError as exc:
        raise ValueError("La URL de ofertas no devolvió JSON válido.") from exc
    return _jobs_from_data(data)


def _jobs_from_data(data: object) -> list[Job]:
    if not isinstance(data, list):
        raise TypeError("El archivo de ofertas debe contener una lista JSON.")
    jobs = []
    for item in data:
        if not isinstance(item, dict):
            raise TypeError("Cada oferta debe ser un objeto JSON.")
        values = dict(item)
        values["skills"] = tuple(values.pop("skills", []))
        jobs.append(Job(**values))
    return jobs


def load_profile(path: Path) -> CandidateProfile:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["skills"] = tuple(data.get("skills", []))
    data["target_roles"] = tuple(data.get("target_roles", []))
    data["preferred_locations"] = tuple(data.get("preferred_locations", []))
    return CandidateProfile(**data)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
