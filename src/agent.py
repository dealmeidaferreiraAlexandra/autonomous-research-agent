from __future__ import annotations

import json
import re
from typing import List, Optional, Tuple

from openai import OpenAI

from src.config import get_openai_api_key, get_openai_model, openai_enabled
from src.local_search import search_local_docs
from src.pdf_utils import extract_many_pdfs
from src.schemas import Reference, ResearchReport


def _openai_client() -> Optional[OpenAI]:
    key = get_openai_api_key()
    if not key:
        return None
    return OpenAI(api_key=key)


def _split_sentences(text: str) -> List[str]:
    clean = re.sub(r"\s+", " ", text).strip()
    if not clean:
        return []
    parts = re.split(r"(?<=[.!?])\s+", clean)
    return [p.strip() for p in parts if p.strip()]


def _bullet_lines(text: str) -> List[str]:
    out: List[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(("-", "•", "*", "1.", "2.", "3.", "4.", "5.")):
            cleaned = re.sub(r"^(\d+\.\s*|[-•*]\s*)", "", line).strip()
            if cleaned:
                out.append(cleaned)
    return out


def _simple_summary(text: str, max_sentences: int = 4) -> str:
    sentences = _split_sentences(text)
    if not sentences:
        return "No summary available."
    return " ".join(sentences[:max_sentences])


def _truncate(text: str, max_chars: int = 5000) -> str:
    text = text or ""
    return text[:max_chars]


def gather_local_evidence(topic: str, pdf_docs: List[dict]) -> Tuple[str, List[Reference]]:
    local_hits = search_local_docs(topic, top_k=5)
    lines: List[str] = []
    refs: List[Reference] = []

    lines.append(f"TOPIC: {topic}")
    lines.append("")
    lines.append("LOCAL KNOWLEDGE BASE:")

    if local_hits["hits"]:
        for hit in local_hits["hits"]:
            file_name = hit["path"].split("/")[-1]
            snippet = hit["snippet"]
            lines.append(f"- {file_name} (score={hit['score']}): {snippet}")
            refs.append(
                Reference(
                    title=file_name,
                    source_type="local",
                    url_or_path=hit["path"],
                    snippet=snippet,
                )
            )
    else:
        lines.append("- No local hits found.")

    if pdf_docs:
        lines.append("")
        lines.append("UPLOADED PDFS:")
        for doc in pdf_docs:
            snippet = (doc["text"] or "")[:500].replace("\n", " ")
            if snippet:
                lines.append(f"- {doc['name']}: {snippet}")
                refs.append(
                    Reference(
                        title=doc["name"],
                        source_type="pdf",
                        url_or_path=doc["name"],
                        snippet=snippet,
                    )
                )
            else:
                lines.append(f"- {doc['name']}: [no extractable text]")

    return "\n".join(lines), refs


def research_agent_openai(topic: str, local_evidence: str, pdf_docs: List[dict]) -> str:
    client = _openai_client()
    if client is None:
        raise RuntimeError("OpenAI key not available")

    pdf_context = "\n\n".join(
        [
            f"PDF FILE: {doc['name']}\n{_truncate(doc['text'], 4000)}"
            for doc in pdf_docs
            if doc.get("text")
        ]
    )

    prompt = f"""
You are the Research Agent.

Research topic:
{topic}

Use web search when needed.
Also use the local evidence below and the uploaded PDF context.

Return a compact evidence memo with:
- key facts
- current context
- caveats
- source names or URLs when available

LOCAL EVIDENCE:
{local_evidence}

PDF CONTEXT:
{pdf_context if pdf_context else "[none]"}
""".strip()

    response = client.responses.create(
        model=get_openai_model(),
        tools=[{"type": "web_search"}],
        input=prompt,
    )

    return response.output_text


def analysis_agent_openai(topic: str, evidence: str) -> str:
    client = _openai_client()
    if client is None:
        raise RuntimeError("OpenAI key not available")

    prompt = f"""
You are the Analysis Agent.

Topic:
{topic}

Evidence memo:
{evidence}

Turn this into a concise analytical brief with:
- 5 key insights
- 3 practical recommendations
- 1 short risk/caveat note
""".strip()

    response = client.responses.create(
        model=get_openai_model(),
        input=prompt,
    )

    return response.output_text


def writer_agent_openai(topic: str, analysis: str, reference_seeds: List[Reference]) -> ResearchReport:
    client = _openai_client()
    if client is None:
        raise RuntimeError("OpenAI key not available")

    schema = ResearchReport.model_json_schema()
    reference_json = json.dumps([ref.model_dump() for ref in reference_seeds], ensure_ascii=False, indent=2)

    prompt = f"""
You are the Writer Agent.

Create the final report as JSON only.
Topic: {topic}

Requirements:
- topic: the topic string
- mode: "openai"
- executive_summary: a concise paragraph
- key_insights: 5 bullets
- recommendations: 3 bullets
- references: use the reference seeds below and add any useful web references you have evidence for

Analysis:
{analysis}

Reference seeds:
{reference_json}
""".strip()

    response = client.responses.create(
        model=get_openai_model(),
        input=prompt,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "research_report",
                "schema": schema,
                "strict": True,
            },
        },
    )

    report = ResearchReport.model_validate_json(response.output_text)
    report.mode = "openai"

    if not report.references and reference_seeds:
        report.references = reference_seeds[:]

    return report


