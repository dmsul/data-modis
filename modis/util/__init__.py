def annual_mean(df, spatial_index=None):
    quarter = (df['time'].dt.month - 1) // 3 + 1
    quarter_mean = df.groupby(quarter)['aod'].mean()

#    if spatial_index is not None:
#       annual_mean = quarter_mean.groupby(spatial_index).mean()
#    else:
    annual_mean = quarter_mean.mean()

    return annual_mean
