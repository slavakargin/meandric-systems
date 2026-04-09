"""Standard generators and common elements of Thompson's group F.

Each element is given as a pair ``(domain, range_)`` of dyadic partitions.
"""

# x_0: [0, 1/2, 3/4, 1] -> [0, 1/4, 1/2, 1]
X0_DOMAIN = ['0', '10', '11']
X0_RANGE  = ['00', '01', '1']

# x_1: [0, 1/2, 3/4, 7/8, 1] -> [0, 1/2, 5/8, 3/4, 1]
X1_DOMAIN = ['0', '10', '110', '111']
X1_RANGE  = ['0', '100', '101', '11']
