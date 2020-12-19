import decimal

def float_range(start, stop, step):
    while start < stop:
        yield float(start)
        start += decimal.Decimal(step)


def float_lerp(a, b, t):
	return (b - a) * t + a
