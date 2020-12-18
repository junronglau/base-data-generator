# Base Dataset Generator 
[![Maintainability](https://api.codeclimate.com/v1/badges/a99a88d28ad37a79dbf6/maintainability)](https://codeclimate.com/github/codeclimate/codeclimate/maintainability) [![Python 3.6](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/) [![dvc](https://camo.githubusercontent.com/6447c3e192a6a3cb9f9fd54c6af3cfc498494dc95753a9a587a520299483d935/68747470733a2f2f736e617063726166742e696f2f2f6476632f62616467652e737667)](https://snapcraft.io/dvc) [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This repo is to help us track the changes and preprocessing methods.
We refer this dataset as the base dataset because it performs common, basic preprocessing methods which can then be further
processed in our independent use cases. This repo will also enforce data version control using [DVC](https://github.com/iterative/dvc), 
and allows easy retrieval of the base dataset as long as you have access to the remote server `instance-janellah`.

This allows dataset standardization, and a single source of truth across our use cases. We can also easily reproduce 
this pipeline with other datasets in the future.


# File directory

```
.
├── data/                               # Stores data for preprocessing
│   ├── base/   
│   │   ├── consolidated_profiles.csv
│   │   └── consolidated_products.txt
│   │
│   ├── raw/
│   │   ├── consolidated_profiles.csv
│   │   └── consolidated_products.txt
│   │
│   └── preprocessing/
│       ├── contractions.txt
│       └── slangs.txt
│
├── configs/                            # Stores configuration files for pipeline 
│   └── config.json
│
├── installation/                       # Required installation files 
│   ├── environment.yml  
│   └── install.sh
│
├── data_loader/                        # DataLoader class to load data from files
│   └── data_loader.py
│
├── preprocess/                         # Preprocessor class for preprocessing and cleaning steps
│   └── preprocessor.py
│
├── pipeline/                           # Generator class to load all methods and classes required 
│   └── generator.py
│
├── utils/                              # Cleaning and processing functions
│
├── notebooks/     
│
└── generate_data.py                    # Controls the flow of the process
```

# Datasets

## Input
The input data will be generated from the data extraction repo [here](https://github.com/fatberryz/FYP_UC1), which retrieves both reviews and profiles dataset from amazon. 
The format is listed below, and should be placed in the `./data/raw` folder

### Reviews

| stars              | profile_name | profile_link                                           | profile_image                                                                                | title          | date                                               | style           | verified          | comment                                                  | voting                        | review_images | ASIN       |
|--------------------|--------------|--------------------------------------------------------|----------------------------------------------------------------------------------------------|----------------|----------------------------------------------------|-----------------|-------------------|----------------------------------------------------------|-------------------------------|---------------|------------|
| 5.0 out of 5 stars | Willow       | /gp/profile/amzn1.account.AHR5T6MM2O3EPWKQS2TBOVXBXLQA | https://images-na.ssl-images-amazon.com/images/S/amazon-avatars-global/e783dd3d-..-SX48_.jpg | Love love love | Reviewed in the United States on December 11, 2019 | Size: 1.7 Ounce | Verified Purchase | Love, love, love this moisturizer! As a woman who has... | One person found this helpful | 0             | B01M09QQI0 |

### Profiles

| json_data                                                               | acc_num                  | name    | occupation | location | description                | badges | ranking |
|-------------------------------------------------------------------------|--------------------------|---------|------------|----------|----------------------------|--------|---------|
| {'marketplaceId': xxx, 'locale': xxx, 'contributions': [{'id': ....}] } | AE25VHDU4KBY2EIVKGZCEG2A | JD Hart | Retired    | USA      | fitness instructor, writer | null   | 887548  |


## Output

### Reviews
On top of existing columns, 13 new ones are added:

- new_profile_link
- clean_title
- decoded_comment
- ratings
- clean_verified
- account_number
- clean_voting
- location
- date_posted
- poly_obj
- language
- language_confidence
- cleaned_text

### Profiles
On top of existing columns, 4 new ones are added:
- deleted_status
- reviewer_contributions
- marketplace_id
- locale


# Installation

Give permissions and run the installation script
```
chmod +x installation/install.sh
installation/install.sh
```

### Troubleshooting
If you are on windows, you may experience difficulties installing polygot. Follow these steps to install instead
```
https://github.com/aboSamoor/polyglot/issues/127#issuecomment-492604421
```

# Usage

Activate the conda environment
```
conda activate dvc
```

To view the list of available arguments
```
python generate_data.py -h
```

Specify your data paths in `configs/config.json` and generate all datasets (reviews, profiles)
```
python generate_data.py -d all
```

After dataset has been generated, we can register the changes with DVC
```
dvc add data/raw data/base
git add data/raw.dvc data/base.dvc
git commit -m "Generated base dataset"
dvc push
git push origin master
```

To access this version of dataset outside of this project (requires access to remote server `instance-janellah`)
```
dvc get https://github.com/junronglau/base-data-generator data
```


# TODO
- Add script to pull latest set of data from ryan's database
- add Delin's amazon checklist cleaning functions
- Tag a release + changelog after confirmation with hongliang
