import os
import sys
from pathlib import Path
from unittest import mock

from s3_tool.main import create_upload_list


# TODO turn into fixture
def test_create_upload_list(tmp_path):
    d = tmp_path / "upload-files"
    d.mkdir()
    for i in range(10):
        p = d / f"file {i}.txt"
        p.write_text(f"{i}")

    create_upload_list(
        files_path=d, file_extension="txt", output_path=d,
    )

    upload_txt_path = Path(os.path.join(d, "upload.txt"))
    assert upload_txt_path.exists() == True

    for i in upload_txt_path.read_text().split(","):
        assert Path(i).exists()


def test_compatible_os():
    sys.platform = mock.Mock(return_value="win32")
    assert sys.platform.startswith("win32")


@mock.patch("s3_tool.main.os_platform")
# @mock.patch("s3_tool.main._get_os")
def test_incompatible_os(mock_sys, tmp_path, capsys):
    mock_sys.__str__.return_value = "darwin"

    d = tmp_path / "upload-files"
    d.mkdir()
    for i in range(10):
        p = d / f"file {i}.txt"
        p.write_text(f"{i}")

    create_upload_list(
        files_path=d, file_extension="txt", output_path=d,
    )

    captured = capsys.readouterr()
    assert captured.out == "OS not compatible\n"
