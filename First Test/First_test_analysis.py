
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

power = loadvectors('first_test_power.csv')
temp = loadvectors('first_test_temp.csv')

import matplotlib.pyplot as plt
import numpy as np

a1 = np.array(temp['timestamp'])
a2 = np.array(power['timestamp'])

a2 = a2 - a1[0]
a1 = a1 - a1[0]
a1 = a1 / (60)
a2 = a2 / (60)

plt.plot(a1, temp['value'])
#plt.plot(a2, power['value']) #adding the power squishes the temperature on the Y axis
    
plt.xlim(0,100)
plt.xlabel('Time [minutes]')
plt.ylabel('Temperature of Water (C)')
plt.legend(['Water Temp (C)', 'Power Draw (W)'])
plt.show()


