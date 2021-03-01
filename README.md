[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

## About The Project

This project is motivated to provide a useful alternative Path object.

### Built With

- [poetry](https://python-poetry.org/)

## Getting Started

```sh
$ pip install paaaaath
$ python -c "from paaaaath import Path; print(Path('https://raw.githubusercontent.com/ar90n/paaaaath/main/assets/python_logo.txt').read_text())"
                   _.gj8888888lkoz.,_
                d888888888888888888888b,
               j88P""V8888888888888888888
               888    8888888888888888888
               888baed8888888888888888888
               88888888888888888888888888
                            8888888888888
    ,ad8888888888888888888888888888888888  888888be,
   d8888888888888888888888888888888888888  888888888b,
  d88888888888888888888888888888888888888  8888888888b,
 j888888888888888888888888888888888888888  88888888888p,
j888888888888888888888888888888888888888'  8888888888888
8888888888888888888888888888888888888^"   ,8888888888888
88888888888888^'                        .d88888888888888
8888888888888"   .a8888888888888888888888888888888888888
8888888888888  ,888888888888888888888888888888888888888^
^888888888888  888888888888888888888888888888888888888^
 V88888888888  88888888888888888888888888888888888888Y
  V8888888888  8888888888888888888888888888888888888Y
   `"^8888888  8888888888888888888888888888888888^"'
               8888888888888
               88888888888888888888888888
               8888888888888888888P""V888
               8888888888888888888    888
               8888888888888888888baed88V
                `^888888888888888888888^
                  `'"^^V888888888V^^'
```

### Prerequisites

If you rune some codes in this repository, you have to install poetry as following.

```sh
pip install poetry
```

### Installation

```sh
pip install paaaaath
```

## Usage

```python
from paaaaath import Path

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
```

## Featuers
| | HttpPath | S3Path| GCSPath |
| :-------------: | :-------------: | :-------------: | :-------------: |
| open | ✅ | ✅ | ✅ |
| read_text | ✅ | ✅ | ✅ |
| read_byte | ✅ | ✅ | ✅ |
| write_text | ❌ | ✅ | ✅ |
| write_byte | ❌ | ✅ | ✅ |
| iterdir | ❌ | ✅ | ✅ |
| touch | ❌ | ✅ | ✅ |
| mkdir | ❌ | ✅ | ✅ |
| exists | ❌ | ✅ | ✅ |


## Roadmap

See the [open issues](https://github.com/ar90n/paaaaath/issues) for a list of proposed features (and known issues).

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Masahiro Wada - [@ar90n](https://twitter.com/ar90n) - argon.argon.argon@gmail.com

Project Link: [https://github.com/ar90n/paaaaath](https://github.com/ar90n/paaaaath)

## Acknowledgements

- [smart-open](https://pypi.org/project/smart-open/)
- [Python Logo](https://ascii.matthewbarber.io/art/python/)

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/ar90n/paaaaath.svg?style=for-the-badge
[contributors-url]: https://github.com/ar90n/paaaaath/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/ar90n/paaaaath.svg?style=for-the-badge
[forks-url]: https://github.com/ar90n/paaaaath/network/members
[stars-shield]: https://img.shields.io/github/stars/ar90n/paaaaath.svg?style=for-the-badge
[stars-url]: https://github.com/ar90n/paaaaath/stargazers
[issues-shield]: https://img.shields.io/github/issues/ar90n/paaaaath.svg?style=for-the-badge
[issues-url]: https://github.com/ar90n/paaaaath/issues
[license-shield]: https://img.shields.io/github/license/ar90n/paaaaath.svg?style=for-the-badge
[license-url]: https://github.com/ar90n/paaaaath/blob/master/LICENSE.txt
