from preprocess.preprocessor import Preprocessor
from data_loader.data_loader import DataLoader


class Generator:
    def __init__(self, config):
        self.config = config
        self.reviews_data_loader = DataLoader(config.reviews.raw_data_path)
        self.profiles_data_loader = DataLoader(config.profiles.raw_data_path)
        self.reviews_data = None
        self.profiles_data = None
        self.preprocessor = None

    def load_data(self):
        self.reviews_data = self.get_reviews_data()
        self.profiles_data = self.get_profiles_data()

    def load_preprocessor(self):
        self.preprocessor = Preprocessor(self.config, self.reviews_data, self.profiles_data)

    def preprocess_data(self):
        self.reviews_data = self.preprocessor.preprocess_reviews()
        self.profiles_data = self.preprocessor.preprocess_profiles()

    def get_reviews_data(self):
        self.reviews_data_loader.load_data()
        return self.reviews_data_loader.get_data()

    def get_profiles_data(self):
        self.profiles_data_loader.load_data()
        return self.profiles_data_loader.get_data()

    def save(self):
        self.reviews_data.to_csv(self.config.reviews.save_data_path, index=False)
        self.profiles_data.to_csv(self.config.profiles.save_data_path, index=False)