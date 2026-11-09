import json
import os

from .models import ApplicationDraft, CandidateProfile, Job


def _keyword_lines(job: Job, profile: CandidateProfile) -> tuple[str, ...]:
    profile_skills = {skill.lower(): skill for skill in profile.skills}
    return tuple(skill for skill in job.skills if skill.lower() in profile_skills)


def create_draft(job: Job, profile: CandidateProfile, resume: str) -> ApplicationDraft:
    """Create a reviewable draft without inventing candidate experience."""
    keywords = _keyword_lines(job, profile)
    keyword_text = ", ".join(keywords) if keywords else "las habilidades descritas en mi CV"
    resume_addendum = (
        f"\n\n## Enfoque para {job.title} en {job.company}\n"
        f"Palabras clave relevantes: {keyword_text}.\n"
        "Este bloque es una guía de edición: conserva únicamente afirmaciones "
        "que puedas demostrar."
    )
    cover_letter = (
        f"Hola equipo de {job.company},\n\n"
        f"Me interesa la posición de {job.title}. Mi experiencia incluye {keyword_text}, "
        "y me gustaría aportar esas capacidades al equipo.\n\n"
        f"Analicé la descripción publicada ({job.url}) y preparé mi CV para destacar "
        "la experiencia más relevante. Quedo disponible para conversar sobre cómo "
        "puedo contribuir.\n\nSaludos,\n"
        f"{profile.name}"
    )
    return ApplicationDraft(
        job_id=job.id,
        tailored_resume=resume.rstrip() + resume_addendum,
        cover_letter=cover_letter,
        matched_keywords=keywords,
    )


def create_llm_draft(job: Job, profile: CandidateProfile, resume: str) -> ApplicationDraft:
    """Create a reviewable draft with an OpenAI-compatible local model."""
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            'Falta la dependencia opcional. Instala el extra con: pip install -e ".[llm]"'
        ) from exc

    client = OpenAI(
        base_url=os.getenv("JOB_AGENT_LLM_BASE_URL", "http://localhost:11434/v1"),
        api_key=os.getenv("JOB_AGENT_LLM_API_KEY", "local"),
    )
    model = os.getenv("JOB_AGENT_LLM_MODEL", "qwen3:8b")
    prompt = f"""    Genera un borrador breve de CV adaptado y una carta de presentación para esta oferta.
    No inventes experiencia, fechas, títulos, logros ni habilidades. Usa únicamente información del CV.
    Copia literalmente los nombres de certificaciones, instituciones, proyectos, tecnologías y fechas;
    no los traduzcas, generalices ni reemplaces. Para la oferta, solo identifica requisitos que ya aparecen en el CV. Conserva las secciones
    importantes, resume cada proyecto en una o dos frases y limita tailored_resume a 1200 palabras.
    Responde exclusivamente con un objeto JSON válido que contenga SIEMPRE estas tres claves:
    tailored_resume (string), cover_letter (string), matched_keywords (array de strings). No omitas
    ninguna clave aunque su contenido sea breve.
matched_keywords debe ser una lista de strings.

PERFIL:
{profile}

OFERTA:
{job}

CV:
{resume}
"""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Eres un asistente de postulación cuidadoso y veraz.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=3000,
        reasoning_effort="none",
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("El modelo local devolvió una respuesta vacía.")
    try:
        payload = json.loads(content)
        tailored_resume = payload["tailored_resume"]
        cover_letter = payload["cover_letter"]
        raw_keywords = payload["matched_keywords"]
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError("El modelo local no devolvió el JSON esperado.") from exc
    if not isinstance(raw_keywords, list):
        raise TypeError("El modelo local devolvió una lista de palabras clave inválida.")
    matched_keywords = tuple(raw_keywords)
    if not all(isinstance(value, str) for value in (tailored_resume, cover_letter)):
        raise RuntimeError("El modelo local devolvió texto inválido para el CV o la carta.")
    if not all(isinstance(value, str) for value in matched_keywords):
        raise RuntimeError("El modelo local devolvió palabras clave inválidas.")
    return ApplicationDraft(
        job_id=job.id,
        tailored_resume=tailored_resume,
        cover_letter=cover_letter,
        matched_keywords=matched_keywords,
    )
