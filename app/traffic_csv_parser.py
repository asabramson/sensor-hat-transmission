import csv, re
from functools import lru_cache
from pathlib import Path
from flask import current_app

DAY_LETTERS = ["M","T","W","T","F","S","S"]  # help parse CSV

def _data_dir() -> Path:
    return Path(current_app.config["TRAFFIC_DATA_DIR"]).resolve()

def _row_is_day(row):
    # first column has "T 26" format (letter + space + number)
    if not row or not row[0]:
        return False
    return bool(re.match(r"^[MTWFS]\s+\d{1,2}$", row[0].strip()))

@lru_cache(maxsize=None)
def load_csv(loc_id: str, direction: str):
    fname = f"{loc_id}_{direction}.csv"
    path  = _data_dir() / fname
    rows  = []
    with path.open() as f:
        rdr = csv.reader(f)
        for row in rdr:
            rows.append(row)

    data_rows = []
    for row in rows:
        if _row_is_day(row):
            day_num = int(row[0].split()[1])
            hours   = list(map(int, row[1:25]))
            total   = int(row[25]) # final column
            data_rows.append({"day": day_num, "hours": hours, "total": total})
    return data_rows

def get_day_hours(loc_id: str, day: int):
    inbound = load_csv(loc_id, "in")
    outbound = load_csv(loc_id, "out")
    def pick(rows):
        for r in rows:
            if r["day"] == day:
                return r["hours"]
        return [0]*24
    return pick(inbound), pick(outbound)

def get_month_totals(loc_id: str):
    inbound = load_csv(loc_id, "in")
    outbound = load_csv(loc_id, "out")
    inbound_sorted  = sorted(inbound, key=lambda r: r["day"])
    outbound_sorted = sorted(outbound, key=lambda r: r["day"])
    in_tot  = [r["total"]  for r in inbound_sorted]
    out_tot = [r["total"]  for r in outbound_sorted]
    days    = [r["day"]    for r in inbound_sorted]
    return days, in_tot, out_tot