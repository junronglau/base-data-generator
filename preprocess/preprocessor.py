class Preprocessor:
    def __init__(self, reviews_df, profiles_df):
        self.reviews_df = reviews_df
        self.profiles_df = profiles_df

    def keep_english(self):
        self.reviews_df = self.reviews_df[self.reviews_df['language'] == 'English']

    def preprocess_text(self):
        pass