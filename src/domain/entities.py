"""
Domain entities — pure business logic, zero external imports.

These are the core concepts of the system, independent of any technology.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    """Difficulty of educational content."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class RenderStatus(str, Enum):
    """Lifecycle of a render job."""

    PENDING = "pending"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"


class PublishStatus(str, Enum):
    """Lifecycle of a publication."""

    DRAFT = "draft"
    PUBLISHED = "published"
    FAILED = "failed"


@dataclass(frozen=True)
class Prompt:
    """
    Immutable pedagogical prompt for video generation.
    Used as cache key (SHA-256 of canonical form).
    """

    topic: str
    difficulty: DifficultyLevel
    target_duration_seconds: int
    style_notes: str = ""
    language: str = "pt-BR"

    def canonical_form(self) -> str:
        """Deterministic string for hashing."""
        return (
            f"topic={self.topic.lower().strip()}\n"
            f"difficulty={self.difficulty.value}\n"
            f"duration={self.target_duration_seconds}\n"
            f"style={self.style_notes.lower().strip()}\n"
            f"lang={self.language}"
        )

    def hash(self) -> str:
        """SHA-256 of canonical form — used as cache key."""
        import hashlib

        return hashlib.sha256(self.canonical_form().encode()).hexdigest()


@dataclass
class SceneManifest:
    """
    Validated Manim scene metadata.
    Extracted from script AST before rendering.
    """

    class_name: str
    file_path: str
    duration_estimate_seconds: float
    resolution: tuple[int, int] = (854, 480)  # 480p default
    has_illegal_imports: bool = False
    has_file_io: bool = False
    validation_errors: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return (
            not self.has_illegal_imports
            and not self.has_file_io
            and len(self.validation_errors) == 0
        )


@dataclass
class RenderJob:
    """
    A render attempt for a given prompt.
    """

    job_id: str
    prompt: Prompt
    status: RenderStatus = RenderStatus.PENDING
    script_content: str = ""
    output_path: str | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int = 0
    retry_count: int = 0
    max_retries: int = 3

    def can_retry(self) -> bool:
        """Whether this job can be retried."""
        return self.retry_count < self.max_retries


@dataclass
class VideoAsset:
    """
    A successfully rendered video, ready for publication.
    """

    asset_id: str  # Same as prompt hash
    prompt: Prompt
    file_path: str
    file_size_bytes: int
    duration_seconds: float
    checksum_sha256: str
    rendered_at: datetime
    template_id: str | None = None  # If derived from template


@dataclass
class Publication:
    """
    A video published to Google Classroom.
    """

    publication_id: str
    video_asset: VideoAsset
    course_id: str
    drive_file_id: str
    coursework_id: str | None = None  # If published as assignment/material
    status: PublishStatus = PublishStatus.DRAFT
    published_at: datetime | None = None
    student_view_url: str | None = None
