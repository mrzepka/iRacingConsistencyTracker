#This is the API wrapper I leaned on:
#https://github.com/jasondilworth56/iracingdataapi
#------------------------------------
#iracing api documentation: https://members-login.iracing.com/?ref=https%3A%2F%2Fmembers-ng.iracing.com%2Fdata
#------------------------------------
import getopt, sys, statistics, csv, operator, time
from iracingdataapi.client import irDataClient

#create data client that does all the work
idc = irDataClient(username="<your iRacing email here>", password="<your iRacing password here>")

#get command line stuff
argumentList = sys.argv[1:]

#short options:
options = "hc:s:l:"

long_options = ['help', 'cust_id=', 'subsession_id=', 'last=', 'series=', 'year=', 'season=']

_cust_id = None
_subsession_id = None
_last_x = None
_series_id = None
_year = None
_season = None

helpText = """
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
            """

try:
    arguments, values = getopt.getopt(argumentList, options, long_options)

    if arguments == []:
        print(helpText)
        exit(0)

    for currArg, currVal in arguments:
        if currArg in ('-h', '--help'):
            print(helpText)
            exit(0)
        elif currArg in ('-c', '--cust_id'):
            _cust_id = currVal
        elif currArg in ('-s', '--subsession_id'):
            _subsession_id = currVal
        elif currArg in ('-l', '--last'):
            _last_x = currVal
        elif currArg in ('--series'):
            _series_id = currVal
        elif currArg in ('--year'):
            _year = currVal
        elif currArg in ('--season'):
            _season = currVal
        else:
            print(helpText)
            exit(0)

except getopt.error as err:
    print(str(err))


#Private Variables! :D
_start_year = 2008 #always 2008, that was the first season of iracing
_curr_year = 2023 

#more for reference than use
_event_types = [{'label': 'Practice', 'value': 2}, 
                {'label': 'Qualify', 'value': 3}, 
                {'label': 'Time Trial', 'value': 4}, 
                {'label': 'Race', 'value': 5}]

#list for the column headers for the csv
_title_row_session_only = ["Subsession ID",
                            "License Class",
                            "Year",
                            "Season",
                            "Series",
                            "SOF",
                            "Track",
                            "Layout",
                            "cust_id",
                            "display_name",
                            "finish_position",
                            "finish_position_in_class",
                            "laps_lead",
                            "laps_complete",
                            "interval",
                            "class_interval",
                            "average_lap",
                            "best_lap_num",
                            "best_lap_time",
                            "best_nlaps_num",
                            "best_nlaps_time",
                            "best_qual_lap_num",
                            "best_qual_lap_time",
                            "reason_out_id",
                            "reason_out",
                            "champ_points",
                            "drop_race",
                            "position",
                            "qual_lap_time",
                            "starting_position",
                            "starting_position_in_class",
                            "car_class_id",
                            "car_class_name",
                            "car_class_short_name",
                            "division",
                            "old_cpi",
                            "oldi_rating",
                            "new_cpi",
                            "newi_rating",
                            "incidents",
                            "league_points",
                            "league_agg_points",
                            "car_name",
                            "iRating Change",
                            "Position Change",
                            "Car Num in Class",
                            "Average Lap",
                            "Fastest Lap",
                            "Consistency",
                            "Standard Deviation",
                            "Adjusted Standard Deviation",
                            "Percent Normal Laps",
                            "Clean Laps",
                            "Clean Lap Percent"]

#private list of fields that the subsession returns, that we are not interested in
# including in our output csv.
_exclude_fields = ["opt_laps_complete",
                "new_ttrating",
                "multiplier",
                "club_id",
                "club_name",
                "club_shortname",
                "division_name",
                "best_qual_lap_at",
                "club_points",
                "old_license_level",
                "old_sub_level",
                "old_ttrating",
                "new_license_level",
                "new_sub_level",
                "new_ttrating,multiplier",
                "license_change_oval",
                "license_change_road",
                "max_pct_fuel_fill",
                "weight_penalty_kg",
                "car_id",
                "aggregate_champ_points",
                "livery",
                "suit",
                "helmet",
                "watched",
                "friend",
                "ai"]

