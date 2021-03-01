from paaaaath import GCSPath, Path
from google.auth.credentials import AnonymousCredentials
from google.cloud import storage

OUTPUT_BUCKET = ""  # fill output bucket name

GCSPath.register_client(
    storage.Client(
        credentials=AnonymousCredentials(),
        client_options={
            "api_endpoint": "http://127.0.0.1:4443"  # use local gcs emulator
        },
    )
)

def main():
    p = Path("gs://local_test/abc")
    p.write_text("abc")
    assert p.read_text() == "abc"

if __name__ == "__main__":
    main()