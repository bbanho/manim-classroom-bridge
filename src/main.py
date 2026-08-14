"""Manim × Classroom Bridge — entry point."""

from __future__ import annotations

import asyncio

from domain.entities import DifficultyLevel, Prompt
from usecases import generate_video


async def main() -> None:
    """CLI entry point for v0.1."""
    prompt = Prompt(
        topic="Pitágoras",
        difficulty=DifficultyLevel.EASY,
        target_duration_seconds=180,
        style_notes="Visual style: clean, minimal",
    )

    # TODO: Wire adapters here
    from adapters import ASTScriptValidator, LLMStubAdapter, LocalFileCache, ManimLocalRenderer

    llm = LLMStubAdapter()
    validator = ASTScriptValidator()
    renderer = ManimLocalRenderer()
    cache = LocalFileCache()

    result = await generate_video(prompt, llm, validator, renderer, cache)

    print(f"Job: {result.job_id}")
    print(f"Status: {result.status}")
    if result.asset:
        print(f"Asset: {result.asset.file_path}")
    if result.error:
        print(f"Error: {result.error}")


if __name__ == "__main__":
    asyncio.run(main())
