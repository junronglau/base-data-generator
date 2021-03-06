from utils.reformat import reformat_profiles_df, reformat_reviews_df, reformat_products_df


class Preprocessor:
    def __init__(self, config, reviews_df, profiles_df,products_df):
        self.config = config
        self.reviews_df = reviews_df
        self.profiles_df = profiles_df
        self.products_df = products_df

    def preprocess_reviews(self):
        self.reviews_df = reformat_reviews_df(self.reviews_df,
                                              self.config.preprocessing.contractions_path,
                                              self.config.preprocessing.slangs_path)
        return self.reviews_df

    def preprocess_profiles(self):
        self.profiles_df = reformat_profiles_df(self.profiles_df)
        return self.profiles_df

    def preprocess_products(self):
        self.products_df = reformat_products_df(self.products_df,
                                                self.config.preprocessing.contractions_path,
                                                self.config.preprocessing.slangs_path)
        return self.products_df
