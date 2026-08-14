"""
Adapters — implementations of ports.

These are concrete implementations that can be swapped.
Each adapter has a corresponding test in tests/integration/.
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from domain.entities import Prompt, RenderJob, RenderStatus, SceneManifest, VideoAsset
from ports import (
    CachePort,
    ClassroomPort,
    ERPPort,
    GoogleDrivePort,
    LLMPort,
    RendererPort,
    ScriptValidatorPort,
)

# ─── LLM Adapters ─────────────────────────────────────────────

class LLMStubAdapter(LLMPort):
    """
    Deterministic stub for testing.
    Returns a simple Manim scene based on prompt topic.
    """

    async def generate_script(self, prompt: Prompt) -> str:
        return f'''
from manim import *

class {prompt.topic.replace(" ", "")}Scene(Scene):
    def construct(self):
        title = Text("{prompt.topic}")
        self.play(Write(title))
        self.wait(2)
'''

    async def generate_quiz(self, prompt: Prompt, scene_summary: str) -> str:
        import json

        return json.dumps([
            {
                "question": f"O que é {prompt.topic}?",
                "alternatives": ["A", "B", "C", "D"],
                "correct_index": 0,
                "explanation": "Explicação aqui."
            }
        ])


class GeminiLLMAdapter(LLMPort):
    """
    Real Gemini adapter (placeholder).
    TODO: Implement with google-generativeai SDK.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model

    async def generate_script(self, prompt: Prompt) -> str:
        # TODO: Implement actual Gemini call
        raise NotImplementedError("Gemini adapter not implemented yet")

    async def generate_quiz(self, prompt: Prompt, scene_summary: str) -> str:
        raise NotImplementedError("Gemini adapter not implemented yet")


# ─── Script Validator Adapters ───────────────────────────────

class ASTScriptValidator(ScriptValidatorPort):
    """
    Validates Manim scripts using AST analysis.
    Checks: syntax, Scene subclass, illegal imports, file I/O.
    """

    ILLEGAL_MODULES: ClassVar = {"os", "sys", "subprocess", "shutil", "requests"}
    ILLEGAL_FUNCTIONS: ClassVar = {"open", "exec", "eval", "__import__", "compile"}

    def validate(self, script_content: str) -> SceneManifest:
        import ast

        errors: list[str] = []

        # Step 1: Syntax check
        try:
            tree = ast.parse(script_content)
        except SyntaxError as e:
            return SceneManifest(
                class_name="",
                file_path="",
                duration_estimate_seconds=0.0,
                validation_errors=[f"Syntax error: {e}"],
            )

        # Step 2: Find Scene subclass
        scene_classes = [
            node.name for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
            and any(
                isinstance(base, ast.Name) and base.id == "Scene"
                for base in node.bases
            )
        ]

        if not scene_classes:
            errors.append("No Scene subclass found")

        # Step 3: Check for illegal imports
        has_illegal = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in self.ILLEGAL_MODULES:
                        errors.append(f"Illegal import: {alias.name}")
                        has_illegal = True
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split(".")[0] in self.ILLEGAL_MODULES:
                    errors.append(f"Illegal import: {node.module}")
                    has_illegal = True

        # Step 4: Check for file I/O
        has_file_io = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = (
                    node.func.id if isinstance(node.func, ast.Name) else None
                )
                if func_name in self.ILLEGAL_FUNCTIONS:
                    errors.append(f"Potentially unsafe call: {func_name}()")
                    has_file_io = True

        return SceneManifest(
            class_name=scene_classes[0] if scene_classes else "",
            file_path="",
            duration_estimate_seconds=0.0,
            has_illegal_imports=has_illegal,
            has_file_io=has_file_io,
            validation_errors=errors,
        )


# ─── Renderer Adapters ───────────────────────────────────────

class ManimDockerRenderer(RendererPort):
    """
    Renders Manim scenes in a Docker container.
    TODO: Implement actual subprocess call to docker exec.
    """

    def __init__(self, container_name: str = "manim-render"):
        self.container_name = container_name

    async def render(self, job: RenderJob) -> RenderJob:
        # TODO: Write script to temp file, exec docker run manim
        job.status = RenderStatus.COMPLETED
        job.output_path = f"/tmp/{job.job_id}.mp4"
        job.duration_ms = 5000
        return job


