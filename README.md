# iRacingConsistencyTracker
An ongoing project where I try to make it easier to grab consistency information from iRacing results.

This is a script you can run locally (once you install the iracingdataapi referenced below) to pull data from the iRacing API for results and laptimes.
This script will create csv files that can be opened in excel, sheets, or another program of your choice to further look into the data.

HOW TO USE IT:

You will need to install https://github.com/jasondilworth56/iracingdataapi for this to work, but that can be done via pip.

Line 11 - Add your iRacing email and your iRacing password


            Use this script with a customer Id, subsession Id, or both.
            Parameters:
            Customer ID   -> -c or --cust_id
            Subsession ID -> -s or --subsession_id
            last x races  -> -l or --last
            !!-- Getting data for a specific series --!!
            Series        -> --series
            Year          -> --year
            Season        -> --season

            Example:
            python consistency_tracker.py -c 573444 -s 59067779
            python consistency_tracker.py -c 573444 -l 5
            python consistency_tracker.py -s 59067779
            python consistency_tracker.py -c 573444

            If you only use a customer ID, it will create a csv of _all_ solo events for that customer
            If you only use a subsession ID, it will create a csv of _all_ drivers in that subsession
            If you use both a customer ID, and subsession ID, it will only include data for that driver 
                in that subsession
            If you use a subsession ID it will use that and NOT the "last x races"
            If you include a series ID, you will need to include a year and a season (otherwise it just takes forever)
                 SERIES ID can be found on the series information page within iracing for a series you are intereseted in.


-----------------------------------------------------------------------------
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

** PLEASE FEEL FREE TO FORK, UPDATE, CREATE ISSUES, SUGGEST THINGS, CREATE PULL REQUESTS **
