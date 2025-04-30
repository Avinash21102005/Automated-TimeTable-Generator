from ortools.sat.python import cp_model
import pandas as pd

def solve_timetable(classes, subjects, teachers, rooms, availability, days, periods):
    model = cp_model.CpModel()
    schedule = {}

    # Create decision variables
    for cls in classes['class_id']:
        for subj in subjects['subject_id']:
            for d in range(len(days)):
                for p in range(periods):
                    for r in range(len(rooms)):
                        schedule[(d, cls, subj, r, p)] = model.NewBoolVar(f'schedule_{cls}_{subj}_{d}_{p}_{r}')

    # Constraint 1: Each class can have at most one subject per period
    for cls in classes['class_id']:
        for d in range(len(days)):
            for p in range(periods):
                model.AddAtMostOne(
                    [schedule[(d, cls, subj, r, p)] for subj in subjects['subject_id'] for r in range(len(rooms))]
                )

    # Constraint 2: Each room can be used by at most one class at a time
    for r in range(len(rooms)):
        for d in range(len(days)):
            for p in range(periods):
                model.AddAtMostOne(
                    [schedule[(d, cls, subj, r, p)] for cls in classes['class_id'] for subj in subjects['subject_id']]
                )

    # Constraint 3: Each teacher can only teach one class at a time
    for t in teachers['teacher_id']:
        for d in range(len(days)):
            for p in range(periods):
                model.AddAtMostOne(
                    [
                        schedule[(d, cls, subj, r, p)]
                        for cls in classes['class_id']
                        for subj in subjects[subjects['teacher_id'] == t]['subject_id']
                        for r in range(len(rooms))
                    ]
                )

    # Constraint 4: Teacher must be available for the assigned period
    for subj_idx, subj_row in subjects.iterrows(): 
        t = subj_row['teacher_id']
        subj = subj_row['subject_id']
        for d_idx, day in enumerate(days):
            for p in range(periods):
                for cls in classes['class_id']:
                    for r in range(len(rooms)):
                        available_row = availability[
                            (availability['teacher_id'] == t) &
                            (availability['day'] == day) &
                            (availability['period'] == p + 1)
                        ]
                        if available_row.empty or available_row.iloc[0]['available'] == 0:
                            model.Add(schedule[(d_idx, cls, subj, r, p)] == 0)

    # Constraint 5: Each subject should be taught to each class 3 times per week
    subject_periods_per_week = 3  # Change this as needed!
    for cls in classes['class_id']:
        for subj in subjects['subject_id']:
            model.Add(
                sum(
                    schedule[(d, cls, subj, r, p)]
                    for d in range(len(days))
                    for p in range(periods)
                    for r in range(len(rooms))
                ) == subject_periods_per_week
            )

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Check solver status
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(" Timetable found!")
        timetable_data = []
        for cls in classes['class_id']:
            for subj in subjects['subject_id']:
                for d in range(len(days)):
                    for p in range(periods):
                        for r in range(len(rooms)):
                            if solver.Value(schedule[(d, cls, subj, r, p)]) == 1:
                                timetable_data.append({
                                    'Class': cls,
                                    'Subject': subj,
                                    'Day': days[d],
                                    'Period': p + 1,
                                    'Room': rooms.iloc[r]['room_name']
                                })

        if timetable_data:
            timetable_df = pd.DataFrame(timetable_data)
            timetable_df.to_excel('generated_timetable.xlsx', index=False)
            return timetable_df
        else:
            print(" Timetable data is empty. No valid timetable found.")
            return None
    else:
        print(f" No solution found. Solver status: {status}")
        if status == cp_model.INFEASIBLE:
            print(" The problem is infeasible — no valid timetable exists with the current constraints.")
        return None
