
def loadvectors(filename):
    """
    Given the path to a CSV file with column headers, loads the file and returns
    a dict of lists, where the dict keys are the column headers and each
    corresponding value is a list with the data from that column. """
    import csv
    # the Python csv library does the hard work for us
    reader = csv.DictReader(open(filename), skipinitialspace=True)
    d = dict() # Start with an empty dictionary
    for row in reader: # The reader will give us a dictionary for every line in the file
        for key,val in row.items(): # Iterate through the keys in the dictionary for this row
            if key in d: # If we've already got this key,
                d[key].append(float(val)) # just add the item to the end of the corresponding list
            else: # Otherwise,
                d[key] = [float(val)] # Create a new list with just this one element
    return d # Finally, return the completed dictionary

power = loadvectors('first_steak_power.csv')
temp = loadvectors('first_steak_temp.csv')

import matplotlib.pyplot as plt
import numpy as np

temp_time = np.array(temp['timestamp'])
power_time = np.array(power['timestamp'])

power_time = power_time - temp_time[0]
temp_time = temp_time - temp_time[0]
temp_time = temp_time / (60)
power_time = power_time / (60)

power_value = np.array(power['value'])
power_value = power_value - 200


plt.plot(temp_time, temp['value'])
plt.plot(power_time, power_value) #adding the power squishes the temperature on the Y axis

plt.xlim(0,140)
plt.ylim(50,65)
plt.xlabel('Time [minutes]')
plt.ylabel('Temperature of Water (C)')
plt.legend(['Water Temp (C)', 'Power switched on/off'])
plt.show()


