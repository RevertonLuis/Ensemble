import datetime


def matrix_linear_interp(dates, values, nvalues=3):

    """ Function that uses linear interpolation of matrices """

    # dates_out and values_out will be the values that entered
    # with the interpolated values between they
    dates_out = []
    values_out = []

    for i in range(1, len(dates)):

        # Calculando o interval entre as dates em segundos
        # Compute the interval between the dates in seconds
        dh = (dates[i] - dates[i - 1]).seconds
        interval = dh / nvalues

        # Compute A and B of y = Ax + B
        A = (values[i] - values[i - 1]) / nvalues
        B = values[i - 1]  # = values[i-1] - A * 0

        # Use linear interpolation between dates[i - 1] and dates[i]
        for x in range(0, nvalues):

            # Add the old dates and the new interpolated ones in the vector
            dates_out.append(dates[i - 1] +
                             datetime.timedelta(seconds=x * interval))

            # Add the old values and the new interpolated ones
            values_out.append(A * x + B)

    # Add the last value and date that were skipped in the for above
    dates_out.append(dates[-1])
    values_out.append(values[-1])

    return dates_out, values_out


# ################## TESTES #################################
# import matplotlib
# import matplotlib.pyplot

# dates = [ datetime.datetime( 2016, 9, 11 ),
# datetime.datetime( 2016, 9, 11 ) + datetime.timedelta(hours=3) ]
# a = numpy.zeros((2,2), 'f')
# b = numpy.zeros((2,2), 'f')

# a[0,0] = numpy.random.random_sample()
# a[0,1] = numpy.random.random_sample()
# a[1,0] = numpy.random.random_sample()
# a[1,1] = numpy.random.random_sample()

# b[0,0] = numpy.random.random_sample()
# b[0,1] = numpy.random.random_sample()
# b[1,0] = numpy.random.random_sample()
# b[1,1] = numpy.random.random_sample()

# print a
# print
# print b

# y = [a, b]

# x = dates

# print x
# print y

# x2, y2 = interpolacao_linear_matricial(x, y, 3)

# y00 = []
# y01 = []
# y10 = []
# y11 = []
# for v in xrange(len(y)):
#   y00.append( y[v][0,0] )
#   y01.append( y[v][0,1] )
#   y10.append( y[v][1,0] )
#   y11.append( y[v][1,1] )

# y200 = []
# y201 = []
# y210 = []
# y211 = []
# for v in xrange(len(y2)):
#   y200.append( y2[v][0,0] )
#   y201.append( y2[v][0,1] )
#   y210.append( y2[v][1,0] )
#   y211.append( y2[v][1,1] )

# fig, ax = matplotlib.pyplot.subplots()
# ax.plot(x, y00,  'r-')
# ax.plot(x, y01,  'b-')
# ax.plot(x, y10,  'g-')
# ax.plot(x, y11,  'y-')

# ax.plot(x2, y200, 'ro')
# ax.plot(x2, y201, 'bo')
# ax.plot(x2, y210, 'go')
# ax.plot(x2, y211, 'yo')

# matplotlib.pyplot.show()
