import argparse
from pathlib import Path

from .io import load_jobs, load_jobs_url, load_profile, write_json
from .matching import rank_jobs
from .pdf import export_resume_pdf
from .tailoring import create_draft, create_llm_draft


def _sample_data(args: argparse.Namespace) -> None:
    jobs = [
        {
            "id": "acme-data-engineer",
            "title": "Data Engineer",
            "company": "Acme Analytics",
            "location": "Remote",
            "url": "https://example.com/jobs/acme-data-engineer",
            "description": "Build reliable data products and pipelines.",
            "skills": ["Python", "SQL", "Airflow", "Docker"],
        },
        {
            "id": "northstar-python-developer",
            "title": "Python Developer",
            "company": "Northstar Labs",
            "location": "Hybrid",
            "url": "https://example.com/jobs/northstar-python-developer",
            "description": "Develop APIs and internal automation.",
            "skills": ["Python", "FastAPI", "PostgreSQL"],
        },
    ]
    write_json(args.output, jobs)
    print(f"Datos de ejemplo escritos en {args.output}")


def _rank(args: argparse.Namespace) -> None:
    results = rank_jobs(_load_jobs(args), load_profile(args.profile))
    for result in results:
        print(f"{result.score:>5.1f} | {result.job.title} | {result.job.company} | {result.job.url}")
        print(f"      Coinciden: {', '.join(result.matched_skills) or 'ninguna'}")
        print(f"      Motivos: {', '.join(result.reasons) or 'sin coincidencias'}")


def _tailor(args: argparse.Namespace) -> None:
    jobs = {job.id: job for job in _load_jobs(args)}
    if args.job_id not in jobs:
        raise ValueError(f"No existe la oferta '{args.job_id}'.")
    job = jobs[args.job_id]
    profile = load_profile(args.profile)
    resume = args.resume.read_text(encoding="utf-8")
    draft = create_llm_draft(job, profile, resume) if args.llm else create_draft(job, profile, resume)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / f"{args.job_id}-resume.md").write_text(draft.tailored_resume, encoding="utf-8")
    (args.output / f"{args.job_id}-cover-letter.md").write_text(draft.cover_letter, encoding="utf-8")
    if args.pdf:
        export_resume_pdf(draft.tailored_resume, args.output / f"{args.job_id}-resume.pdf")
    print(f"Borrador creado en {args.output}. Revísalo antes de enviar.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Asistente local de búsqueda de empleo.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sample = subparsers.add_parser("sample-data", help="crear ofertas de ejemplo")
    sample.add_argument("--output", type=Path, default=Path("data/jobs.json"))
    sample.set_defaults(function=_sample_data)

    rank = subparsers.add_parser("rank", help="puntuar ofertas contra un perfil")
    _add_jobs_source_arguments(rank)
    rank.add_argument("--profile", type=Path, required=True)
    rank.set_defaults(function=_rank)

    tailor = subparsers.add_parser("tailor", help="crear un paquete de postulación")
    tailor.add_argument("--job-id", required=True)
    _add_jobs_source_arguments(tailor)
    tailor.add_argument("--profile", type=Path, required=True)
    tailor.add_argument("--resume", type=Path, required=True)
    tailor.add_argument("--output", type=Path, default=Path("output"))
    tailor.add_argument("--llm", action="store_true", help="usar el modelo local configurado")
    tailor.add_argument("--pdf", action="store_true", help="generar también el CV en PDF")
    tailor.set_defaults(function=_tailor)

    args = parser.parse_args()
    args.function(args)


def _add_jobs_source_arguments(parser: argparse.ArgumentParser) -> None:
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--jobs", type=Path, help="archivo JSON local de ofertas")
    source.add_argument("--jobs-url", help="URL pública que devuelva una lista JSON")


def _load_jobs(args: argparse.Namespace):
    if args.jobs is not None:
        return load_jobs(args.jobs)
    return load_jobs_url(args.jobs_url)
