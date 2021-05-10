from s3_tool.main import create_upload_list
from pathlib import Path
import os, sys
from mock import MagicMock
import mock

# TODO turn into fixture
def test_create_upload_list(tmp_path):
    d = tmp_path / "upload-files"
    d.mkdir()
    for i in range(10):
        p = d / f"file{i}.txt"
        p.write_text(f"{i}")

    create_upload_list(
        files_path=d,
        file_extension="txt",
        output_path=d,
    )

    upload_txt_path = Path(os.path.join(d, "upload.txt"))
    assert upload_txt_path.exists() == True

    for i in upload_txt_path.read_text().split(","):
        assert Path(i).exists()
        if sys.platform.startswith("linux"):
            assert i == f'"{i}"'


def test_compatible_os():
    assert sys.platform.startswith("win32")


# TODO mock the sys os
# @mock.patch(sys.platform, return_value="darwin")
def test_incompatible_os(tmp_path, capsys):
    # sys = mock.MagicMock()
    # sys.configure_mock(platform="darwin")
    with mock.patch("s3_tool.main.create_upload_list", return_value="darwin"):
        d = tmp_path / "upload-files"
        d.mkdir()
        for i in range(10):
            p = d / f"file{i}.txt"
            p.write_text(f"{i}")

        create_upload_list(
            files_path=d,
            file_extension="txt",
            output_path=d,
        )

        assert sys.platform.startswith("darwin")
