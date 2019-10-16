from datetime import datetime


BEEKEEPER_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


def bkdt_to_dt(beekeper_time):
    """
    Converts date time received from the API to Python datetime object
    Args:
        beekeper_time (str): string value of date time, e.g. `2019-10-12T15:43:37`

    Returns:
        datetime: datetime object
    """
    return datetime.strptime(beekeper_time, BEEKEEPER_TIME_FORMAT)


def dt_to_bkdt(date_time):
    """
    Converts date time received from the API to Python datetime object
    Args:
        date_time (datetime): Python date time

    Returns:
        str: Beekeeper-compatible date time, e.g. `2019-10-12T15:43:37`
    """
    return date_time.strftime(BEEKEEPER_TIME_FORMAT)
