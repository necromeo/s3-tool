import os
from pathlib import Path
from unittest import mock

import pytest
from click.exceptions import Exit as TyperExit
from moto import mock_s3
from typer import Abort

from s3_tool.main import download

from .test_login_data import bucket_contents


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_download_file(mock_bucket, tmp_path):
    mock_bucket.return_value = bucket_contents()

    download_folder = tmp_path / "download_folder"
    download_folder.mkdir()

    download(
        download_path=download_folder,
        files=["source/empty.txt"],
        recursive=None,
        threads=1,
    )

    expected_file = Path(os.path.join(download_folder, "empty.txt"))

    assert Path.exists(expected_file) is True


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_download_multiple_files(mock_bucket, tmp_path):
    mock_bucket.return_value = bucket_contents()

    download_folder = tmp_path / "download_folder"
    download_folder.mkdir()

    download(
        download_path=download_folder,
        files=[
            "source/empty.txt",
            "delimiter/delimiter/empty2.txt",
        ],
        recursive=None,
        threads=2,
    )

    expected_files = [file for file in Path(download_folder).iterdir()]

    for file in expected_files:
        assert Path.exists(file) is True


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_download_is_not_file(mock_bucket, tmp_path, capsys):
    with pytest.raises(Abort):
        mock_bucket.return_value = bucket_contents()
        download_folder = tmp_path / "download_folder"
        download_folder.mkdir()

        download(
            download_path=download_folder,
            files=None,
            recursive=None,
            threads=1,
        )


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_download_recursive(mock_bucket, tmp_path):
    mock_bucket.return_value = bucket_contents()

    download_folder = tmp_path / "download_folder"
    download_folder.mkdir()

    download(
        download_path=download_folder,
        files=None,
        recursive="source/",
        threads=3,
    )

    expected_files = [file for file in Path(download_folder).glob("**/*.*")]

    for file in expected_files:
        assert Path.exists(file) is True


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_download_recursive_fail_with_no_delimiter(mock_bucket, tmp_path):
    mock_bucket.return_value = bucket_contents()

    download_folder = tmp_path / "download_folder"
    download_folder.mkdir()

    with pytest.raises(TyperExit):
        download(
            download_path=download_folder,
            files=None,
            recursive="source",
            threads=3,
        )
