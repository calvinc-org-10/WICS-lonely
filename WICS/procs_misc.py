from typing import List
from datetime import datetime


def HolidayList(includePast:bool = True) -> List:
    # hardcoded until Holiday table is built and utilized
    HList = [
        datetime.fromisoformat('2023-01-02'),
        datetime.fromisoformat('2023-01-16'),
        datetime.fromisoformat('2023-02-20'),
        datetime.fromisoformat('2023-05-29'),
        datetime.fromisoformat('2023-06-19'),
        datetime.fromisoformat('2023-07-04'),
        datetime.fromisoformat('2023-09-04'),
        datetime.fromisoformat('2023-11-23'),
        datetime.fromisoformat('2023-11-24'),
        datetime.fromisoformat('2023-12-25'),
        datetime.fromisoformat('2023-12-26'),
        datetime.fromisoformat('2024-01-01'),
    ]
    return HList

