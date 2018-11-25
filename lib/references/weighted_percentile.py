import os
import sys
import numpy

#http://stackoverflow.com/questions/21844024/weighted-percentile-using-numpy
#http://support.sas.com/documentation/cdl/en/procstat/68142/HTML/default/viewer.htm#procstat_univariate_details14.htm
#http://kochanski.org/gpk/code/speechresearch/gmisclib/gmisclib.weighted_percentile-module.html
#https://pypi.python.org/pypi/wquantiles

def weighted_percentile(a, q=numpy.array([75, 25]), w=None):
    """
    Calculates percentiles associated with a (possibly weighted) array

    Parameters
    ----------
    a : array-like
        The input array from which to calculate percents
    q : array-like
        The percentiles to calculate (0.0 - 100.0)
    w : array-like, optional
        The weights to assign to values of a.  Equal weighting if None
        is specified

    Returns
    -------
    values : numpy.array
        The values associated with the specified percentiles.  
    """
    # Standardize and sort based on values in a
    q = numpy.array(q) / 100.0
    if w is None:
        w = numpy.ones(a.size)
    idx = numpy.argsort(a)
    a_sort = a[idx]
    w_sort = w[idx]

    # Get the cumulative sum of weights
    ecdf = numpy.cumsum(w_sort)

    # Find the percentile index positions associated with the percentiles
    p = q * (w.sum() - 1)

    # Find the bounding indices (both low and high)
    idx_low = numpy.searchsorted(ecdf, p, side='right')
    idx_high = numpy.searchsorted(ecdf, p + 1, side='right')
    idx_high[idx_high > ecdf.size - 1] = ecdf.size - 1

    # Calculate the weights 
    weights_high = p - numpy.floor(p)
    weights_low = 1.0 - weights_high

    # Extract the low/high indexes and multiply by the corresponding weights
    x1 = numpy.take(a_sort, idx_low) * weights_low
    x2 = numpy.take(a_sort, idx_high) * weights_high

    # Return the average
    return numpy.add(x1, x2)

# Sample data
a = numpy.array([1.0, 2.0, 9.0, 3.2, 4.0], dtype=numpy.float)
w = numpy.array([2.0, 1.0, 3.0, 4.0, 1.0], dtype=numpy.float)


print a
print w
exit()

# Make an unweighted "copy" of a for testing
a2 = numpy.repeat(a, w.astype(numpy.int))

# Tests with different percentiles chosen
q1 = numpy.linspace(0.0, 100.0, 11)
q2 = numpy.linspace(5.0, 95.0, 10)
q3 = numpy.linspace(4.0, 94.0, 10)
for q in (q1, q2, q3):
    assert numpy.all(weighted_percentile(a, q, w) == numpy.percentile(a2, q))
