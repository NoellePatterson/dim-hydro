import os
import numpy as np
import pandas as pd
import matplotlib
from datetime import datetime
from utils.helpers import remove_offset_from_julian_date
import matplotlib.pyplot as plt
from utils.helpers import is_multiple_date_data, find_index
from utils.matrix_convert import convert_raw_data_to_matrix
from utils.calc_all_year import calculate_average_each_column
from pre_processFiles.gauge_reference import gauge_reference

np.warnings.filterwarnings('ignore')

"""Note: this script will not work for running all gages at once (use plotter_indiv function, #2)"""

def dim_hydrograph_plotter_agg(start_date, directory_name, end_with, class_number, gauge_numbers, plot):
    aggregate_matrix = np.zeros((366, 7)) # change to 5 for matrix without min/max
    counter = 0
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
                            aggregate_matrix = np.add(aggregate_matrix, _getAggMatrix(flow_matrix))
                            counter = counter + 1

                    elif int(fixed_df.iloc[0, current_gauge_column_index]) == int(class_number):
                        current_gauge_class, current_gauge_number, year_ranges, flow_matrix, julian_dates = convert_raw_data_to_matrix(fixed_df, current_gauge_column_index, start_date)
                        start_year_index = find_index(year_ranges, int(gauge_reference[int(current_gauge_number)]['start']))
                        end_year_index = find_index(year_ranges, int(gauge_reference[int(current_gauge_number)]['end']))
                        flow_matrix = flow_matrix[:,start_year_index:end_year_index]
                        aggregate_matrix = np.add(aggregate_matrix, _getAggMatrix(flow_matrix))
                        counter = counter + 1

                    current_gauge_column_index = current_gauge_column_index + step

        final_aggregate = aggregate_matrix/counter

        if class_number:
            np.savetxt("post_processedFiles/Hydrographs/Class_{}_aggregate.csv".format(int(current_gauge_class)), final_aggregate, delimiter=",", fmt="%s")
        else:
            np.savetxt("post_processedFiles/Hydrographs/plot_data_{}.csv".format(int(current_gauge_number)), final_aggregate, delimiter=",", fmt="%s")

        """To output plot, uncomment line below"""
        _plotter(final_aggregate, start_date)

def _getAggMatrix(flow_matrix):

    average_annual_flow = calculate_average_each_column(flow_matrix)

    number_of_rows = len(flow_matrix)
    number_of_columns = len(flow_matrix[0,:])
    normalized_matrix = np.zeros((number_of_rows, number_of_columns))
    percentiles = np.zeros((number_of_rows, 7))

    for row_index, row_data in enumerate(flow_matrix[:,0]):
        for column_index, column_data in enumerate(flow_matrix[row_index, :]):
            normalized_matrix[row_index,column_index] = flow_matrix[row_index,column_index]/average_annual_flow[column_index]

        percentiles[row_index,0] = np.nanpercentile(normalized_matrix[row_index,:], 10)
        percentiles[row_index,1] = np.nanpercentile(normalized_matrix[row_index,:], 25)
        percentiles[row_index,2] = np.nanpercentile(normalized_matrix[row_index,:], 50)
        percentiles[row_index,3] = np.nanpercentile(normalized_matrix[row_index,:], 75)
        percentiles[row_index,4] = np.nanpercentile(normalized_matrix[row_index,:], 90)
        percentiles[row_index,5] = np.nanmin(normalized_matrix[row_index,:]) # comment out to remove min line
        percentiles[row_index,6] = np.nanmax(normalized_matrix[row_index,:]) # comment out to remove max line

    return percentiles

def _plotter(aggregate_matrix, start_date):
    # def format_func(value, tick_number):
    #     julian_start_date = datetime.strptime("{}/2001".format(start_date), "%m/%d/%Y").timetuple().tm_yday
    #     return int(remove_offset_from_julian_date(value, julian_start_date))
    """Dimensionless Hydrograph Plotter"""

    fig = plt.figure('aggregate_matrix')
    ax = plt.subplot(111)
    plt.subplots_adjust(bottom = .15)
    #ax.xaxis.set_major_formatter(plt.FuncFormatter(format_func))
    x = np.arange(0,366,1)
    plt.grid(which = 'major', linestyle = '-', axis = 'y')
    perc10 = ax.plot(aggregate_matrix[:,0], color = 'navy', label = "10%")
    perc25 = ax.plot(aggregate_matrix[:,1], color = 'blue', label = "25%")
    perc50 = ax.plot(aggregate_matrix[:,2], color = 'red', label = "50%")
    perc75 = ax.plot(aggregate_matrix[:,3], color = 'blue', label = "75%")
    perc90 = ax.plot(aggregate_matrix[:,4], color = 'navy', label = "90%")
    min_lin = ax.plot(aggregate_matrix[:,5], color = 'black', label = 'min', lw=1)
    max_lin = ax.plot(aggregate_matrix[:,6], color = 'black', label = 'max', lw=1)
    ax.fill_between(x, aggregate_matrix[:,0], aggregate_matrix[:,1], color = 'powderblue')
    ax.fill_between(x, aggregate_matrix[:,1], aggregate_matrix[:,2], color = 'powderblue')
    ax.fill_between(x, aggregate_matrix[:,2], aggregate_matrix[:,3], color = 'powderblue')
    ax.fill_between(x, aggregate_matrix[:,3], aggregate_matrix[:,4], color = 'powderblue')
    box = ax.get_position('aggregate_matrix')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, ncol=7, borderaxespad = .9, fontsize='small', labelspacing=.2, columnspacing=1, markerscale=.5)

    #plt.title("High Elevation Low Precipitation")
    #plt.xlabel("Julian Date")
    plt.ylabel("Daily Flow/Average Annual Flow")

    ax = plt.gca()
    tick_spacing = [0, 30.5, 61, 91.5, 122, 152.5, 183, 213.5, 244, 274.5, 305, 335.5]
    tick_labels = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
    plt.xticks(tick_spacing, tick_labels)
    #ax.set_xticks(tick_spacing)
    #tick_labels = label_xaxis[tick_spacing]
    #ax.set_xticklabels(tick_labels)

    plt.grid(which = 'major', linestyle = '-', axis = 'y')

    plt.savefig("post_processedFiles/Hydrographs/dim_hydro_aggregate.png")