#private data structure that has good lookup time, but is very ugly to access when it's
# all put together
_all_data = { "column_headers": _title_row_session_only,
                "subsession_data": {} 
            }

"""
Parses all the customer IDs, and names that are within a subsession json/dict format.
Adds the Customer ID Dictionaries, and the Customer Names to the _all_data dictionary

Parameters:
    subsession : dict
Return Values:
    customer_ids : list
    driver_names : list
"""
def get_cust_ids_in_subsession(subsession=None):
    if not subsession:
        raise RuntimeError("Please supply subsession that is not None")
    race_result_index = len(subsession["session_results"])-1
    all_results = []
    simsession_numbers = get_simsession_numbers(subsession)

    for session in subsession["session_results"]:
        if session["simsession_type"] == 6:
            all_results.append(session["results"])

    customer_ids = []
    driver_names = []
    #silly iterator for the simsession numbers. Next target of refactor lol
    i=0
    #single result is a single simsession result page
    for single_result in all_results:

        #result is a single persons race result
        for result in single_result:

            if "team_id" in result.keys():
                (_all_data["subsession_data"]
                [subsession["subsession_id"]]
                [simsession_numbers[i]]) = {-100 : ["team", "event", "not", "supported", "yet"]}
                continue
            customer_ids.append(result["cust_id"])
            driver_names.append(result["display_name"])
            
            #write to dict
            (_all_data["subsession_data"]
                [subsession["subsession_id"]]
                [simsession_numbers[i]]
                [result["cust_id"]]) = {}
            (_all_data["subsession_data"]
                [subsession["subsession_id"]]
                [simsession_numbers[i]]
                [result["cust_id"]]
                ["name"]) = result["display_name"]
        i=i+1
    return customer_ids, driver_names

"""
Calls iRacing API (wrapper) to get all the laptimes for a customer within a subsession

Parameters:
    subsession_id : int
    cust_id : int
    simsession Number : int

    Note: Simsesson != Subsession. Each subsession can have multiple simsessions
Return Values:
    laptime_list : list
    clean_laps : int
"""
def get_lap_data_for_subsession_and_cust(subsession_id=None, cust_id=None, simsession_number=None):
    if not cust_id:
        raise RuntimeError("Please supply customer ID")
    if not subsession_id:
        raise RuntimeError("Please supply subsession ID")
    if not simsession_number:
        lap_results = idc.result_lap_data(subsession_id=subsession_id, cust_id=cust_id)
    else:
        lap_results = idc.result_lap_data(subsession_id=subsession_id, cust_id=cust_id, 
            simsession_number=simsession_number)
    laptime_list = []
    clean_laps = 0
    if lap_results:
        for lap in lap_results:
            if lap["lap_number"] == 0:
                continue
            if not lap["incident"]:
                clean_laps = clean_laps + 1
            laptime_list.append(lap["lap_time"]/10000)
    return laptime_list, clean_laps

