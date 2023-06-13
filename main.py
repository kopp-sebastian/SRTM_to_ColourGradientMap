import os
import tempfile
import concurrent.futures
import matplotlib.pyplot as plt
import matplotlib as mpl
import rasterio
from rasterio.merge import merge


def process_srtm(file):
    with rasterio.open(file) as src:
        data = src.read(1)
        profile = src.profile

    temp_file = tempfile.mktemp(suffix='.tif')

    with rasterio.open(temp_file, 'w', **profile) as dest:
        dest.write(data, 1)

    return temp_file


def main():
    # PUT YOUR FILES HERE
    srtm_files = ["srtm_39_02.asc", "srtm_39_03.asc"]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(process_srtm, srtm_files))

    # Define color ranges
    colors = [(0, 'blue'), (30/2300, 'darkgreen'), (50/2300, 'green'),
              (200/2300, 'lightgreen'), (230/2300, 'yellow'), (1000/2300, 'red'),
              (1400/2300, 'brown'), (1800/2300, 'grey'), (1, 'white')]

    # Convert your data range to a normalized range for the colormap
    cmap_norm = mpl.colors.Normalize(vmin=0, vmax=2300)
    cmap = mpl.colors.LinearSegmentedColormap.from_list("", colors)
    cmap.set_under('white')  # Color for values under vmin

    # Open the temp files as datasets and merge them
    datasets = [rasterio.open(temp_file) for temp_file in results]
    mosaic, out_trans = merge(datasets)

    # Close the datasets and remove temp files after merging
    for ds, temp_file in zip(datasets, results):
        ds.close()
        os.remove(temp_file)

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(20, 10))

    # Display image using the normalizer
    im = ax.imshow(mosaic[0], cmap=cmap, norm=cmap_norm)

    # Colorbar
    # cbar = fig.colorbar(im, orientation='horizontal', pad=0.03)
    # cbar.set_label('Elevation (m)')

    # Labels and title
    # ax.set_xlabel('Longitude')
    # ax.set_ylabel('Latitude')
    # ax.set_title('Elevation Map')

    # Save figure
    plt.axis('off')
    plt.savefig('color_map.png', dpi=100, bbox_inches='tight', pad_inches=0)
    print('Done')


if __name__ == '__main__':
    main()
