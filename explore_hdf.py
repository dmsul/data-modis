from pyhdf.SD import SD, SDC


if __name__ == '__main__':
    FILE_NAME = '../data/src/2000/55/MOD04_3K.A2000055.0005.hdf'

    hdf = SD(FILE_NAME, SDC.READ)
    dataset_names = hdf.datasets().keys()
    for name in dataset_names:
        this_dataset = hdf.select(name)
        print(name)
        print(this_dataset.attributes()['long_name'])
        print('\n')
