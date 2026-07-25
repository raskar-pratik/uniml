"""
UniML — Generator Tests

Tests for the code generation and ZIP packaging modules.
"""

from pathlib import Path

import pytest


class TestApiGenerator:
    """Test the FastAPI server generator."""

    def test_generates_all_files(self, tmp_path):
        """Should generate all expected server files."""
        from generator.api_generator import generate_api_server

        files = generate_api_server(
            output_dir=tmp_path / "output",
            project_name="test_server",
        )

        assert "main.py" in files
        assert "predict.py" in files
        assert "config.py" in files
        assert "requirements.txt" in files
        assert "README.md" in files

    def test_generated_files_exist_on_disk(self, tmp_path):
        """Generated files should actually exist."""
        from generator.api_generator import generate_api_server

        output_dir = tmp_path / "output"
        generate_api_server(output_dir=output_dir, project_name="test_server")

        assert (output_dir / "main.py").exists()
        assert (output_dir / "predict.py").exists()
        assert (output_dir / "config.py").exists()

    def test_generated_main_contains_fastapi(self, tmp_path):
        """Generated main.py should contain FastAPI import."""
        from generator.api_generator import generate_api_server

        output_dir = tmp_path / "output"
        generate_api_server(output_dir=output_dir, project_name="test_server")

        content = (output_dir / "main.py").read_text()
        assert "FastAPI" in content
        assert "/predict" in content
        assert "/health" in content


class TestDockerGenerator:
    """Test the Docker configuration generator."""

    def test_generates_docker_files(self, tmp_path):
        """Should generate Dockerfile and docker-compose.yml."""
        from generator.docker_generator import generate_docker_files

        files = generate_docker_files(
            output_dir=tmp_path / "output",
            project_name="test_server",
            port=8080,
        )

        assert "Dockerfile" in files
        assert "docker-compose.yml" in files
        assert "startup.sh" in files


class TestZipPackager:
    """Test the ZIP packaging module."""

    def test_creates_zip_file(self, tmp_path):
        """Should create a .zip file."""
        from generator.zip_packager import create_zip_package

        # Create some dummy files
        source = tmp_path / "source"
        source.mkdir()
        (source / "main.py").write_text("print('hello')")
        (source / "config.py").write_text("PORT = 8080")

        output = tmp_path / "output"
        zip_path = create_zip_package(
            source_dir=source,
            output_dir=output,
            archive_name="test_package",
        )

        assert zip_path.exists()
        assert zip_path.suffix == ".zip"
        assert zip_path.stat().st_size > 0

    def test_zip_contains_files(self, tmp_path):
        """ZIP should contain all source files."""
        import zipfile
        from generator.zip_packager import create_zip_package

        source = tmp_path / "source"
        source.mkdir()
        (source / "main.py").write_text("print('hello')")

        output = tmp_path / "output"
        zip_path = create_zip_package(
            source_dir=source,
            output_dir=output,
            archive_name="test_pkg",
        )

        with zipfile.ZipFile(str(zip_path), "r") as zf:
            names = zf.namelist()
            assert any("main.py" in n for n in names)
