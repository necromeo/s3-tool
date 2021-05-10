import os
from datetime import datetime
from unittest import mock
import ast
import pytest
from moto import mock_s3

from s3_tool.main import change_permissions, list_keys
from s3_tool.choices import access_types

from .test_login_data import bucket_contents


"""
Permissions are:
    "private"
    "public-read"
    "public-read-write"
    "authenticated-read"
    "aws-exec-read"
    "bucket-owner-read"
    "bucket-owner-full-control"
"""


@pytest.fixture
def env_variables():
    os.environ["ENDPOINT"] = "endpoint"
    os.environ["ACCESS_KEY"] = "access_key"
    os.environ["SECRET_ACCESS_KEY"] = "aws_secret_access_key"
    os.environ["HTTP_PREFIX"] = "https://http_prefix.com/"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_change_permissions_public_read_write(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    change_permissions(
        args=["source/empty.txt"],
        prefix_threads=1,
        changer_threads=1,
        permissions=access_types.ACLTypes.public_read_write,
    )

    list_keys(
        limit=0,
        prefix="source/empty.txt",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods="acl",
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert "<Element " in captured.out


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_change_permissions_public_read(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    change_permissions(
        args=["source/empty.txt"],
        prefix_threads=1,
        changer_threads=1,
        permissions=access_types.ACLTypes.public_read,
    )

    list_keys(
        limit=0,
        prefix="source/empty.txt",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods="acl",
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    captured_dict = ast.literal_eval(captured.out)
    assert len(captured_dict) == 2
    assert captured_dict[1].get("Grantee").get("Type") == "Group"
    assert captured_dict[1].get("Permission") == "READ"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_change_permissions_private(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    change_permissions(
        args=["source/empty.txt"],
        prefix_threads=1,
        changer_threads=1,
        permissions=access_types.ACLTypes.private,
    )

    list_keys(
        limit=0,
        prefix="source/empty.txt",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods="acl",
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    captured_dict = ast.literal_eval(captured.out)
    assert len(captured_dict) == 1
    assert captured_dict[0].get("Grantee").get("Type") == "CanonicalUser"
    assert captured_dict[0].get("Permission") == "FULL_CONTROL"
    # assert (
    #     captured_dict[0].get("Grantee").get("URI")
    #     == "http://acs.amazonaws.com/groups/global/AllUsers"
    # )


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_change_permissions_authenticated_read(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    change_permissions(
        args=["source/empty.txt"],
        prefix_threads=1,
        changer_threads=1,
        permissions=access_types.ACLTypes.authenticated_read,
    )

    list_keys(
        limit=0,
        prefix="source/empty.txt",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods="acl",
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    captured_dict = ast.literal_eval(captured.out)
    assert (
        captured_dict[1].get("Grantee").get("URI")
        == "http://acs.amazonaws.com/groups/global/AuthenticatedUsers"
    )


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_change_permissions_aws_exec_read(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    change_permissions(
        args=["source/empty.txt"],
        prefix_threads=1,
        changer_threads=1,
        permissions=access_types.ACLTypes.aws_exec_read,
    )

    list_keys(
        limit=0,
        prefix="source/empty.txt",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods="acl",
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    captured_dict = ast.literal_eval(captured.out)
    assert captured_dict[0].get("Grantee").get("Type") == "CanonicalUser"
    assert captured_dict[0].get("Permission") == "FULL_CONTROL"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_change_permissions_bucket_owner_full_control(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    change_permissions(
        args=["source/empty.txt"],
        prefix_threads=1,
        changer_threads=1,
        permissions=access_types.ACLTypes.bucket_owner_full_control,
    )

    list_keys(
        limit=0,
        prefix="source/empty.txt",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods="acl",
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    captured_dict = ast.literal_eval(captured.out)
    assert captured_dict[0].get("Grantee").get("Type") == "CanonicalUser"
    assert captured_dict[0].get("Permission") == "FULL_CONTROL"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_change_permissions_bucket_owner_read(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    change_permissions(
        args=["source/empty.txt"],
        prefix_threads=1,
        changer_threads=1,
        permissions=access_types.ACLTypes.bucket_owner_read,
    )

    list_keys(
        limit=0,
        prefix="source/empty.txt",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods="acl",
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    captured_dict = ast.literal_eval(captured.out)
    assert captured_dict[0].get("Grantee").get("Type") == "CanonicalUser"
    assert captured_dict[0].get("Permission") == "FULL_CONTROL"
