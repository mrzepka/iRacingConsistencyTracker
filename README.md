# iRacingConsistencyTracker
An ongoing project where I try to make it easier to grab consistency information from iRacing results

HOW TO USE IT:

You will need to install https://github.com/jasondilworth56/iracingdataapi for this to work, but that can be done via pip.

Line 11 - Add your iRacing email and your iRacing password


Use this script with a customer Id, subsession Id, or both.
Parameters:
Help          -> -h or --help
Customer ID   -> -c or --cust_id
Subsession ID -> -s or --subsession_id

Example:
python consistency_tracker.py -c 573444 -s 59067779

If you only use a customer ID, it will create a csv of _all_ solo events for that customer
If you only use a subsession ID, it will create a csv of _all_ drivers in that subsession
If you use both a customer ID, and subsession ID, it will only include data for that driver in that subsession

The paramters for main:
 - If you only include a subsession ID, it will create a CSV for all drivers in that subsession
 - If you only include a customer ID, it will create a CSV for all official race events that driver has done (may take a while)
 - If you include both a customer ID and a subsesion ID, it will grab the data only for that driver in that subsession.

NOTES:
- Doesn't work on team events yet (I don't plan to add it because I'm lazy)
- Two csv are output:
  - *_info.csv - This has the results data as you would probably expect to see in iRacing. Includes some "consistency" metrics I made up
  - *_info_laps.csv - This has all the laptimes from the data pulled (i.e. every race, every driver in a race, or the single driver in a single race)

If something is confusing I'm sorry but I didn't really intend anyone else to use this when I started writing it.