"""
"Orchestrator" for getting all laps in a simsession within a subsession
Calls "get_lap_data_for_subsession_and_cust"
Writes lapdata to _all_data dictionary

Parameters:
    subsession_id : int
    customers : list
        # This is a list of customer IDs
    simsession_number : int
    cust_id : int
        #Optional

Return Values:
    lap_list_list : list
        #list of laptime lists
    clean_lap_counts : list
"""
def get_all_session_laps(subsession_id, customers, simsession_number, cust_id=None):
    lap_list_list = []
    clean_lap_counts = []
    curr_drivers = _all_data["subsession_data"][subsession_id][simsession_number].keys()
    for customer in customers:
        #if we are looking for a customer, and it's not who we're looking for or
        #the driver isn't in the heat/simsession, then we continue without looking for the laps
        if cust_id and (customer != cust_id or cust_id not in curr_drivers):
            continue
        curr_name = (_all_data["subsession_data"]
            [subsession_id]
            [simsession_number]
            [customer]
            ["name"])
        meta = [subsession_id, customer, curr_name]
        laps, clean_lap_count = get_lap_data_for_subsession_and_cust(subsession_id, customer, simsession_number)
        lap_list_list.append(meta + laps)
        clean_lap_counts.append(clean_lap_count)
        #write to dict
        (_all_data["subsession_data"]
            [subsession_id]
            [simsession_number]
            [customer]
            ["laps"]) = laps
        (_all_data["subsession_data"]
            [subsession_id]
            [simsession_number]
            [customer]
            ["clean_laps"]) = clean_lap_count

    return lap_list_list, clean_lap_counts

"""
Gets the subsession dictionary through the iRacingData API Client
Stands up the subsession dictionaries within the _all_data dictionary
Stands up the simsession dictionaries within the subsession dictionary
Calls "get_simsession_numbers"

Parameters:
    subsession_id : int

Return Values:
    subsession : dict
"""
def get_subsession(subsession_id=None):
    if not subsession_id:
        raise RuntimeError("Please supply subsession ID")
    subsession = idc.result(subsession_id=subsession_id)

    if subsession:
        _all_data["subsession_data"][subsession["subsession_id"]] = {}
        simsession_numbers = get_simsession_numbers(subsession)
        for simsession_num in simsession_numbers:
            (_all_data["subsession_data"]
                [subsession["subsession_id"]]
                [simsession_num]) = {}
    return subsession

"""
Parses subsession metadata from subsession dictionary
Writes metadata to the subsession dictionary within _all_data dictionary

Parameters:
    subsession : dict

Return Values:
    metadata : list
"""
def get_subsession_metadata(subsession=None):
    if not subsession:
        raise RuntimeError("Missing subsession")
    metadata = []
    metadata.append(subsession["subsession_id"])
    metadata.append(subsession["license_category"])
    metadata.append(subsession["season_year"])
    metadata.append(subsession["season_quarter"])
    metadata.append(subsession["series_short_name"])
    metadata.append(subsession["event_strength_of_field"])
    metadata.append(subsession["track"]["track_name"])
    metadata.append(subsession["track"]["config_name"])
    #write to dict
    (_all_data["subsession_data"]
        [subsession["subsession_id"]]
        ["metadata"]) = metadata
    return metadata

"""
Parses race results from subsession dictionary (in a very ugly way)
Writes the races results to the customer dictionary in the simession dictionary 
    within the subsession dictionary
Returns a list of lists of data rows (previous way to print)

Parameters:
    subsession : dict
    cust_id : dict
        #optional

Return Values:
    data : list
        #list of lists
    is_team_event : boolean
        #since we dont handle team events, we pass this back to indicate this subsession as such
        #opportunity for next refactor since this is now written to the subsession dictionary
"""
def get_subsession_race_results(subsession=None, cust_id=None):
    if not subsession:
        raise RuntimeError("Please supply subsession")
    is_team_event = False
    all_results = []
    curr_subsession_id = subsession["subsession_id"]
    simsession_numbers = get_simsession_numbers(subsession)

    for session in subsession["session_results"]:
        if session["simsession_type"] == 6:
            all_results.append(session["results"])

    data = []

    #iterator for simsession_numbers
    i=0
    for single_result in all_results:
        for results in single_result:
            result_row = []
            #if it's a team
            if "team_id" in results.keys():
                (_all_data["subsession_data"]
                    [curr_subsession_id]
                    ["team_event"]) = True
                is_team_event = True
                return [['team event not yet handled']], is_team_event
            
            curr_cust_id = results["cust_id"]

            #if we're getting all data
            for item in results:
                # print(item)
                if item in _exclude_fields:
                    continue
                elif item in ["position", 
                            "starting_position", 
                            "starting_position_in_class",
                            "finish_position",
                            "finish_position_in_class"]:

                    result_row.append(results[item]+1)
                else:
                    result_row.append(results[item])

                #getting the "old irating" to calculate car number easier
                if item == "oldi_rating":
                    (_all_data["subsession_data"]
                        [curr_subsession_id]
                        [simsession_numbers[i]]
                        [curr_cust_id]
                        ["start_irating"]) = results[item]
            result_row.append(results["newi_rating"] - results["oldi_rating"])
            result_row.append(results["starting_position_in_class"] - results["finish_position_in_class"])
            
            (_all_data["subsession_data"]
                [curr_subsession_id]
                [simsession_numbers[i]]
                [curr_cust_id]
                ["results"]) = result_row
            data.append(result_row)
        i=i+1
    return data, is_team_event

