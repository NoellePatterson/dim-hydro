from utils.helpers import create_folders, get_calculation_numbers
from calculations.dim_hydrograph_plotter_aggregate import dim_hydrograph_plotter_agg
from calculations.dim_hydrograph_plotter_indiv import dim_hydrograph_plotter_indiv
from calculations.dim_hydrograph_plotter_layer import dim_hydrograph_plotter_layer

directory_name = 'rawFiles'
end_with = '.csv'

create_folders()
calculation_number, start_date, class_number, gauge_numbers = get_calculation_numbers()

if calculation_number == 1:
    print('Plotting aggregate dimensionless reference hydrograph with start date at {} in {} directory'.format(start_date, directory_name))
    dim_hydrograph_plotter_agg(start_date, directory_name, end_with, class_number, gauge_numbers, True)
elif calculation_number == 2:
    print('Plotting individual dimensionless reference hydrographs with start date at {} in {} directory'.format(start_date, directory_name))
    dim_hydrograph_plotter_indiv(start_date, directory_name, end_with, class_number, gauge_numbers, True)
elif calculation_number == 3:
    print('Plotting layered dimensionless reference hydrographs with start date at {} in {} directory'.format(start_date, directory_name))
    dim_hydrograph_plotter_layer(start_date, directory_name, end_with, class_number, gauge_numbers, True)

print('')
print('Done!!!!!!!!!!!!!!!!')
