# DigiCon: OpenSoft 2018 project

DigiCon is LBS hall's gold winning submission for OpenSoft 2018.
![DigiCon logo](assets/logo.png "Digicon Logo")

## Usage

### Requirements

- Docker

### Setup

- TODO: Add setup instructions

## Problem Statement

> "Medicinal prescriptions are still widely written by hand by doctors, but imperfect handwriting results in a lot of mistakes with the prescription, sometimes even resulting in severe cases like deaths. Can we use technology to solve this problem?"

You can view the full problem statement [here](PS.pdf).

## Solution overview

DigiCon provides a solution to the age old problem of reading doctors’ prescriptions by providing a web and mobile interface that both pharmacists and patients can easily use to read the prescriptions.

The solution works for any image, in any orientation, scanned even with a mobile camera. It detects all bounding boxes surrounding only the text in the image and satisfactorily return the parsed text that is spell corrected with both English and medical vocabulary. The system can extract information regarding the medical aspects mentioned in the text, the exact dosages of the drugs prescribed, the names of the doctor, the hospital, date of prescription, along with other named entities in the text. The end user can view and download the corrected text in both image and pdf formats, with the text either smartly overlaid on the original handwriting or on a fresh sheet entirely.

## License

[GPLv3](LICENSE)
