import pandas as pd

def load_data():
    try:
        classes = pd.read_csv('data/classes.csv')
        subjects = pd.read_csv('data/subjects.csv')
        teachers = pd.read_csv('data/teachers.csv')
        rooms = pd.read_csv('data/rooms.csv')
        availability = pd.read_csv('data/availability.csv')
        return classes, subjects, teachers, rooms, availability
    except FileNotFoundError as e:
        print(f"❌ File not found: {e.filename}")
        return None, None, None, None, None
    except Exception as e:
        print(f"❌ Error while loading data: {e}")
        return None, None, None, None, None
