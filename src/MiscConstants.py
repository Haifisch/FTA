# max number of datapoints to store for each line on the graph really
# combined graphs will contain MaxPointsOnGraph multiplied by the number of lines shown.
# this is semi-forgiving but i wouldn't recommend setting it too high as old values may get "smothered" tbh
# ideally each widget will setup seperate ui updating logic and just shovel telemetry data as fast as it can.
# updating internal vars that the ui reflects. 
MaxPointsOnGraph = 8000
# autoshifter config
UPSHIFT_KEY = "e"
DOWNSHIFT_KEY = "q"