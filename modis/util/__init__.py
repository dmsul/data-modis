from clean.raw import load_modis_year


def annual_mean(year, spatial_index=None):
    df = load_modis_year(2000)
    quarter = (df['time'].dt.month - 1) // 3 + 1
    quarter_mean = df.groupby(quarter)['aod'].mean()

#    if spatial_index is not None:
#       annual_mean = quarter_mean.groupby(spatial_index).mean()
#    else:
    annual_mean = quarter_mean.mean()

    return annual_mean


if __name__ == '__main__':
    annual_mean(2000)
