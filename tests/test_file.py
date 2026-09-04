from __future__ import annotations

from pathlib import Path

from python_multipart.multipart import File


def test_upload_dir_with_leading_slash_in_filename(tmp_path: Path) -> None:
    upload_dir = tmp_path / "upload"
    upload_dir.mkdir()

    # When the file_name provided has a leading slash, we should only use the basename.
    # This is to avoid directory traversal.
    to_upload = tmp_path / "foo.txt"

    file = File(
        bytes(to_upload),
        config={
            "UPLOAD_DIR": bytes(upload_dir),
            "UPLOAD_KEEP_FILENAME": True,
            "UPLOAD_KEEP_EXTENSIONS": True,
            "MAX_MEMORY_FILE_SIZE": 10,
        },
    )
    file.write(b"123456789012")
    assert not file.in_memory
    assert Path(upload_dir / "foo.txt").exists()
    assert Path(upload_dir / "foo.txt").read_bytes() == b"123456789012"


def test_upload_dir_with_relative_traversal_in_filename(tmp_path: Path) -> None:
    root = tmp_path / "root"
    upload_dir = root / "upload"
    upload_dir.mkdir(parents=True)

    # A file_name made of `..` segments must not be able to escape the upload directory.
    file = File(
        b"../escaped.txt",
        config={
            "UPLOAD_DIR": bytes(upload_dir),
            "UPLOAD_KEEP_FILENAME": True,
            "UPLOAD_KEEP_EXTENSIONS": True,
            "MAX_MEMORY_FILE_SIZE": 10,
        },
    )
    file.write(b"123456789012")
    assert not file.in_memory
    assert file.actual_file_name == b"escaped.txt"
    assert not Path(root / "escaped.txt").exists()
    assert Path(upload_dir / "escaped.txt").exists()
    assert Path(upload_dir / "escaped.txt").read_bytes() == b"123456789012"
