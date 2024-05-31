def parse_interval(interval_str):
    units = {'s': 1, 'm': 60, 'h': 3600}
    unit = interval_str[-1]
    if unit in units:
        return int(interval_str[:-1]) * units[unit]
    else:
        raise ValueError(f"Unknown interval unit: {unit}")
