import soccerdata as sd
fbref = sd.FBref(leagues="ENG-Premier League", seasons="20-21")
sched = fbref.read_schedule()
sched = sched.reset_index()
print("COLUMNS:", list(sched.columns))
print("SAMPLE ROW:", sched.iloc[0].to_dict())
print("TOTAL MATCHES:", len(sched))