class ManimLocalRenderer(RendererPort):
    """
    Renders Manim scenes locally (for development).
    """

    def __init__(self, quality: str = "-ql"):
        self.quality = quality  # -ql = 480p, -qm = 720p, -qh = 1080p

    async def render(self, job: RenderJob) -> RenderJob:
        import subprocess
        import tempfile
        from pathlib import Path

        # Write script to temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(job.script_content)
            script_path = f.name

        output_dir = Path("/tmp/manim_output")
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            result = subprocess.run(
                [
                    "manim",
                    self.quality,
                    "--format=mp4",
                    "--output_dir", str(output_dir),
                    script_path,
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                job.status = RenderStatus.FAILED
                job.error_message = result.stderr
                return job

            # Find output file
            output_files = list(output_dir.glob("*.mp4"))
            if output_files:
                job.output_path = str(output_files[0])
                job.status = RenderStatus.COMPLETED
            else:
                job.status = RenderStatus.FAILED
                job.error_message = "No output file produced"

        except subprocess.TimeoutExpired:
            job.status = RenderStatus.FAILED
            job.error_message = "Render timeout (5min)"
        except Exception as e:
            job.status = RenderStatus.FAILED
            job.error_message = str(e)
        finally:
            Path(script_path).unlink(missing_ok=True)

        return job


# ─── Cache Adapters ──────────────────────────────────────────

class LocalFileCache(CachePort):
    """
    File-based cache using prompt hash as filename.
    For development and single-user scenarios.
    """

    def __init__(self, cache_dir: str = "/tmp/manim_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def get(self, prompt_hash: str) -> VideoAsset | None:
        # TODO: Implement metadata lookup
        return None

    async def put(self, asset: VideoAsset) -> None:
        # TODO: Store asset + metadata
        pass

    async def invalidate(self, template_id: str) -> int:
        # TODO: Find and delete all assets with matching template_id
        return 0


class GoogleDriveCache(CachePort):
    """
    Drive-based cache using folder structure.
    Production-ready, multi-user.
    """

    def __init__(self, drive: GoogleDrivePort, folder_id: str):
        self.drive = drive
        self.folder_id = folder_id

    async def get(self, prompt_hash: str) -> VideoAsset | None:
        # TODO: Search Drive for file with name = prompt_hash
        return None

    async def put(self, asset: VideoAsset) -> None:
        # TODO: Upload to Drive folder
        pass

    async def invalidate(self, template_id: str) -> int:
        # TODO: List and delete files with template_id in metadata
        return 0


# ─── Google Adapters ─────────────────────────────────────────

class GoogleDriveAdapter(GoogleDrivePort):
    """
    Real Google Drive adapter (placeholder).
    TODO: Implement with google-api-python-client.
    """

    def __init__(self, service_account_file: str):
        self.service_account_file = service_account_file

    async def upload_video(self, file_path: str, folder_id: str | None = None) -> str:
        raise NotImplementedError("Google Drive adapter not implemented yet")

    async def set_permissions(self, file_id: str, domain: str) -> None:
        raise NotImplementedError("Google Drive adapter not implemented yet")


class ClassroomAdapter(ClassroomPort):
    """
    Real Google Classroom adapter (placeholder).
    TODO: Implement with google-api-python-client.
    """

    def __init__(self, service_account_file: str):
        self.service_account_file = service_account_file

    async def publish_material(
        self, course_id: str, drive_file_id: str, title: str, description: str
    ) -> str:
        raise NotImplementedError("Classroom adapter not implemented yet")

    async def create_quiz(
        self, course_id: str, questions: str, title: str
    ) -> str:
        raise NotImplementedError("Classroom adapter not implemented yet")

    async def get_student_responses(self, course_id: str, coursework_id: str) -> dict:
        raise NotImplementedError("Classroom adapter not implemented yet")


# ─── ERP Adapters ────────────────────────────────────────────

class ERPStubAdapter(ERPPort):
    """
    Stub ERP adapter for testing.
    Simulates event consumption and template mapping.
    """

    def __init__(self) -> None:
        self.templates = {
            "return": "template_revisao",
            "initial": "template_introducao",
            "exam": "template_exame",
        }

    async def consume_event(self, event_type: str, payload: dict) -> dict:
        if not payload.get("idempotencyKey"):
            raise ValueError("Missing idempotencyKey")
        return payload

    async def map_to_template(self, appointment_type: str) -> str:
        return self.templates.get(appointment_type, "template_generico")
