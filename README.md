# iRacingConsistencyTracker
An ongoing project where I try to make it easier to grab consistency information from iRacing results

HOW TO USE IT:

Line 11 - Add your iRacing email and your iRacing password

Update _cust_id to the iRacing customer ID you want to grab data for

Update _subsession_id if you want a specific subsession to be pulled in

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