"""
Gets all the subsession IDs from a specific subset (i.e. series, driver)
We need either a customer ID or a series ID

Parameters:
    cust_id : int
        #required if series_id is not included
    series_id : int
        #required if cust_id is not included
    year_in : int
        #optional if cust_id is included
        #required with series_id
        #required with season_in
    season_in : int
        #optional if cust_id is included
        #optional if year_in is included
        #required if series_id is included

Return Values:
    all_subsession_ids : list
"""
def get_all_subsessions(cust_id=None, series_id=None, year_in=None, season_in=None):
    if not cust_id and not series_id:
        raise RuntimeError("Please supply customer ID or series ID")
    all_series_data = []

    #no year and season provided, loop through all years and seasons for customer
    if not year_in and not season_in:
        for year in range(_start_year, _curr_year+1):
            print('retrieving year: ' + str(year))
            for season in range(1, 5):
                series_data_for_season = idc.result_search_series(season_year=year, season_quarter=season, cust_id=cust_id, event_types=5)
                all_series_data = all_series_data + series_data_for_season

    #loop through all seasons for a year for customer
    elif not season_in:
        for season in range(1, 5):
            series_data_for_season = idc.result_search_series(season_year=year_in, season_quarter=season, cust_id=cust_id, event_types=5)
            all_series_data = all_series_data + series_data_for_season

    #get specific year and season for customer or series
    else:
        series_data_for_season = idc.result_search_series(season_year=year_in, season_quarter=season_in, series_id=series_id, cust_id=cust_id, event_types=5)
        all_series_data = all_series_data + series_data_for_season

    all_subsession_ids = []
    for session in all_series_data:
        all_subsession_ids.append(session["subsession_id"])

    return all_subsession_ids

"""
This is the beginning of the "Lap Math" suite of functions
#possibly a target of refactoring?

This function is used to remove "outlier" laps from data (i.e. pit stops, bad crashes)
    to create the "adjusted" standard deviation values

Parameters:
    laps : list
    avg : float
        #average laptime

Return Values:
    valid_laptimes : list
"""
def remove_outlier_laps(laps, avg):
    delta = 0
    valid_laptimes = []
    for lap in laps:
        d2 = 0
        delta = 0
        delta = delta + abs(lap-avg)
        d2 = delta * delta
        if d2 < 100:
            valid_laptimes.append(lap)
    return valid_laptimes

"""
Calculates the standard deviation of a list of laptimes

Parameters:
    laps : list

Return Values:
    std_dev : float
"""
def get_standard_deviation_of_laps(laps):
    positive_laps = []
    std_dev = 0
    #don't count weird negative or impossible laptimes
    for lap in laps:
        if lap > 1:
            positive_laps.append(lap)
    if len(positive_laps) > 1:
        std_dev = statistics.stdev(positive_laps)
    return std_dev

