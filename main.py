from util import load_data
from timetablesolver import solve_timetable

import pandas as pd
import os

# Setup days and periods
days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
periods_per_day = 5

# ✅ Step 1: Load all input data
classes, subjects, teachers, rooms, availability = load_data()

# ✅ Step 2: Call the solver with loaded data
timetable_df = solve_timetable(classes, subjects, teachers, rooms, availability, days, periods_per_day)

if timetable_df is not None:
    os.makedirs('output', exist_ok=True)
    timetable_df.to_excel('output/final_timetable.xlsx', index=False)
    print("✅ Timetable generated and saved to output/final_timetable.xlsx")
else:
    print("❌ No solution found.")
