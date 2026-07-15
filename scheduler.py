from datetime import datetime, timedelta
import pytz, time, configparser
from reddit import reddit

config = configparser.ConfigParser()

# Config variables
config.read('settings.ini')
waiting_duration = int(config['TIME']['waiting_duration'])
cst_from = int(config['TIME']['cst_from'])
cst_to = int(config['TIME']['cst_to'])

def remove_newlines_and_empty(lst):
    # Remove "\n" from each element and filter out empty elements
    cleaned_lst = [element.rstrip('\n') for element in lst if element.strip()]
    return cleaned_lst

with open('subreddits.txt', 'r') as f:
    subreddits = f.readlines()

subreddits = remove_newlines_and_empty(subreddits) # Cleaning list

while True:
	# Get the current time in UTC
	utc_now = datetime.utcnow()

	# Convert UTC time to CST time
	cst_tz = pytz.timezone('America/Chicago')
	cst_now = utc_now.replace(tzinfo=pytz.utc).astimezone(cst_tz)

	# Print the current hour in CST
	#print("Current CST hour:", cst_now.hour)  
	time.sleep(1)

	if cst_now.hour >= cst_from and cst_now.hour <= cst_to:
		for subreddit in subreddits:
			print("Posting on: "+subreddit)
			# Call main script with the subreddit name
			reddit(subreddit)

		print(f"Sleeping for {waiting_duration} seconds . . .")
		time.sleep(waiting_duration)