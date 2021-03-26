from google.auth.credentials import AnonymousCredentials
from google.cloud import storage
from paaaaath import GCSPath, Path

OUTPUT_BUCKET = ""  # fill output bucket name

GCSPath.register_client(
    storage.Client(
        credentials=AnonymousCredentials(),
        client_options={
            "api_endpoint": "http://127.0.0.1:4443",  # use local gcs emulator
        },
    )
)


def main():
    p = Path("gs://local_test/abc")

    text = "abc"
    p.write_text(text)
    print(f"write text:{text}")
    print(f"read text:{p.read_text()}")


if __name__ == "__main__":
    main()
