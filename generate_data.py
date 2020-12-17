"""
This script loads the required files, preprocesses it, and saves in a directory.
"""
from utils.config import process_config
from utils.utils import get_args


def clean():
    # capture the config path from the run arguments
    # then process the json configuration file
    try:
        args = get_args()
        config = process_config(args.config)
    except:
        print("missing or invalid arguments")
        exit(0)

    print('Creating the data generators.')
    reviews_data_loader = ReviewsDataLoader(config)
    profiles_data_loader = ProfilesDataLoader(config)

    print('Creating the Preprocessor.')
    preprocessor = Preprocessor(reviews_data_loader.df, profiles_data_loader.df)

    print('Preprocessing data..')
    preprocessor.preprocess_all()

    reviews_data_loader.save()
    profiles_data_loader.save()

    generate_basic_stats()

def __init__():
    pass




