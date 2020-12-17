# Overview
This repo is to help us track the changes and preprocessing methods.
We refer this dataset as the base dataset because it performs common, basic preprocessing methods which can then be further
processed in our independent use cases. Currently, our files are stored in Google Drive. In the future, if we need to shift to a cloud bucket, it will make the
process easy.

This allows standardization and reproducibility across our use cases.

# Pre-requisites
TODO: give format of input data

# File directory

```
.
├── data/                         # Stores data for training/testing
│   ├── train/   
│   │   ├── labels.csv
│   │   └── generated_labels.txt
│   ├── test/
│   │   ├── labels.csv
│   │   └── generated_labels.txt
│   ├── label_map.txt
│   └── label_map_tfite.txt
│
├── data_loader/                  # Generate required data format from csv 
│   ├── create_tfrecord.py
│   └── generate_labels.py
```

# Installation

Give permissions and run the installation script
```
chmod +x installation/install.sh
installation/install.sh
```

### Troubleshooting
If you are on windows, you may experience difficulties installing polygot. Follow listed steps to install instead
```
https://github.com/aboSamoor/polyglot/issues/127
```

# Usage



# ToDo
- Add script to pull latest set of data from ryan's database
- add delin's amazon chcklist
- clean up codes (pep8)
- diffferent modes - choose dataset to run

-changes: unparsed contributions in the json_data and no more amazon checklist since delin will have a seperate scraping for that,
also, different parsing method for the json_data
- also, we dont merge the 2 files tgt. When doing your own analysis, then you can join the tables if not it is unnecessary because we have 89k reviews, but 65k users. So means there should be users who reviewed more than 1 loreal product
