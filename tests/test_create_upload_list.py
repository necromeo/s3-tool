import os
import sys
from pathlib import Path
from unittest import mock

from s3_tool.main import create_upload_list


def create_files(tmp_path):
    d = tmp_path / "upload-files"
    d.mkdir()
    for i in range(10):
        p = d / f"file {i}.txt"
        p.write_text(f"{i}")
    return d


def test_create_upload_list(tmp_path):
    d = create_files(tmp_path)

    create_upload_list(
        files_path=d,
        file_extension="txt",
        output_path=d,
    )

    upload_txt_path = Path(os.path.join(d, "upload.txt"))
    assert upload_txt_path.exists() is True

    for i in upload_txt_path.read_text().split(","):
        assert Path(i).exists()


def test_compatible_os():
    sys.platform = mock.Mock(return_value="win32")
    assert sys.platform.startswith("win32")


@mock.patch("s3_tool.main.os_platform")
def test_incompatible_os(mock_sys, tmp_path, capsys):
    mock_sys.__str__.return_value = "darwin"

    d = create_files(tmp_path)

    create_upload_list(
        files_path=d,
        file_extension="txt",
        output_path=d,
    )

    captured = capsys.readouterr()
    assert captured.out == "OS not compatible\n"
