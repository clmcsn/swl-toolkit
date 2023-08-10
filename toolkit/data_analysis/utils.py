from typing import Union
from dataclasses import dataclass
import pandas as pd

@dataclass
class TimeEventClass():
    def __init__(self, ID : Union[int, str], period : int = 0, start : int = -1, ecount : int = 1):
        self.ID = ID
        self.period = 0
        self.start = -1
        self.is_new = True
        self.sub_events = 0
        self.thread_sub_events = 0
        if period > 0:
            self.register(period, start, ecount)
    
    def end(self):
        return self.start + self.period

    def register(self, period, start, ecount) -> bool:
        new_event_end = start + period
        if self.is_new:
            self.period = period
            self.start = start
            self.sub_events += 1
            self.thread_sub_events += ecount
            self.is_new = False
            return True
        else:
            if start > self.start + self.period: # No overlap, event happening after the end of the current event
                return False
            elif start < self.start:             # No overlap, event happening before the start of the current event
                return False
            elif new_event_end < self.end():     # Overlap, event ending before the end of the current event
                self.sub_events += 1
                self.thread_sub_events += ecount
                return True
            else:                                # Overlap, but event ending after the end of the current event
                self.sub_events += 1
                self.thread_sub_events += ecount
                self.period = new_event_end - self.start
                return True
    def to_dict(self):
        return {"ID":self.ID, "period":self.period, "start":self.start, "event_count":self.sub_events, "thread_event_count":self.thread_sub_events}


class TimeSeriesClass():
    def __init__(   self, ID : Union[int, str], events : pd.DataFrame = pd.DataFrame({}),
                    period_col_name : str = "period", start_col_name : str = "start"):
        self.ID = ID
        self.events = events
        self.period_col_name = period_col_name
        self.start_col_name = start_col_name
        self.iter = 0
        self.trace = [TimeEventClass(   ID=self.iter, 
                                        period=self.events.iloc[0][self.period_col_name], 
                                        start=self.events.iloc[0][self.start_col_name],
                                        ecount=self.events.iloc[0]["e_count"])]
    
    def make_synthesis(self) -> pd.DataFrame:
        self.events = self.events.sort_values(by=self.start_col_name)
        self.events.reset_index(drop=True, inplace=True)
        for i in range(1,len(self.events)):
            is_not_new = self.trace[self.iter].register(    period=self.events.iloc[i][self.period_col_name], 
                                                            start=self.events.iloc[i][self.start_col_name],
                                                            ecount=self.events.iloc[i]["e_count"])
            if not is_not_new:
                self.iter += 1
                self.trace.append(TimeEventClass(   ID=self.iter,
                                                    period=self.events.iloc[i][self.period_col_name],
                                                    start=self.events.iloc[i][self.start_col_name],
                                                    ecount=self.events.iloc[i]["e_count"]))
        return self.make_df()
            
    def make_df(self):
        l = []
        for t in self.trace:
            l.append(t.to_dict())
        df = pd.DataFrame(l)
        df.rename(columns={"period":self.period_col_name, "start":self.start_col_name}, inplace=True)
        return df