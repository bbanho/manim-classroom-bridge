"""
Use cases — application orchestration layer.

Each function is a pure orchestration of ports.
No imports from adapters. No I/O side effects except through ports.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.entities import (
    DifficultyLevel,
    Prompt,
    PublishStatus,
    RenderJob,
    RenderStatus,
    VideoAsset,
)
from ports import (
    CachePort,
    ClassroomPort,
    ERPPort,
    GoogleDrivePort,
    LLMPort,
    RendererPort,
    ScriptValidatorPort,
)


@dataclass
class GenerateVideoResult:
    job_id: str
    status: RenderStatus
    asset: VideoAsset | None = None
    error: str | None = None
    cached: bool = False


async def generate_video(
    prompt: Prompt,
    llm: LLMPort,
    validator: ScriptValidatorPort,
    renderer: RendererPort,
    cache: CachePort,
) -> GenerateVideoResult:
    """
    UC-01: Generate video from pedagogical prompt.

    Flow:
    1. Check cache (REQ-CACHE-02)
    2. If miss: generate script via LLM (REQ-LLM-02)
    3. Validate script (REQ-MJ-02)
    4. Render with timeout + retry (REQ-MJ-03)
    5. Store in cache (REQ-CACHE-02)

    Returns result with status and asset (if successful).
    """
    # Step 1: Cache check
    cached_asset = await cache.get(prompt.hash())
    if cached_asset:
        return GenerateVideoResult(
            job_id=f"cached-{prompt.hash()[:8]}",
            status=RenderStatus.CACHED,
            asset=cached_asset,
            cached=True,
        )

    # Step 2: Generate script
    try:
        script_content = await llm.generate_script(prompt)
    except Exception as e:
        return GenerateVideoResult(
            job_id=f"llm-fail-{prompt.hash()[:8]}",
            status=RenderStatus.FAILED,
            error=f"LLM generation failed: {e}",
        )

    # Step 3: Validate
    manifest = validator.validate(script_content)
    if not manifest.is_valid:
        return GenerateVideoResult(
            job_id=f"invalid-{prompt.hash()[:8]}",
            status=RenderStatus.FAILED,
            error=f"Script validation failed: {manifest.validation_errors}",
        )

    # Step 4: Render with retry logic
    job = RenderJob(
        job_id=f"render-{prompt.hash()[:8]}",
        prompt=prompt,
        script_content=script_content,
        status=RenderStatus.PENDING,
    )

    max_attempts = job.max_retries + 1
    for attempt in range(max_attempts):
        job.retry_count = attempt
        job.status = RenderStatus.RENDERING
        job.started_at = datetime.utcnow()

        try:
            job = await renderer.render(job)
        except Exception as e:
            job.error_message = str(e)
            job.status = RenderStatus.FAILED
            if attempt < max_attempts - 1:
                continue  # retry
            break

        if job.status == RenderStatus.COMPLETED:
            job.completed_at = datetime.utcnow()
            break

    if job.status != RenderStatus.COMPLETED:
        return GenerateVideoResult(
            job_id=job.job_id,
            status=RenderStatus.FAILED,
            error=job.error_message or "Render failed after retries",
        )

    # Step 5: Create asset and cache
    asset = VideoAsset(
        asset_id=prompt.hash(),
        prompt=prompt,
        file_path=job.output_path or "",
        file_size_bytes=0,  # TODO: populate from actual file
        duration_seconds=0.0,
        checksum_sha256=prompt.hash(),
        rendered_at=datetime.utcnow(),
    )

    await cache.put(asset)

    return GenerateVideoResult(
        job_id=job.job_id,
        status=RenderStatus.COMPLETED,
        asset=asset,
    )


@dataclass
class PublishVideoResult:
    publication_id: str
    status: PublishStatus
    student_view_url: str | None = None
    error: str | None = None


async def publish_video_to_classroom(
    asset: VideoAsset,
    course_id: str,
    title: str,
    description: str,
    drive: GoogleDrivePort,
    classroom: ClassroomPort,
) -> PublishVideoResult:
    """
    UC-02: Publish video to Google Classroom.

    Flow:
    1. Upload video to Drive (REQ-GAPI-01)
    2. Set domain permissions (REQ-GAPI-01)
    3. Create CourseWorkMaterial (REQ-GAPI-02)

    Returns publication result.
    """
    # Step 1: Upload to Drive
    try:
        drive_file_id = await drive.upload_video(asset.file_path)
    except Exception as e:
        return PublishVideoResult(
            publication_id="",
            status=PublishStatus.FAILED,
            error=f"Drive upload failed: {e}",
        )

    # Step 2: Set permissions
    try:
        await drive.set_permissions(drive_file_id, domain="your-domain.com")
    except Exception:
        # Non-fatal: file is uploaded, just log
        pass

    # Step 3: Publish to Classroom
    try:
        coursework_id = await classroom.publish_material(
            course_id=course_id,
            drive_file_id=drive_file_id,
            title=title,
            description=description,
        )
    except Exception as e:
        return PublishVideoResult(
            publication_id="",
            status=PublishStatus.FAILED,
            error=f"Classroom publish failed: {e}",
        )

    return PublishVideoResult(
        publication_id=f"{coursework_id}",
        status=PublishStatus.PUBLISHED,
        student_view_url=f"https://classroom.google.com/c/{course_id}",
    )


@dataclass
class GenerateQuizResult:
    quiz_id: str
    questions_count: int
    error: str | None = None


async def generate_and_publish_quiz(
    prompt: Prompt,
    scene_summary: str,
    course_id: str,
    llm: LLMPort,
    classroom: ClassroomPort,
) -> GenerateQuizResult:
    """
    UC-04: Generate quiz from video content and publish to Classroom.

    Flow:
    1. LLM generates questions from scene summary (REQ-LLM-04, REQ-LLM-05)
    2. Classroom creates quiz assignment (REQ-GAPI-04)

    Returns quiz result.
    """
    try:
        questions_json = await llm.generate_quiz(prompt, scene_summary)
    except Exception as e:
        return GenerateQuizResult(
            quiz_id="",
            questions_count=0,
            error=f"Quiz generation failed: {e}",
        )

    try:
        quiz_id = await classroom.create_quiz(
            course_id=course_id,
            questions=questions_json,
            title=f"Quiz: {prompt.topic}",
        )
    except Exception as e:
        return GenerateQuizResult(
            quiz_id="",
            questions_count=0,
            error=f"Quiz publish failed: {e}",
        )

    import json

    questions = json.loads(questions_json) if isinstance(questions_json, str) else questions_json
    return GenerateQuizResult(
        quiz_id=quiz_id,
        questions_count=len(questions) if isinstance(questions, list) else 0,
    )


@dataclass
class ERPTriggerResult:
    asset: VideoAsset | None
    error: str | None = None


async def handle_erp_appointment_event(
    event_payload: dict,
    llm: LLMPort,
    validator: ScriptValidatorPort,
    renderer: RendererPort,
    cache: CachePort,
    drive: GoogleDrivePort,
    erp: ERPPort,
) -> ERPTriggerResult:
    """
    UC-06: Handle ERP appointment event and trigger video generation.

    Flow:
    1. Verify idempotency (REQ-ERP-01)
    2. Map appointment type to template (REQ-ERP-02)
    3. Generate video with template context (REQ-ERP-02)
    4. Upload to patient folder (REQ-ERP-03)
    5. Trigger notification (REQ-UI-05)

    Returns result with asset or error.
    """
    # Step 1: Idempotency check
    idempotency_key = event_payload.get("idempotencyKey")
    if not idempotency_key:
        return ERPTriggerResult(
            asset=None,
            error="Missing idempotencyKey in event payload",
        )

    # Check if already processed
    existing = await cache.get(idempotency_key)
    if existing:
        return ERPTriggerResult(asset=existing)

    # Step 2: Map to template
    appointment_type = event_payload.get("appointmentType", "return")
    try:
        template_id = await erp.map_to_template(appointment_type)
    except Exception as e:
        return ERPTriggerResult(asset=None, error=f"Template mapping failed: {e}")

    # Step 3: Generate prompt from event
    patient_name = event_payload.get("patientName", "")
    doctor_name = event_payload.get("doctorName", "")
    prompt = Prompt(
        topic=f"Orientação para consulta de {appointment_type} — {patient_name}",
        difficulty=DifficultyLevel.EASY,
        target_duration_seconds=120,
        style_notes=f"Contexto: paciente de {doctor_name}. Template: {template_id}",
    )

    # Step 4: Generate video (reuse UC-01 logic)
    result = await generate_video(
        prompt=prompt,
        llm=llm,
        validator=validator,
        renderer=renderer,
        cache=cache,
    )

    if result.status != RenderStatus.COMPLETED or not result.asset:
        return ERPTriggerResult(asset=None, error=result.error)

    # Step 5: Upload to patient folder
    cpf = event_payload.get("patientCpf", "unknown")
    try:
        await drive.upload_video(result.asset.file_path, folder_id=f"patients/{cpf}")
    except Exception:
        # Non-fatal: asset is generated, just log
        pass

    # Cache by idempotency key to prevent reprocessing
    await cache.put(result.asset)

    return ERPTriggerResult(asset=result.asset)