"""
Calculates the average laptime of a list of laptimes

Parameters:
    laps : list

Return Values:
    average_laptime : float
"""
def get_average_laptime_of_laps(laps):
    positive_laps = []
    average_laptime = 0
    #don't count weird negative or impossible laptimes
    for lap in laps:
        if lap > 1:
            positive_laps.append(lap)
    if len(positive_laps) > 1:
        average_laptime = statistics.mean(positive_laps)
    return average_laptime

"""
Calculates the fastest laptime of a list of laptimes

Parameters:
    laps : list

Return Values:
    fastest_laptime : float
"""
def get_fastest_laptime_of_laps(laps):
    positive_laps = []
    fastest_laptime = 0
    #don't count weird negative or impossible laptimes
    for lap in laps:
        if lap > 1:
            positive_laps.append(lap)

    if len(positive_laps) > 1:
        fastest_laptime = min(positive_laps)
    return fastest_laptime

"""
Calls all the lap math related functions
Organizes the results of the lap math

Parameters:
    laps_for_race : list
    clean_lap_count : int

Return Values:
    data_to_return : list
"""
def do_lap_math(laps_for_race, clean_lap_count):
    if laps_for_race and len(laps_for_race) > 1:
        lap_stdev = get_standard_deviation_of_laps(laps_for_race)
        lap_avg = get_average_laptime_of_laps(laps_for_race)
        lap_fast = get_fastest_laptime_of_laps(laps_for_race)
        valid_laps = remove_outlier_laps(laps_for_race, lap_avg)
        if valid_laps and len(valid_laps) > 1:
            valid_stdev = get_standard_deviation_of_laps(valid_laps)
            valid_percent = len(valid_laps)/len(laps_for_race)
        else:
            valid_stdev = 0
            valid_percent = 0
        incident_free_lap_percent = clean_lap_count/len(laps_for_race)
    else:
        lap_stdev = 0
        lap_avg = 1
        lap_fast = 1
        valid_stdev = 0
        valid_percent = 0
        incident_free_lap_percent = 0
    if lap_avg > 0:
        delta = (lap_avg - lap_fast)/lap_avg
    else:
        delta = 0

    data_to_return = [lap_avg,
            lap_fast,
            delta,
            lap_stdev,
            valid_stdev,
            valid_percent,
            clean_lap_count,
            incident_free_lap_percent]

    return data_to_return

"""
Parses the _all_data dictionary for the lists that should be printed

Parameters:
    cust_id : int

Return Values:
    result_rows : list
        #rows that should be printed in the *_consistency csv
    lap_rows : list
        #rows that should be printed in the *_laps csv
"""
def organize_data(cust_id=None):
    result_rows = []
    lap_rows = []
    for subsession_id in _all_data["subsession_data"]:
        if "team_event" in _all_data["subsession_data"][subsession_id].keys():
            result_rows.append(["team", "events", "not", "supported"])
            lap_rows.append([])
            continue
        for simsession_num in (_all_data["subsession_data"]
                                [subsession_id]):
            if simsession_num == "metadata":
                continue
            for curr_cust_id in (_all_data["subsession_data"]
                                [subsession_id]
                                [simsession_num]):
                curr_cust_id = int(curr_cust_id)
                #if no cust_id passed in, we want all. If we did pass in a cust id
                #we only want to append that customers data
                if not cust_id or cust_id == curr_cust_id:
                    #ugly but it's just concatenating the metadata, results, and lap math
                    curr_row = ((_all_data["subsession_data"]
                                    [subsession_id]
                                    ["metadata"]) +
                                (_all_data["subsession_data"]
                                [subsession_id]
                                [simsession_num]
                                [curr_cust_id]
                                ["results"]) + 
                                (_all_data["subsession_data"]
                                    [subsession_id]
                                    [simsession_num]
                                    [curr_cust_id]
                                    ["lap_math"]))


                    curr_lap_row = ([subsession_id, curr_cust_id] + 
                                    ([_all_data["subsession_data"]
                                    [subsession_id]
                                    [simsession_num]
                                    [curr_cust_id]
                                    ["name"]]) +
                                    (_all_data["subsession_data"]
                                    [subsession_id]
                                    [simsession_num]
                                    [curr_cust_id]
                                    ["laps"]))
                    result_rows.append(curr_row)
                    lap_rows.append(curr_lap_row)
    return result_rows, lap_rows

