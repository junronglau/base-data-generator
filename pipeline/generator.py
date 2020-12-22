from data_loader.data_loader import DataLoader
from preprocess.preprocessor import Preprocessor


class Generator:
    def __init__(self, config):
        self.config = config
        self.reviews_data_loader = DataLoader(config.reviews.raw_data_path)
        self.profiles_data_loader = DataLoader(config.profiles.raw_data_path)
        self.products_data_loader = DataLoader(config.products.raw_data_path)
        self.reviews_data = None
        self.profiles_data = None
        self.products_data = None
        self.preprocessor = None

    def load_data(self):
        self.reviews_data = self.get_reviews_data()
        self.profiles_data = self.get_profiles_data()
        self.products_data = self.get_products_data()

    def load_preprocessor(self):
        self.preprocessor = Preprocessor(self.config, self.reviews_data, self.profiles_data,self.products_data)

    def preprocess_reviews(self):
        self.reviews_data = self.preprocessor.preprocess_reviews()

    def preprocess_profiles(self):
        self.profiles_data = self.preprocessor.preprocess_profiles()
    
    def preprocess_products(self):
        self.products_data = self.preprocessor.preprocess_products()

    def get_reviews_data(self):
        self.reviews_data_loader.load_data()
        return self.reviews_data_loader.get_data()

    def get_profiles_data(self):
        self.profiles_data_loader.load_data()
        return self.profiles_data_loader.get_data()
    
    def get_products_data(self):
        self.products_data_loader.load_data()
        return self.products_data_loader.get_data()

    def save(self):
        self.reviews_data.to_csv(self.config.reviews.save_data_path, index=False)
        self.profiles_data.to_csv(self.config.profiles.save_data_path, index=False)
        self.products_data.to_csv(self.config.products.save_data_path, index=False)