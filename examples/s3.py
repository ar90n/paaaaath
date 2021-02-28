from paaaaath import Path, S3Path

OUTPUT_BUCKET = ""  # fill output bucket name


def main():
    png_images = []
    for p in Path("s3://elevation-tiles-prod/normal/10/963").iterdir():
        if p.suffix != ".png":
            continue

        png_images.append(p)
        if 3 < len(png_images):
            break

    for input_path in png_images:
        if OUTPUT_BUCKET != "":
            output_path = Path(f"s3://{OUTPUT_BUCKET}/{input_path.name}")
            print(f"upload {output_path.name} to {output_path}")
            output_path.write_bytes(p.read_bytes())
        else:
            print(f"skip upload {input_path.name}")


if __name__ == "__main__":
    main()