"""
Collates all rows to print (including the title rows)
Calls "organize_data"

Parameters:
    cust_id : int
    lap_row_headers : list
        #maybe we don't need this because we have the private variable

Return Values:
    result_rows : list
        #rows to be added to the *_consistency csv
    lap_rows : list
        #rows to be added to the *_laps csv
"""
def get_all_data_to_print(cust_id, lap_row_headers):
    result_rows = [_all_data["column_headers"]]
    lap_rows = [lap_row_headers]
    all_result_rows, all_lap_rows = organize_data(cust_id)

    result_rows = result_rows + all_result_rows
    lap_rows = lap_rows + all_lap_rows

    return result_rows, lap_rows

"""
Writes the data given to a csv

Parameters:
    filename : string
    rows : list

Return Values:
    None
"""
def write_to_file(filename, rows):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        filewriter = csv.writer(csvfile,
                                delimiter=',',
                                quotechar='|',
                                quoting=csv.QUOTE_MINIMAL)
        for row in rows:
            filewriter.writerow(row)

"""
Creates the title row for *_laps csv

Parameters:
    None

Return Values:
    lap_title_row : list
"""
def init_lap_row_headers():
    lap_title_row = ['subession_id', 'cust_id', 'name']
    for i in range(500):
        lap_title_row.append(str(i))

    return lap_title_row

"""
Figures out which subset of subsession IDs we need to look up, and looks them up
We can use:
    A customer ID with:
        last_x OR
        year
        season (if season, you need year)
    A subsession ID
    A series ID with:
        year AND
        season

Parameters:
    cust_id : int
    subsession_id : int
    last_x : int
    series_id : int
    year : int
    season : int

Return Values:
    all_subsession_ids : list
"""
def get_subession_id_list(cust_id=None, subsession_id=None, last_x=None, series_id=None, year=None, season=None):
    all_subsession_ids = []
    if series_id and (not year or not season):
        raise RuntimeError("If you provide a series, you must also provide a year AND season")
    if not year and season:
        raise RuntimeError("If you provide a season, you must also provide a year")
    if not subsession_id:
        all_subsession_ids = get_all_subsessions(cust_id, series_id, year, season)
        if last_x:
            last_x = -1*int(last_x)
            all_subsession_ids = all_subsession_ids[last_x:]
    else:
        all_subsession_ids = [subsession_id]

    return all_subsession_ids

"""
Finds the Race-session related simsessions for a given subsession (i.e. if there a heats, get each heat)

Parameters:
    subsession : dict

Return Values:
    simsession_numbers : list
"""
def get_simsession_numbers(subsession=None):
    if not subsession:
        raise RuntimeError("Missing subsession")
    simsession_numbers = []
    for session in subsession["session_results"]:
        if session["simsession_type"] == 6:
            simsession_numbers.append(session["simsession_number"])

    return simsession_numbers

"""
Uses the "get_all_session_laps" function to write to _all_data dictionary

Parameters:
    subsession : dict
    customers : list
    is_team_event : bool
    cust_id : int

Return Values:
    None
"""
def get_laps(subsession=None, customers=None, is_team_event=False, cust_id=None):
    if is_team_event:
        return []
    if not subsession:
        raise RuntimeError("Missing subsession")
    if not customers:
        raise RuntimeError("Missing customer id list")
    simsession_numbers = get_simsession_numbers(subsession)
    subsession_id = subsession["subsession_id"]


    for simsession_num in simsession_numbers:
        get_all_session_laps(subsession_id=subsession_id, 
            customers=customers, 
            simsession_number=simsession_num,
            cust_id=cust_id)

