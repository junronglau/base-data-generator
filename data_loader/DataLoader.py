import pandas as pd


class DataLoader:
    def __init__(self, config):
        self.df = self.load_data(config.reviews.raw_data_path)

    @staticmethod
    def load_data(path):
        df = pd.read_csv(path, encoding='utf-8')
        return df

    def save_data(self, path):
        self.df.to_csv(path, index=False)

    def get_data(self):
        return self.df