def _build_local_report(topic: str, local_evidence: str, reference_seeds: List[Reference], pdf_docs: List[dict]) -> ResearchReport:
    summary_source = local_evidence
    if pdf_docs:
        summary_source += "\n\n" + "\n\n".join(
            [f"{doc['name']}: {_truncate(doc.get('text', ''), 1500)}" for doc in pdf_docs]
        )

    bullets = _bullet_lines(local_evidence)
    if not bullets:
        bullets = _split_sentences(local_evidence)[:5]

    insights = bullets[:5] if bullets else [
        "The topic can be grounded in the uploaded PDFs and local knowledge base.",
        "A web-enabled mode is available when an OpenAI key is configured.",
        "The project is designed to degrade gracefully into local fallback mode.",
    ]

    recommendations = [
        "Upload more relevant PDFs to improve grounding.",
        "Add more notes to the knowledge base for better local retrieval.",
        "Use the OpenAI mode when you need current web research and richer synthesis.",
    ]

    refs: List[Reference] = reference_seeds[:]
    for doc in pdf_docs:
        snippet = _truncate(doc.get("text", ""), 280).replace("\n", " ")
        if snippet:
            refs.append(
                Reference(
                    title=doc["name"],
                    source_type="pdf",
                    url_or_path=doc["name"],
                    snippet=snippet,
                )
            )

    if not refs:
        refs = [
            Reference(
                title="Local knowledge base",
                source_type="local",
                url_or_path="knowledge_base/",
                snippet="No local references found.",
            )
        ]

    return ResearchReport(
        topic=topic,
        mode="local_fallback",
        executive_summary=_simple_summary(summary_source),
        key_insights=insights,
        recommendations=recommendations,
        references=refs[:8],
    )


def build_report(topic: str, pdf_files=None) -> ResearchReport:
    pdf_docs = extract_many_pdfs(pdf_files or [])
    local_evidence, reference_seeds = gather_local_evidence(topic, pdf_docs)

    client = _openai_client()
    if client is None:
        return _build_local_report(topic, local_evidence, reference_seeds, pdf_docs)

    try:
        evidence = research_agent_openai(topic, local_evidence, pdf_docs)
        analysis = analysis_agent_openai(topic, evidence)
        report = writer_agent_openai(topic, analysis, reference_seeds)
        if not report.references:
            report.references = reference_seeds[:]
        return report
    except Exception as e:
        print("OpenAI failed:", e)
        return _build_local_report(topic, local_evidence, reference_seeds, pdf_docs)