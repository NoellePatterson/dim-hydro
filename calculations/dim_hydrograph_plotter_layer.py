import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from utils.helpers import is_multiple_date_data
from utils.matrix_convert import convert_raw_data_to_matrix
from utils.calc_all_year import calculate_average_each_column
matplotlib.use('Agg')

np.warnings.filterwarnings('ignore')

def dim_hydrograph_plotter_layer(start_date, directory_name, end_with, class_number, gauge_numbers, plot):
    for root,dirs,files in os.walk(directory_name):
        for file in files:
            if file.endswith(end_with):
                fixed_df = pd.read_csv('{}/{}'.format(directory_name, file), sep=',', encoding='latin1', dayfirst=False, header=None).dropna(axis=1, how='all')
                step = is_multiple_date_data(fixed_df);

                current_gauge_column_index = 1

                while current_gauge_column_index <= (len(fixed_df.iloc[1,:]) - 1):
                    if gauge_numbers:
                        if int(fixed_df.iloc[1, current_gauge_column_index]) in gauge_numbers:
                            current_gauge_class, current_gauge_number, year_ranges, flow_matrix, julian_dates = convert_raw_data_to_matrix(fixed_df, current_gauge_column_index, start_date)

                            _plotter(flow_matrix, julian_dates, current_gauge_number, plot)

                    elif not class_number and not gauge_numbers:
                        current_gauge_class, current_gauge_number, year_ranges, flow_matrix, julian_dates = convert_raw_data_to_matrix(fixed_df, current_gauge_column_index, start_date)

                        _plotter(flow_matrix, julian_dates, current_gauge_number, plot)
                    elif int(fixed_df.iloc[0, current_gauge_column_index]) == int(class_number):
                        current_gauge_class, current_gauge_number, year_ranges, flow_matrix, julian_dates = convert_raw_data_to_matrix(fixed_df, current_gauge_column_index, start_date)

                        _plotter(flow_matrix, julian_dates, current_gauge_number, plot)

                    current_gauge_column_index = current_gauge_column_index + step


def _plotter(flow_matrix, julian_dates, current_gauge_number, plot):

    """Dimensionless Hydrograph Plotter"""
    average_annual_flow = calculate_average_each_column(flow_matrix)
    number_of_rows = len(flow_matrix)
    number_of_columns = len(flow_matrix[0,:])
    normalized_matrix = np.zeros((number_of_rows, number_of_columns))
    percentiles = np.zeros((number_of_rows, 3))

    for row_index, row_data in enumerate(flow_matrix[:,0]):
        for column_index, column_data in enumerate(flow_matrix[row_index, :]):
            normalized_matrix[row_index,column_index] = flow_matrix[row_index,column_index]/average_annual_flow[column_index]

        percentiles[row_index,0] = np.nanpercentile(normalized_matrix[row_index,:], 25)
        percentiles[row_index,1] = np.nanpercentile(normalized_matrix[row_index,:], 50)
        percentiles[row_index,2] = np.nanpercentile(normalized_matrix[row_index,:], 75)

    x = np.arange(0,366,1)
    label_xaxis = np.array(julian_dates[0:366])

    plt.figure('dimensionles hydrograph')
    plt.plot(percentiles[:,0], color = 'blue')
    plt.plot(percentiles[:,1], color = 'red')
    plt.plot(percentiles[:,2], color = 'blue')

    plt.fill_between(x, percentiles[:,0], percentiles[:,1], color = 'powderblue')
    plt.fill_between(x, percentiles[:,1], percentiles[:,2], color = 'powderblue')
    plt.title("Dimensionless Hydrograph")
    plt.xlabel("Julian Date")
    plt.ylabel("Daily Flow/Average Annual Flow")
    plt.grid(which = 'major', linestyle = '-', axis = 'y')
    ax = plt.gca()
    tick_spacing = [0, 50, 100, 150, 200, 250, 300, 350]
    ax.set_xticks(tick_spacing)
    tick_labels = label_xaxis[tick_spacing]
    ax.set_xticklabels(tick_labels)
    plt.savefig("post_processedFiles/Hydrographs/dim_hydro_layered.png")
