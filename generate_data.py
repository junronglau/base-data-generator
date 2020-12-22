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
    except ValueError:
        print("Missing or invalid arguments")
        exit(0)
    dataset = args.dataset

    print('Creating the data generator...')
    data_generator = Generator(config)

    print('Loading the Data and Preprocessor...')

    data_generator.load_data()
    data_generator.load_preprocessor()

    print('Preprocessing data..')
    if dataset in ['all', 'reviews']:
        print('Preprocessing reviews dataset...')
        data_generator.preprocess_reviews()

        print('Saving the generated reviews dataset...')
        data_generator.save_reviews_data()
    if dataset in ['all', 'profiles']:
        print('Preprocessing profiles dataset...')
        data_generator.preprocess_profiles()

        print('Saving the generated profiles dataset...')
        data_generator.save_profiles_data()
    if dataset in ['all', 'products']:
        print('Preprocessing products dataset...')
        data_generator.preprocess_products()

        print('Saving the generated products dataset...')
        data_generator.save_products_data()

    print('Generated datasets are saved...')

if __name__ == '__main__':
    generate()




