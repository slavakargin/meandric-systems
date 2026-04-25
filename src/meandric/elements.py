"""Standard generators and common elements of Thompson's group F.

Each element is given as a pair ``(domain, range_)`` of dyadic partitions.
"""

# x_0: [0, 1/2, 3/4, 1] -> [0, 1/4, 1/2, 1]
X0_DOMAIN = ['0', '10', '11']
X0_RANGE  = ['00', '01', '1']

# x_1: [0, 1/2, 3/4, 7/8, 1] -> [0, 1/2, 5/8, 3/4, 1]
X1_DOMAIN = ['0', '10', '110', '111']
X1_RANGE  = ['0', '100', '101', '11']

def xn(n):
    """Generator x_n of Thompson's group F.

    x_n is the identity on [0, 1-1/2^n] and a rescaled x_0 on [1-1/2^n, 1].

    >>> xn(0)
    (['0', '10', '11'], ['00', '01', '1'])
    >>> xn(1)
    (['0', '10', '110', '111'], ['0', '100', '101', '11'])
    """
    prefix = '1' * n
    id_leaves = ['1' * k + '0' for k in range(n)]
    domain = id_leaves + [prefix + '0', prefix + '10', prefix + '11']
    range_ = id_leaves + [prefix + '00', prefix + '01', prefix + '1']
    return domain, range_
