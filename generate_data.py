"""
This script loads the required files, preprocesses it, and saves in a directory.
"""
from utils.config import process_config
from utils.utils import get_args
from pipeline.generator import Generator

def generate():
    # capture the config path from the run arguments
    # then process the json configuration file
    try:
        args = get_args()
        config = process_config(args.config)
    except:
        print("missing or invalid arguments")
        exit(0)

    print('Creating the data generator...')
    data_generator = Generator(config)

    print('Loading the Data and Preprocessor...')

    data_generator.load_data()
    data_generator.load_preprocessor()

    print('Preprocessing data..')
    data_generator.preprocess_data()

    print('Saving the generated dataframes...')
    data_generator.save()

if __name__ == '__main__':
    generate()




