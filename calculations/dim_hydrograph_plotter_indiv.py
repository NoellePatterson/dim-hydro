import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
from utils.helpers import remove_offset_from_julian_date
from pre_processFiles.gauge_reference import gauge_reference
from utils.helpers import is_multiple_date_data, find_index
from utils.matrix_convert import convert_raw_data_to_matrix
from utils.calc_all_year import calculate_average_each_column
matplotlib.use('Agg')


np.warnings.filterwarnings('ignore')

def dim_hydrograph_plotter_indiv(start_date, directory_name, end_with, class_number, gauge_numbers, plot):
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
                            start_year_index = find_index(year_ranges, int(gauge_reference[int(current_gauge_number)]['start']))
                            end_year_index = find_index(year_ranges, int(gauge_reference[int(current_gauge_number)]['end']))
                            flow_matrix = flow_matrix[:,start_year_index:end_year_index]

                            _plotter(flow_matrix, julian_dates, current_gauge_number, plot, current_gauge_class, start_date)

                    elif not class_number and not gauge_numbers:
                        current_gauge_class, current_gauge_number, year_ranges, flow_matrix, julian_dates = convert_raw_data_to_matrix(fixed_df, current_gauge_column_index, start_date)
                        start_year_index = find_index(year_ranges, int(gauge_reference[int(current_gauge_number)]['start']))
                        end_year_index = find_index(year_ranges, int(gauge_reference[int(current_gauge_number)]['end']))
                        flow_matrix = flow_matrix[:,start_year_index:end_year_index]

                        _plotter(flow_matrix, julian_dates, current_gauge_number, plot, current_gauge_class, start_date)

                    elif int(fixed_df.iloc[0, current_gauge_column_index]) == int(class_number):
                        current_gauge_class, current_gauge_number, year_ranges, flow_matrix, julian_dates = convert_raw_data_to_matrix(fixed_df, current_gauge_column_index, start_date)
                        start_year_index = find_index(year_ranges, int(gauge_reference[int(current_gauge_number)]['start']))
                        end_year_index = find_index(year_ranges, int(gauge_reference[int(current_gauge_number)]['end']))
                        flow_matrix = flow_matrix[:,start_year_index:end_year_index]

                        _plotter(flow_matrix, julian_dates, current_gauge_number, plot, current_gauge_class, start_date)

                    current_gauge_column_index = current_gauge_column_index + step


def _plotter(flow_matrix, julian_dates, current_gauge_number, plot, current_gauge_class, start_date):
    def format_func(value, tick_number):
        julian_start_date = datetime.strptime("{}/2001".format(start_date), "%m/%d/%Y").timetuple().tm_yday
        return int(remove_offset_from_julian_date(value, julian_start_date))
    fig = plt.figure('aggregate_matrix')
    ax = plt.subplot(111)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(format_func))
    x = np.arange(0,366,1)

    """Dimensionless Hydrograph Plotter"""
    average_annual_flow = calculate_average_each_column(flow_matrix)
    number_of_rows = len(flow_matrix)
    number_of_columns = len(flow_matrix[0,:])
    normalized_matrix = np.zeros((number_of_rows, number_of_columns))
    percentiles = np.zeros((number_of_rows, 5))

    for row_index, row_data in enumerate(flow_matrix[:,0]):
        for column_index, column_data in enumerate(flow_matrix[row_index, :]):
            normalized_matrix[row_index,column_index] = flow_matrix[row_index,column_index]/average_annual_flow[column_index]

        percentiles[row_index,0] = np.nanpercentile(normalized_matrix[row_index,:], 10)
        percentiles[row_index,1] = np.nanpercentile(normalized_matrix[row_index,:], 25)
        percentiles[row_index,2] = np.nanpercentile(normalized_matrix[row_index,:], 50)
        percentiles[row_index,3] = np.nanpercentile(normalized_matrix[row_index,:], 75)
        percentiles[row_index,4] = np.nanpercentile(normalized_matrix[row_index,:], 90)

    # percentiles = percentiles.transpose()
    # np.savetxt("post_processedFiles/Class-{}/plot_data_{}.csv".format(int(current_gauge_class), int(current_gauge_number)), percentiles, delimiter=",", fmt="%s")

    """Dimensionless Hydrograph Plotter"""

    fig = plt.figure('hydrograph')
    ax = plt.subplot(111)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(format_func))
    x = np.arange(0,366,1)
    plt.grid(which = 'major', linestyle = '-', axis = 'y')
    perc10 = ax.plot(percentiles[:,0], color = 'navy', label = "10%")
    perc25 = ax.plot(percentiles[:,1], color = 'blue', label = "25%")
    perc50 = ax.plot(percentiles[:,2], color = 'red', label = "50%")
    perc75 = ax.plot(percentiles[:,3], color = 'blue', label = "75%")
    perc90 = ax.plot(percentiles[:,4], color = 'navy', label = "90%")
    ax.fill_between(x, percentiles[:,0], percentiles[:,1], color = 'powderblue')
    ax.fill_between(x, percentiles[:,1], percentiles[:,2], color = 'powderblue')
    ax.fill_between(x, percentiles[:,2], percentiles[:,3], color = 'powderblue')
    ax.fill_between(x, percentiles[:,3], percentiles[:,4], color = 'powderblue')
    box = ax.get_position('hydrograph')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, ncol=5)
    plt.tight_layout()

    plt.title("Dimensionless Hydrograph")
    plt.xlabel("Julian Date")
    plt.ylabel("Daily Flow/Average Annual Flow")

    plt.grid(which = 'major', linestyle = '-', axis = 'y')

    if plot:
        plt.savefig("post_processedFiles/Hydrographs/{}.png".format(int(current_gauge_number)))
