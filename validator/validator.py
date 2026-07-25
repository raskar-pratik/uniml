"""
UniML — Model Validator

Validates an uploaded model by:
1. Checking file existence and basic sanity
2. Detecting the framework
3. Delegating to the framework handler's validate() method
4. Building a structured ValidationReport
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from converter.detector import detect_framework
from converter.handlers import find_handler
from models.enums import MLFramework, ValidationSeverity
from models.schemas import ValidationIssue, ValidationReport


def validate_model(file_path: Path) -> ValidationReport:
    """
    Run all validation checks on a model file and return a report.
    """
    issues: list[ValidationIssue] = []
    model_id = ""

    # ── 1. File existence ────────────────────────────────────────
    if not file_path.exists():
        return ValidationReport(
            model_id=model_id,
            framework=MLFramework.UNKNOWN,
            is_valid=False,
            issues=[ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                code="FILE_MISSING",
                message=f"File not found: {file_path}",
            )],
        )

    # ── 2. File size sanity ──────────────────────────────────────
    file_size = file_path.stat().st_size
    if file_size == 0:
        return ValidationReport(
            model_id=model_id,
            framework=MLFramework.UNKNOWN,
            is_valid=False,
            issues=[ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                code="EMPTY_FILE",
                message="File is empty (0 bytes)",
            )],
        )

    if file_size < 100:
        issues.append(ValidationIssue(
            severity=ValidationSeverity.WARNING,
            code="TINY_FILE",
            message=f"File is very small ({file_size} bytes) — might not be a valid model",
        ))

    # ── 3. Detect framework ──────────────────────────────────────
    detection = detect_framework(file_path)
    framework = detection.framework

    if framework == MLFramework.UNKNOWN:
        issues.append(ValidationIssue(
            severity=ValidationSeverity.ERROR,
            code="UNKNOWN_FRAMEWORK",
            message="Could not identify the ML framework for this file",
        ))
        return ValidationReport(
            model_id=model_id,
            framework=framework,
            is_valid=False,
            issues=issues,
        )

    issues.append(ValidationIssue(
        severity=ValidationSeverity.INFO,
        code="FRAMEWORK_DETECTED",
        message=f"Detected framework: {framework.value} (confidence: {detection.confidence})",
    ))

    # ── 4. Framework-specific validation ─────────────────────────
    handler = find_handler(file_path)
    input_shape = None
    output_shape = None
    model_class = None
    parameters = None

    if handler is not None:
        if not handler.is_available():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="LIB_NOT_INSTALLED",
                message=f"{handler.framework_name} library is not installed — "
                        f"limited validation only",
            ))
        else:
            # Run handler validation
            try:
                result = handler.validate(file_path)
                for issue_dict in result.get("issues", []):
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity(issue_dict["severity"]),
                        code=issue_dict["code"],
                        message=issue_dict["message"],
                    ))

                if not result.get("is_valid", True):
                    return ValidationReport(
                        model_id=model_id,
                        framework=framework,
                        is_valid=False,
                        issues=issues,
                    )

            except Exception as exc:
                logger.error("Handler validation error: {}", exc)
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="VALIDATION_ERROR",
                    message=f"Validation error: {exc}",
                ))

            # Extract model info
            try:
                info = handler.get_model_info(file_path)
                input_shape = info.get("input_shape")
                output_shape = info.get("output_shape")
                model_class = info.get("model_class")
                parameters = info.get("parameters")
            except Exception as exc:
                logger.warning("Could not extract model info: {}", exc)

    # ── Build final report ───────────────────────────────────────
    is_valid = not any(
        issue.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL)
        for issue in issues
    )

    return ValidationReport(
        model_id=model_id,
        framework=framework,
        is_valid=is_valid,
        issues=issues,
        input_shape=input_shape,
        output_shape=output_shape,
        model_class=model_class,
        parameters=parameters,
    )