"""
Calculates the car numbers in order from highest irating to lowest
Uses _all_data then cust_id irating to order
Probably a good opportunity to refactor because there's lookup, sorting, writing which
    may be suboptimal with a first pass

Maybe rename to "write_car_numbers_to_data"?

Paramters:
    subsession : dict
    is_team_event : bool

Return Values:
    None
"""
def get_car_numbers(subsession, is_team_event=False):
    if is_team_event:
        return
    car_number_dict = {}
    #the plan is to go through each car class, and have a cust_id : starti_rating map
    #then sort that car_class dict, then assign the car number to each cust_id
    #it's not optimal, but this could be a prime candidate to refactor next
    simsession_numbers = get_simsession_numbers(subsession)

    for session in subsession["session_results"]:
        if session["simsession_number"] in simsession_numbers:
            car_number_dict[session["simsession_number"]] = {}
            for result in session["results"]:
                if result["car_class_id"] not in car_number_dict[session["simsession_number"]].keys():
                    (car_number_dict[session["simsession_number"]]
                        [result["car_class_id"]]) = {}
                    
                (car_number_dict[session["simsession_number"]]
                    [result["car_class_id"]]
                    [result["cust_id"]]) = int(result["oldi_rating"])

            #now to sort
            #stack overflow link: https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
            for car_class_id in car_number_dict[session["simsession_number"]].keys():
                car_number_dict[session["simsession_number"]][car_class_id] = dict(sorted((car_number_dict[session["simsession_number"]]
                                                                                        [car_class_id]).items(), key=operator.itemgetter(1), reverse=True))

                #now that the ratings are sorted, apply the car numbers to the cust_id
                curr_car_num=1
                for cust_id in car_number_dict[session["simsession_number"]][car_class_id]:
                    (_all_data["subsession_data"]
                        [subsession["subsession_id"]]
                        [session["simsession_number"]]
                        [cust_id]
                        ["results"]).append(curr_car_num)
                    curr_car_num = curr_car_num+1

"""
initiates lap math for all simsessions in all subsessions

Parameters:
    cust_id : int

Return Values:
    None
"""   
def lapmath_looper(cust_id=None):
    # lapmath_looping_time = time.time()
    subsession_ids = _all_data["subsession_data"].keys()

    for subsession_id in subsession_ids:
        simsession_numbers = (_all_data["subsession_data"]
                                [subsession_id].keys())
        #don't need to do lapmath in team events yet
        if "team_event" in simsession_numbers:
            continue
        for simsession_number in simsession_numbers:
            if simsession_number == "metadata":
                continue
            cust_ids = (_all_data["subsession_data"]
                            [subsession_id]
                            [simsession_number].keys())
            for curr_cust_id in cust_ids:
                if cust_id and curr_cust_id != cust_id:
                    continue
                curr_laps = (_all_data["subsession_data"]
                                [subsession_id]
                                [simsession_number]
                                [curr_cust_id]
                                ["laps"])
                clean_laps = (_all_data["subsession_data"]
                                [subsession_id]
                                [simsession_number]
                                [curr_cust_id]
                                ["clean_laps"])
                lap_math = do_lap_math(laps_for_race=curr_laps, clean_lap_count=clean_laps)
                (_all_data["subsession_data"]
                                [subsession_id]
                                [simsession_number]
                                [curr_cust_id]
                                ["lap_math"]) = lap_math

