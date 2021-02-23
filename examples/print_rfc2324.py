from paaaaath import Path


def main():
    print(Path("https://www.ietf.org/rfc/rfc2324.txt").read_text())


if __name__ == "__main__":
    main()
