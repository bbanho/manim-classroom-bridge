"""
Ports — interfaces the domain depends on.

Domain never imports adapters. It only imports these interfaces.
Adapters implement them.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

# PublishStatus is used in annotations below
from domain.entities import (
    Prompt,
    RenderJob,
    SceneManifest,
    VideoAsset,
)
from domain.entities import (
    Publication as Publication,
)
from domain.entities import (
    PublishStatus as PublishStatus,
)
from domain.entities import (
    RenderStatus as RenderStatus,
)


class LLMPort(ABC):
    """Generates Manim Python scripts from pedagogical prompts."""

    @abstractmethod
    async def generate_script(self, prompt: Prompt) -> str:
        """Return valid Python Manim script content."""
        ...

    @abstractmethod
    async def generate_quiz(self, prompt: Prompt, scene_summary: str) -> str:
        """Return JSON with 5-10 multiple-choice questions."""
        ...


class ScriptValidatorPort(ABC):
    """Validates generated scripts before rendering."""

    @abstractmethod
    def validate(self, script_content: str) -> SceneManifest:
        """
        Return manifest with validation results.
        Must check: syntax, AST structure, illegal imports, file I/O.
        """
        ...


class RendererPort(ABC):
    """Executes Manim and produces video artifacts."""

    @abstractmethod
    async def render(self, job: RenderJob) -> RenderJob:
        """Execute render, update job with result. Returns updated job."""
        ...


class CachePort(ABC):
    """Stores and retrieves rendered video artifacts by prompt hash."""

    @abstractmethod
    async def get(self, prompt_hash: str) -> VideoAsset | None:
        """Return cached asset or None."""
        ...

    @abstractmethod
    async def put(self, asset: VideoAsset) -> None:
        """Store asset by prompt_hash."""
        ...

    @abstractmethod
    async def invalidate(self, template_id: str) -> int:
        """Invalidate all assets derived from template. Returns count invalidated."""
        ...


class GoogleDrivePort(ABC):
    """Uploads files to Google Drive with permissions."""

    @abstractmethod
    async def upload_video(
        self, file_path: str, folder_id: str | None = None
    ) -> str:
        """
        Upload video to Drive.
        Returns drive_file_id.
        """
        ...

    @abstractmethod
    async def set_permissions(self, file_id: str, domain: str) -> None:
        """Grant reader access to entire Google Workspace domain."""
        ...


class ClassroomPort(ABC):
    """Publishes content to Google Classroom."""

    @abstractmethod
    async def publish_material(
        self,
        course_id: str,
        drive_file_id: str,
        title: str,
        description: str,
    ) -> str:
        """Create CourseWorkMaterial. Returns coursework_id."""
        ...

    @abstractmethod
    async def create_quiz(
        self,
        course_id: str,
        questions: str,  # JSON from LLM
        title: str,
    ) -> str:
        """Create quiz assignment. Returns coursework_id."""
        ...

    @abstractmethod
    async def get_student_responses(self, course_id: str, coursework_id: str) -> dict[str, int]:
        """Return {student_id: score}."""
        ...


class ERPPort(ABC):
    """Consumes events from external ERP system."""

    @abstractmethod
    async def consume_event(self, event_type: str, payload: dict) -> dict:
        """
        Consume one event from ERP queue.
        Must handle idempotency via idempotencyKey.
        """
        ...

    @abstractmethod
    async def map_to_template(self, appointment_type: str) -> str:
        """Return template_id for given appointment type."""
        ...
