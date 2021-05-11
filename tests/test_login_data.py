import os

import boto3
import pytest
from moto import mock_s3

from s3_tool.main import bucket


@pytest.fixture
def env_variables():
    os.environ["ENDPOINT"] = "endpoint"
    os.environ["ACCESS_KEY"] = "access_key"
    os.environ["SECRET_ACCESS_KEY"] = "aws_secret_access_key"
    os.environ["HTTP_PREFIX"] = "https://http_prefix.com/"


# @pytest.fixture
def test_getting_enviroment_variables(env_variables):
    assert os.getenv("ENDPOINT") == "endpoint"
    assert os.getenv("ACCESS_KEY") == "access_key"
    assert os.getenv("SECRET_ACCESS_KEY") == "aws_secret_access_key"
    assert os.getenv("HTTP_PREFIX") == "https://http_prefix.com/"


def test_bucket():
    bucket_name = bucket("bucket_name")
    assert bucket_name == "bucket_name"


# To use for the client upload_file method
def empty_file(tmp_path):
    d = tmp_path / "sub"
    d.mkdir(exist_ok=True)
    p = d / "empty2.txt"
    p.write_text("Empty Body")
    print("what is p?: ", p)
    return p


@mock_s3
def bucket_contents():

    # Resource with bucket
    conn = boto3.resource(
        "s3",
    )
    bucket_name = "testing_bucket"
    # We need to create the bucket since this is all in Moto's 'virtual' AWS account
    conn.create_bucket(Bucket=bucket_name)
    conn.Bucket(bucket_name).put_object(
        Key="source/empty.txt", Body="Empty value", ACL="public-read"
    )
    conn.Bucket(bucket_name).put_object(
        Key="delimiter/delimiter/empty2.txt", Body="Delimiter", ACL="public-read"
    )
    contents = conn.Bucket(name=bucket_name)

    client = boto3.client("s3")

    return contents, conn, bucket_name, client
