import pandas as pd


def mean_df_resample(df: pd.DataFrame):
    df.set_index('timestamp', inplace=True)
    df.drop('user_id', axis=1, inplace=True)
    df_resampled = df.resample('1T').mean()
    return df_resampled
