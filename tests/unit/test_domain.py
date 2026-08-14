"""
Tests for domain entities.
"""

from __future__ import annotations

from domain.entities import (
    DifficultyLevel,
    Prompt,
    RenderJob,
    SceneManifest,
    VideoAsset,
)


class TestPrompt:
    def test_hash_is_deterministic(self):
        """Same prompt always produces same hash."""
        p1 = Prompt(
            topic="Pitágoras",
            difficulty=DifficultyLevel.EASY,
            target_duration_seconds=180,
        )
        p2 = Prompt(
            topic="Pitágoras",
            difficulty=DifficultyLevel.EASY,
            target_duration_seconds=180,
        )
        assert p1.hash() == p2.hash()

    def test_different_prompts_different_hash(self):
        p1 = Prompt(
            topic="Pitágoras",
            difficulty=DifficultyLevel.EASY,
            target_duration_seconds=180,
        )
        p2 = Prompt(
            topic="Área do círculo",
            difficulty=DifficultyLevel.EASY,
            target_duration_seconds=180,
        )
        assert p1.hash() != p2.hash()

    def test_canonical_form_is_stable(self):
        p = Prompt(
            topic="  Pitágoras  ",  # whitespace should be normalized
            difficulty=DifficultyLevel.MEDIUM,
            target_duration_seconds=120,
            style_notes="  Blue theme  ",
        )
        canonical = p.canonical_form()
        assert "topic=pitágoras" in canonical
        assert "difficulty=medium" in canonical
        assert "duration=120" in canonical
        assert "style=blue theme" in canonical


class TestSceneManifest:
    def test_valid_manifest(self):
        manifest = SceneManifest(
            class_name="PitagorasScene",
            file_path="scenes/pitagoras.py",
            duration_estimate_seconds=180.0,
        )
        assert manifest.is_valid

    def test_invalid_with_illegal_imports(self):
        manifest = SceneManifest(
            class_name="BadScene",
            file_path="scenes/bad.py",
            duration_estimate_seconds=10.0,
            has_illegal_imports=True,
        )
        assert not manifest.is_valid

    def test_invalid_with_errors(self):
        manifest = SceneManifest(
            class_name="BadScene",
            file_path="scenes/bad.py",
            duration_estimate_seconds=10.0,
            validation_errors=["No Scene subclass found"],
        )
        assert not manifest.is_valid


class TestRenderJob:
    def test_can_retry_when_under_max(self):
        prompt = Prompt(
            topic="Test",
            difficulty=DifficultyLevel.EASY,
            target_duration_seconds=60,
        )
        job = RenderJob(job_id="test-1", prompt=prompt, retry_count=1, max_retries=3)
        assert job.can_retry()

    def test_cannot_retry_when_at_max(self):
        prompt = Prompt(
            topic="Test",
            difficulty=DifficultyLevel.EASY,
            target_duration_seconds=60,
        )
        job = RenderJob(job_id="test-2", prompt=prompt, retry_count=3, max_retries=3)
        assert not job.can_retry()


class TestVideoAsset:
    def test_asset_creation(self):
        prompt = Prompt(
            topic="Test",
            difficulty=DifficultyLevel.EASY,
            target_duration_seconds=60,
        )
        asset = VideoAsset(
            asset_id=prompt.hash(),
            prompt=prompt,
            file_path="/tmp/test.mp4",
            file_size_bytes=1024,
            duration_seconds=60.0,
            checksum_sha256=prompt.hash(),
            rendered_at="2026-08-13T00:00:00",
        )
        assert asset.asset_id == prompt.hash()
