# Job Automation Agent

Agente local para organizar una búsqueda de empleo de forma reproducible y segura:

1. Importa ofertas desde un JSON o desde proveedores configurables.
2. Normaliza y puntúa las ofertas contra un perfil.
3. Genera una versión adaptada del CV y una carta de presentación.
4. Exporta un paquete de postulación para revisión humana.

El proyecto **no envía postulaciones automáticamente**. El último paso siempre queda bajo control de la persona usuaria.

## Por qué es un buen proyecto de portafolio

- Python moderno con tipado, `dataclasses` y separación por capas.
- Diseño preparado para conectar un agente local (Ollama/Qwen) sin hacer obligatoria una dependencia externa.
- Scoring explicable: cada coincidencia muestra por qué una oferta fue priorizada.
- Datos y salidas locales; no se suben CV, credenciales ni datos personales al repositorio.
- Tests unitarios para el matching y la generación de documentos.

## Requisitos

- Python 3.11+
- Opcional: un servidor compatible con OpenAI para generación local (por ejemplo Ollama).

## Inicio rápido

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

job-agent sample-data --output data/jobs.json
job-agent rank --jobs data/jobs.json --profile examples/profile.json
job-agent tailor --job-id acme-data-engineer --jobs data/jobs.json --profile examples/profile.json --resume examples/resume.md --output output
```

Los archivos generados aparecen en `output/` y están excluidos de Git.

## Usar un modelo local

El modo determinista funciona sin modelo. Para usar Qwen u otro modelo local, inicia un endpoint compatible con OpenAI y configura:

```powershell
$env:JOB_AGENT_LLM_BASE_URL = "http://localhost:11434/v1"
$env:JOB_AGENT_LLM_MODEL = "qwen3:8b"
$env:JOB_AGENT_LLM_API_KEY = "local"
pip install -e ".[llm]"
uv sync --extra llm --extra pdf
job-agent tailor --job-id acme-data-engineer --jobs data/jobs.json --profile examples/profile.json --resume examples/resume.md --output output --llm --pdf
```

El agente local recibe únicamente la oferta y el contenido del CV indicado en el comando. Revisa siempre el resultado antes de usarlo.
Si Ollama no está instalado, descárgalo desde https://ollama.com/download, ejecuta
`ollama pull qwen3:8b` y deja `ollama serve` ejecutándose antes de usar el comando.

El proyecto incluye un CV y perfil ficticios en `examples/resume.md` y `examples/profile.json`.
El PDF generado conserva formato A4 y el PDF original usado como fuente nunca se modifica.

## Probar con una oferta hipotética o una URL JSON

Puedes probar el ranking con la oferta incluida en el repositorio:

```powershell
job-agent rank --jobs examples/hypothetical-jobs.json --profile examples/profile.json
```

También puedes usar una fuente autorizada que devuelva una lista JSON con el mismo formato:

```powershell
job-agent rank --jobs-url "https://tu-fuente-autorizada.example/jobs.json" --profile examples/profile.json
job-agent tailor --job-id cloud-platform-intern --jobs-url "https://tu-fuente-autorizada.example/jobs.json" --profile examples/profile.json --resume examples/resume.md --output output/cloud-platform --llm --pdf
```

El importador no inicia sesión, no evade CAPTCHA ni controles de acceso, y no envía postulaciones.
Para LinkedIn, Indeed o Wellfound usa únicamente APIs, RSS, exportaciones o feeds cuyo uso esté
permitido por el portal.

## Importar ofertas reales

El MVP acepta el siguiente formato JSON:

```json
[
  {
    "id": "company-role",
    "title": "Data Engineer",
    "company": "Example",
    "location": "Remote",
    "url": "https://example.com/jobs/1",
    "description": "Python, SQL and cloud data pipelines",
    "skills": ["python", "sql", "airflow"]
  }
]
```

Los adaptadores para fuentes reales deben respetar las condiciones de uso y robots.txt de cada sitio. No se incluyen scrapers que evadan controles de acceso.

## Publicar en GitHub

```powershell
git init
git add .
git commit -m "Initial job automation agent"
git branch -M main
git remote add origin https://github.com/<usuario>/job-automation-agent.git
git push -u origin main
```

Antes de publicar, reemplaza los datos de ejemplo por datos ficticios y confirma que nunca se hayan añadido credenciales o tu CV real.
