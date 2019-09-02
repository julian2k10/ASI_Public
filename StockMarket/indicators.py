def PVC(volume, fast_period=3, slow_period=13):
	"""
	    Summary:
	    Percentage Volume Change - 
	    Calculates the percentage change of the two volume moving averages over the given period of time.
        -------

        Parameters:
        volume : list or array of volume data

        fast_period : Integer value for fast moving average. Default value = 3

        slow_period : Integer value for slow moving average. Default value = 13
        ----------

        Returns
        -------
        Array of percentage volume changes corresponding to the volume data
	"""
	try:
		size = len(volume)
		fast_sum = 0
		slow_sum = 0
		fast_average = 0
		slow_average = 0
		fast_data = list() #Create dataset for fast moving average
		slow_data = list() #Create dataset for slow moving average
		values = list()
		#loop through data
		for x in range(size):
			#Add new value to the end of the list
			fast_data.append(volume[x]) 
			slow_data.append(volume[x]) 
			#Create running total for each moving average period
			fast_sum += volume[x]
			slow_sum += volume[x]
			values.append(0) #Add default starting value of zero
			#Calculate indicator values
			if len(fast_data) > fast_period:
				fast_sum -= fast_data[0] #Substract the oldest value from the fast running total
				fast_data.pop(0) #Remove the oldest value from the list
				fast_average = fast_sum / fast_period

			if len(slow_data) > slow_period:
				slow_sum -= slow_data[0] #Substract the oldest value from the slow running total
				slow_data.pop(0) #Remove the oldest value from the list
				slow_average = slow_sum / slow_period

			if fast_average > 0 and slow_average > 0:
				#Calculate the moving average percentage change
				values[x] = ((fast_average-slow_average)/slow_average) * 100

		return values
	except:
		print("Invalid Datatype! \nExpected Type: array, or list")