"""
loops through the subession IDs and gets the subsessions, then calls the other functions
related to the subessions:

Calls:
    get_subsession
    get_subsession_metadata
    get_cust_ids_in_subsession
    get_subsession_race_results
    get_car_numbers
    get_laps

Parameters:
    subsession_id_list : list
    cust_id : int

Return Values:
    None
"""
def subsession_looper(subsession_id_list=None, cust_id=None):
    # subsession_looping_time = time.time()
    for subsession_id in subsession_id_list:
        print('working on subsession: ' + str(subsession_id))
        subses = get_subsession(subsession_id)
        metadata = get_subsession_metadata(subses)
        customers, names = get_cust_ids_in_subsession(subses)
        race_results, is_team_event = get_subsession_race_results(subses)
        get_car_numbers(subses, is_team_event)
        laps = get_laps(subses, customers, is_team_event, cust_id)
        #by this point all data is in _all_data dict

"""
Creates the filenames given what information was passed into the file

Parameters:
    cust_id : int
    subsession_id : int
    last_x : int
    series_id : int
    year : int
    season : int

Return Values:
    result_filename : str
    lap_filename : str
"""
def get_filenames(cust_id=None, subsession_id=None, last_x=None, series_id=None, year=None, season=None):
    base_filename = ''

    if cust_id:
        base_filename = base_filename + 'cust_' + str(cust_id) + '_'

    if subsession_id:
        base_filename = base_filename + 'subsession_' + str(subsession_id) + '_'

    if cust_id and last_x:
        base_filename = base_filename + 'last_' + str(last_x) + '_'

    if series_id:
        base_filename = base_filename + 'series_' + str(series_id) + '_'

    if year:
        base_filename = base_filename + 'year_' + str(year) + '_'

    if season:
        base_filename = base_filename + 'season_' + str(season) + '_'

    result_filename = base_filename + 'results.csv'
    lap_filename = base_filename + 'laps.csv'

    return result_filename, lap_filename

"""
every good codebase has a main function :) (I think?)

Validate that we have enough information to actually run the entire script
Convert string input values to int values (it caused issues with comparing str to int equivalencies)
Print out the input values to std out just because

Initiate headers with init_lap_row_headers
Get subsession IDs to use with get_subsession_id_list
call subsession_looper
call lapmath_looper

Get the data to print into rows
get the filenames to print to

Write the data to the csv

Parameters:
    cust_id : int
    subsession_id : int
    last_x : int
    series_id : int
    year : int
    season : int

Return Values:
    None
"""
def main(cust_id=None, subsession_id=None, last_x=None, series_id=None, year=None, season=None):
    if not (cust_id or subsession_id or series_id):
        raise RuntimeError("Please supply a customer id, series id, or subsession id")
    if cust_id:
        cust_id = int(cust_id)
    if series_id:
        series_id = int(series_id)
    if year:
        year = int(year)
    if season:
        season = int(season)
    print('customer id    : ' + str(cust_id))
    print('subsession id  : ' + str(subsession_id))
    print('series id      : ' + str(series_id))
    print('year           : ' + str(year))
    print('season         : ' + str(season))

    lap_row_headers = init_lap_row_headers()

    subsession_id_list = get_subession_id_list(cust_id, subsession_id, last_x, series_id, year, season)
    subsession_looper(subsession_id_list, cust_id)
    lapmath_looper(cust_id)
    #all the data is now in _all_data
    
    #determine what to write
    result_rows_to_print, lap_rows_to_print = get_all_data_to_print(cust_id, lap_row_headers)

    #where to write to
        #where to write to
    result_filename, lap_filename = get_filenames(cust_id=cust_id, 
                                            subsession_id=subsession_id, 
                                            last_x=last_x,
                                            series_id=series_id,
                                            year=year,
                                            season=season)

    print(result_filename)
    print(lap_filename)
    #write it
    write_to_file(result_filename, result_rows_to_print)
    write_to_file(lap_filename, lap_rows_to_print)

#call main (include a specific subsession ID for single race analysis)
main(cust_id=_cust_id, subsession_id=_subsession_id, last_x=_last_x, series_id=_series_id, year=_year, season=_season)