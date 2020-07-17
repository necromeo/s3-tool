# S3 Command Line Utility

### Credentials

First of all, you will need to have your credentials ready.
The following are needed (next to them are the names of the environmental variables associated to them):

- Endpoint `ENDPOINT`
- Access Key `ACCESS_KEY`
- Secret Access Key `SECRET_ACCESS_KEY`
- Bucket `BUCKET`
- OPTIONALLY: if you have an HTTP prefix for accessing keys over a web browser you can add it with the `HTTP_PREFIX` variable

In order to avoid having to introduce your credentials after every command execution it is possible to store them as environmental variables.
You can even do this temporarily setting a variables as `export ENDPOINT_URL=MyURL`. This way, your credentials will only be set for the current terminal.

### Operations

The following operations are possible:

- Listing all keys in a bucket
- Listing keys according to a prefix in a bucket
- Change key permissions to public-read
- Upload any number of keys. Is Multithreaded.
- Download any number of keys. Is Multithreaded.
- Delete keys. Is Multithreaded.

---

**Usage**:

```console
$ s3-tool [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--install-completion`: Install completion for the current shell.
- `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
- `--help`: Show this message and exit.

**Commands**:

- `change-permissions`: Takes any number of keys and changes their...
- `delete-key`: USE WITH EXTREME CAUTION! Deletes a given key...
- `download`: Downloads a key or series of keys
- `list-keys`: Lists keys according to a given prefix
- `upload`: Uploads a single file or multiple files.

## `s3-tool change-permissions`

Takes any number of keys and changes their permissions to public-read

**Usage**:

```console
$ s3-tool change-permissions [OPTIONS] ARGS...
```

**Options**:

- `--prefix-threads INTEGER`: Sets the amount of prefixes that should be queried in parallel
- `--changer-threads INTEGER`: Sets the amount of threads used to change permissions for a given prefix
- `--permissions TEXT`: Options are: 'private' | 'public-read' | 'public-read-write' | 'authenticated-read' | 'aws-exec-read ' |'bucket-owner-read' | 'bucket-owner-full-control'
- `--help`: Show this message and exit.

## `s3-tool delete-key`

USE WITH EXTREME CAUTION! Deletes a given key or keys

**Usage**:

```console
$ s3-tool delete-key [OPTIONS] FILES...
```

**Options**:

- `--prompt / --no-prompt`: Display a prompt to confirm deletion
- `--threads INTEGER`: Set the amount of threads to delete keys in parallel. Disable the prompt if using this option
- `--help`: Show this message and exit.

## `s3-tool download`

Downloads a key or series of keys

**Usage**:

```console
$ s3-tool download [OPTIONS] FILES...
```

**Options**:

- `--download-path TEXT`: Sets download path. Will download in the folder where the command is executed if none is set
- `--worker-threads INTEGER`: Amount of threads used to download in parallel
- `--help`: Show this message and exit.

## `s3-tool list-keys`

Lists keys according to a given prefix

**Usage**:

```console
$ s3-tool list-keys [OPTIONS]
```

**Options**:

- `--prefix TEXT`: Prefix to look for keys
- `--delimiter TEXT`: A delimiter is a character you use to group keys.
- `--http-prefix / --no-http-prefix`: Append HTTP URL Prefix to keys
- `--all / --no-all`: USE WITH CAUTION! If True, will fetch every key in the Bucket
- `--help`: Show this message and exit.

## `s3-tool upload`

Uploads a single file or multiple files. Files need to have their absolute path.
The last argument passed will be the upload path.
Optionally, one can choose the amount of threads that should be used.

**Usage**:

```console
$ s3-tool upload [OPTIONS] FILES... UPLOAD_PATH
```

**Options**:

- `--permissions TEXT`: Sets the permission for the uploaded file. Options are: 'private' | 'public-read' | 'public-read-write ' |'authenticated-read' | 'aws-exec-read' | 'bucket-owner-read' | 'bucket-owner-full-control'
- `--worker-threads INTEGER`: Amount of threads used to upload in parallel
- `--help`: Show this message and exit.
