import html
import re
from pathlib import Path


def _register_fonts() -> tuple[str, str]:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    regular = Path(r"C:\Windows\Fonts\arial.ttf")
    bold = Path(r"C:\Windows\Fonts\arialbd.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("ResumeArial", str(regular)))
        pdfmetrics.registerFont(TTFont("ResumeArial-Bold", str(bold)))
        return "ResumeArial", "ResumeArial-Bold"
    return "Helvetica", "Helvetica-Bold"


def _paragraph_text(line: str) -> str:
    escaped = html.escape(line)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)


def export_resume_pdf(resume: str, output: Path) -> None:
    """Render the generated Markdown CV as a readable A4 PDF."""
    try:
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            PageBreak,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
        )
    except ImportError as exc:
        raise RuntimeError(
            'Falta la dependencia PDF. Instala el extra con: uv sync --extra pdf'
        ) from exc

    regular_font, bold_font = _register_fonts()
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "ResumeTitle",
        parent=styles["Title"],
        fontName=bold_font,
        fontSize=17,
        leading=21,
        alignment=TA_CENTER,
        spaceAfter=5 * mm,
    )
    heading = ParagraphStyle(
        "ResumeHeading",
        parent=styles["Heading2"],
        fontName=bold_font,
        fontSize=10.5,
        leading=13,
        textColor="#1f4e79",
        spaceBefore=4 * mm,
        spaceAfter=1.5 * mm,
    )
    body = ParagraphStyle(
        "ResumeBody",
        parent=styles["BodyText"],
        fontName=regular_font,
        fontSize=9,
        leading=12,
        spaceAfter=2 * mm,
    )
    bullet = ParagraphStyle(
        "ResumeBullet",
        parent=body,
        leftIndent=4 * mm,
        firstLineIndent=-3 * mm,
        bulletIndent=0,
    )
    document = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="CV adaptado",
    )
    story = []
    for line in resume.splitlines():
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 1.5 * mm))
        elif stripped.startswith("# "):
            story.append(Paragraph(_paragraph_text(stripped[2:]), title))
        elif stripped.startswith("## "):
            if stripped[3:].upper() == "PROYECTOS DESTACADOS":
                story.append(PageBreak())
            story.append(Paragraph(_paragraph_text(stripped[3:]), heading))
        elif stripped.startswith("- "):
            story.append(
                Paragraph(_paragraph_text(stripped[2:]), bullet, bulletText="•")
            )
        else:
            story.append(Paragraph(_paragraph_text(stripped), body))
    output.parent.mkdir(parents=True, exist_ok=True)
    document.build(story)
