from paaaaath import Path

OUTPUT_BUCKET = ""  # fill output bucket name


def main():
    txts = []
    for p in Path(
        "gs://gcp-public-data-landsat/LC08/01/044/034/LC08_L1GT_044034_20130330_20170310_01_T2"
    ).iterdir():
        if p.suffix != ".txt":
            continue

        txts.append(p)

    for input_path in txts:
        if OUTPUT_BUCKET != "":
            output_path = Path(f"gs://{OUTPUT_BUCKET}/{input_path.name}")
            print(f"upload {output_path.name} to {output_path}")
            output_path.write_bytes(p.read_bytes())
        else:
            print(f"skip upload {input_path.name}")


if __name__ == "__main__":
    main()
