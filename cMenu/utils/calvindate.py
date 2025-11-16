from typing import Self

import datetime
from datetime import date, datetime, timedelta
from dateutil.parser import parse
from dateutil.rrule import (
    rrule, rruleset, 
    DAILY, WEEKLY, MONTHLY, YEARLY, 
    MO, TU, WE, TH, FR, SA, SU, 
    )


class calvindate(datetime):
    """ 
        calvindate extends datetime to add some convenience methods
        and to allow more flexible construction from various input formats.
        
        Construction formats:
            calvindate()                          # today's date
            calvindate(year, month, day)          # year, month, day as integers
            calvindate(month, day)                # month, day as integers; year is current year
            calvindate(date_string)               # date_string parseable by dateutil.parser
            calvindate(date_object)               # date_object is a datetime.date or datetime.datetime object
    """
    def __new__(cls, *args):
    # def __init__(self, *args) -> None:
    # we initialize via __new__ since datetime is immutable (__init__ constructor parameters must be YY,MM,DD, with optional hh,mm,ss,us)
    # since we want to allow more flexible construction formats, we have to do the work here
        D = cls._generateDT(*args)
        return super(calvindate, cls).__new__(cls, D.year, D.month, D.day, D.hour, D.minute, D.second, D.microsecond)
    # __new__
    def _generateDT(self, *args) -> datetime:
        D = datetime.today()        # default to today
        if len(args) > 3:
            YY = int(args[0])
            MM = int(args[1])
            DD = int(args[2])
            hh = int(args[3])
            mm = int(args[4]) if len(args) > 4 else 0
            ss = int(args[5]) if len(args) > 5 else 0
            us = int(args[6]) if len(args) > 6 else 0
            D = datetime(YY,MM,DD,hh,mm,ss,us)
        elif len(args) == 3:  # year, month, day was passed in
            YY, MM, DD = map(int, args)
            D = datetime(YY,MM,DD)
        elif len(args) == 2:    # month, day passed in , year should be current year
            YY = date.today().year
            MM, DD = map(int, args)
            D = datetime(YY,MM,DD)
        elif len(args) == 1:    # either a date string or date object passed in
            if isinstance(args[0],(date, datetime)):
                D = datetime.combine(args[0], datetime.min.time()) \
                    if isinstance(args[0], date) and not isinstance(args[0], datetime) else args[0]
            else:
                try:
                    D = parse(str(args[0]))
                except Exception:
                    D = datetime.today()                
        else:
            # invalid number of args.  Do nothing; let the default stand
            pass
        return D
    # _generateDT

    def value(self) -> Self:
        return self
    def setValue(self, newdate) -> None:
        D = self._generateDT(newdate)
        self = D
    def as_datetime(self) -> datetime:
        return datetime(self.year, self.month, self.day, self.hour, self.minute, self.second, self.microsecond)

    def daysfrom(self,delta:int) -> Self:
        R_dt = self + timedelta(days=delta)
        return R_dt
    def tomorrow(self) -> Self:
        return self.daysfrom(1)
    def yesterday(self) -> Self:
        return self.daysfrom(-1)
    
    def nextWorkdayAfter(self, nonWorkdays={SA,SU}, extraNonWorkdayList={}, include_afterdate=False):
        afterdate = self.as_datetime()
        
        excRule = rrule(WEEKLY,dtstart=afterdate,byweekday=nonWorkdays)
        afterdaysRule = rrule(DAILY,dtstart=afterdate)

        exclSet = rruleset()
        exclSet.rrule(afterdaysRule)
        exclSet.exrule(excRule)
        # loop extraNonWorkdays into exclSet.exdate
        for xDate in extraNonWorkdayList:
            exclSet.exdate(xDate)

        return exclSet.after(afterdate,include_afterdate)
    
    # operators
    # def __comparison_workhorse__(self, RHE, compOpr):
    #     LHExpr = calvindate(self).as_datetime()
    #     RHExpr = calvindate(RHE).as_datetime()
    #     if compOpr == 'lt':
    #         return LHExpr < RHExpr
    #     if compOpr == 'le':
    #         return LHExpr <= RHExpr
    #     if compOpr == 'eq':
    #         return LHExpr == RHExpr
    #     if compOpr == 'ne':
    #         return LHExpr != RHExpr
    #     if compOpr == 'gt':
    #         return LHExpr > RHExpr
    #     if compOpr == 'ge':
    #         return LHExpr >= RHExpr
    #     return False
    # def __lt__(self, other):
    #     return self.__comparison_workhorse__(other,'lt')
    # def __le__(self, other):
    #     return self.__comparison_workhorse__(other,'le')
    # def __eq__(self, other):
    #     return self.__comparison_workhorse__(other,'eq')
    # def __ne__(self, other):
    #     return self.__comparison_workhorse__(other,'ne')
    # def __gt__(self, other):
    #     return self.__comparison_workhorse__(other,'gt')
    # def __ge__(self, other):
    #     return self.__comparison_workhorse__(other,'ge')
    # def __add__(self, other):
    #     if isinstance(other, int):
    #         return self.daysfrom(other)
    #     else:
    #         return NotImplemented
    # def __sub__(self, other):
    #     if isinstance(other, int):
    #         return self.daysfrom(-other)
    #     else:
    #         return NotImplemented

    def __str__(self) -> str:
        strfmt = "%Y-%m-%d" if self.hour == 0 and self.minute == 0 and self.second == 0 else "%Y-%m-%d %H:%M:%S"
        return self.strftime(strfmt)
    # __str__
# calvindate 

def IsDateString(datestr):
    try:
        D = parse(datestr)
        return True
    except:
        return False
# IsDateString
    
