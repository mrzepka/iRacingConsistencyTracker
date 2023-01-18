# This is the API wrapper I leaned on, but I had to add some functionality
#https://github.com/jasondilworth56/iracingdataapi
# from iracingdataapi.client import irDataClient
#irapi.py is the file that houses the API linked above with some clobbering to get
# search_series endpoint working
import sys, statistics, csv
sys.path.insert(0,"iracingdataapi\src\iracingdataapi")
from client import irDataClient

#create data client that does all the work
idc = irDataClient(username="<your iracing email>", password="<your iracing password>")

#Private Variables! :D
#I'm sure there's a better way to do this
_years = [2008, 
            2009, 
            2010, 
            2011, 
            2012, 
            2013, 
            2014, 
            2015, 
            2016, 
            2017, 
            2018, 
            2019, 
            2020, 
            2021, 
            2022,
            2023]

#also this
_seasons = [1, 2, 3, 4]

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#please update this to whatever customer ID you want to get data for
_cust_id = <customer ID to look up>

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#please update this to whatever subsession ID you want to get data for
_subsession_id = <subsession ID to look up>

#more for reference than use
_event_types = [{'label': 'Practice', 'value': 2}, 
                {'label': 'Qualify', 'value': 3}, 
                {'label': 'Time Trial', 'value': 4}, 
                {'label': 'Race', 'value': 5}]

#just so that the columns are labeled
_title_row_cust = ["Subsession ID",
                "License Category", 
                "Year", 
                "Season", 
                "Series", 
                "SOF", 
                "Track", 
                "Track Configuration", 
                "Car", 
                "Starting Position",
                "Finishing Position", 
                "Positions Gained/Lost",
                "iRating", 
                "iRating Change", 
                "Incidents",
                "Average Lap", 
                "Fastest Lap", 
                "Consistency",
                "Lap Standard Dev",
                "Normalized Lap Standard Dev"]

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
                            "Average Lap",
                            "Fastest Lap",
                            "Consistency",
                            "Standard Deviation",
                            "Adjusted Standard Deviation",
                            "Percent Normal Laps",
                            "Clean Laps",
                            "Clean Lap Percent"]

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

#Functions!

def get_cust_ids_in_subsession(subsession=None):
    if not subsession:
        raise RuntimeError("Please supply subsession that is not None")
    race_result_index = len(subsession["session_results"])-1
    all_results = subsession["session_results"][race_result_index]["results"]
    customer_ids = []
    driver_names = []
    for result in all_results:
        # print(result["cust_id"])
        customer_ids.append(result["cust_id"])
        driver_names.append(result["display_name"])

    return customer_ids, driver_names


#lap information gathering
def get_lap_data_for_subsession_and_cust(subsession_id=None, cust_id=None):
    if not cust_id:
        raise RuntimeError("Please supply customer ID")
    if not subsession_id:
        raise RuntimeError("Please supply subsession ID")
    lap_results = idc.result_lap_data(subsession_id=subsession_id, cust_id=cust_id)
    laptime_list = []
    clean_laps = 0
    if lap_results:
        for lap in lap_results:
            # print(lap)
            if lap["lap_number"] == 0:
                continue
            if not lap["incident"]:
                clean_laps = clean_laps + 1
            laptime_list.append(lap["lap_time"]/10000)
    return laptime_list, clean_laps

def get_all_session_laps(subsession_id, customers, names):
    lap_list_list = []
    clean_lap_counts = []
    i=0
    for customer in customers:
        meta = [subsession_id, customer, names[i]]
        laps, clean_lap_count = get_lap_data_for_subsession_and_cust(subsession_id, customer)
        lap_list_list.append(meta + laps)
        clean_lap_counts.append(clean_lap_count)
        i=i+1
    #clean lap count isn't used for all session data... yet..
    return lap_list_list, clean_lap_counts

def get_subsession(subsession_id=None):
    if not subsession_id:
        raise RuntimeError("Please supply subsession ID")
    subsession = idc.result(subsession_id=subsession_id)
    return subsession

def get_subsession_metadata(subsession=None):
    if not subsession:
        raise RuntimeError("Please supply subsession")
    metadata = []
    metadata.append(subsession["subsession_id"])
    metadata.append(subsession["license_category"])
    metadata.append(subsession["season_year"])
    metadata.append(subsession["season_quarter"])
    metadata.append(subsession["series_short_name"])
    metadata.append(subsession["event_strength_of_field"])
    metadata.append(subsession["track"]["track_name"])
    metadata.append(subsession["track"]["config_name"])
    return metadata

def get_subsession_race_results(subsession=None, cust_id=None):
    if not subsession:
        raise RuntimeError("Please supply subsession")
    race_session_index = len(subsession["session_results"])-1
    race_results = subsession["session_results"][race_session_index]["results"]
    data = []
    for results in race_results:
        result_row = []
        #if it's a team
        if "team_id" in results.keys():
            return [['team event not yet handled']], True
        #if it's a single customer
        if cust_id:
            if results["cust_id"] == cust_id:
                for item in results:
                    if item in _exclude_fields:
                        continue
                    if item in ["position", 
                            "starting_position", 
                            "starting_position_in_class",
                            "finish_position",
                            "finish_position_in_class"]:

                        result_row.append(results[item]+1)
                    else:
                        result_row.append(results[item])
                result_row.append(results["newi_rating"] - results["oldi_rating"])
                result_row.append(results["starting_position_in_class"] - results["finish_position_in_class"])
                data.append(result_row)
                return data, False
        else:
            #if we're getting all data
            for item in results:
                # print(item)
                if item in _exclude_fields:
                    continue
                if item in ["position", 
                            "starting_position", 
                            "starting_position_in_class",
                            "finish_position",
                            "finish_position_in_class"]:

                    result_row.append(results[item]+1)
                else:
                    result_row.append(results[item])
            result_row.append(results["newi_rating"] - results["oldi_rating"])
            result_row.append(results["starting_position_in_class"] - results["finish_position_in_class"])
            data.append(result_row)
    return data, False

#get all subsessions for the customer id provided
def get_all_subsessions(cust_id=None):
    if not cust_id:
        raise RuntimeError("Please supply customer ID")
    all_series_data = []
    for year in _years:
        for season in _seasons:
            print('looking up season ' + str(season) + ' year ' + str(year))
            series_data_for_season = idc.search_series(season_year=year, season_quarter=season, cust_id=cust_id, event_types=5)
            all_series_data = all_series_data + series_data_for_season

    all_subsession_ids = []
    for session in all_series_data:
        all_subsession_ids.append(session["subsession_id"])

    return all_subsession_ids

def remove_outlier_laps(laps, avg):
    delta = 0
    valid_laptimes = []
    for lap in laps:
        d2 = 0
        delta = 0
        delta = delta + abs(lap-avg)
        d2 = delta * delta
        # print(d2)
        if d2 < 100:
            valid_laptimes.append(lap)
    return valid_laptimes



#hiding the standard deviation math from the lap_math function 
def get_standard_deviation_of_laps(laps):
    positive_laps = []
    #don't count weird negative or impossible laptimes
    for lap in laps:
        if lap > 1:
            positive_laps.append(lap)
    if len(positive_laps) > 1:
        return statistics.stdev(positive_laps)
    else:
        return 0

def get_average_laptime_of_laps(laps):
    positive_laps = []
    #don't count weird negative or impossible laptimes
    for lap in laps:
        if lap > 1:
            positive_laps.append(lap)
    if len(positive_laps) > 1:
        return statistics.mean(positive_laps)
    else:
        return 0

def get_fastest_laptime_of_laps(laps):
    positive_laps = []
    #don't count weird negative or impossible laptimes
    for lap in laps:
        if lap > 1:
            positive_laps.append(lap)

    if len(positive_laps) > 1:
        return min(positive_laps)
    else:
        return 0

#handles all the lap math we want to do with the laptimes
def do_lap_math(laps_for_race, clean_lap_count):
    if laps_for_race and len(laps_for_race) > 1:
        print(laps_for_race)
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

#Getting data for specific customer
def get_cust_data(cust_id, subsession_id=None):
    if not subsession_id:
        my_race_ids = get_all_subsessions(_cust_id)
    else:
        my_race_ids = [subsession_id]

    all_rows = []
    all_lap_rows = []
    for race_id in my_race_ids:
        print('working on subsession: ' + str(race_id))
        subses = get_subsession(race_id)
        metadata = get_subsession_metadata(subses)
        race_results, is_team_event = get_subsession_race_results(subses, cust_id)

        if len(race_results)>0:
            curr_row = metadata + race_results[0]
        else:
            curr_row = metadata

        if not is_team_event:
            laps_for_race, clean_lap_count = get_lap_data_for_subsession_and_cust(race_id, cust_id)
            lap_math_results = do_lap_math(laps_for_race, clean_lap_count)
        else:
            lap_math_results = ['team', 'events', 'not', 'supported']
        
        all_rows.append(curr_row + lap_math_results)
        #append subsession ID and cust_id laps just in case
        all_lap_rows.append([race_id] + [cust_id] + laps_for_race)

    return all_rows, all_lap_rows

def get_all_single_session_data(subsession_id):
    subses = get_subsession(subsession_id)
    customers, names = get_cust_ids_in_subsession(subses)
    metadata = get_subsession_metadata(subses)
    race_results, is_team_event = get_subsession_race_results(subses)
    print('race results are: ')
    print(race_results)

    print('metadata is:')
    print(metadata)

    for i in range(len(race_results)):
        race_results[i] = metadata + race_results[i]
    laps = [[]]
    if not is_team_event:
        laps, clean_lap_counts = get_all_session_laps(subsession_id, customers, names)
        index = 0
        for lap_list in laps:
            lap_math_results = do_lap_math(lap_list[3:], clean_lap_counts[index])
            race_results[index] = race_results[index] + lap_math_results
            index = index + 1

    return race_results, laps

def write_to_file(filename, rows):
    with open(filename, 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile,
                                delimiter=',',
                                quotechar='|',
                                quoting=csv.QUOTE_MINIMAL)
        for row in rows:
            print(row)
            filewriter.writerow(row)

#every good codebase has a main function :)
def main(cust_id=None, subsession_id=None):
    if not (cust_id or subsession_id):
        raise RuntimeError("Please supply either customer id or subsession id, or both")
    print(cust_id)
    print(subsession_id)

    rows = []
    lap_rows = []
    lap_title_row = ['subession_id', 'cust_id']
    for i in range(500):
        lap_title_row.append(str(i))

    lap_rows.append(lap_title_row)

    filename = 'sometehing_went_wrong_if_this_is_the_filename.csv'
    if cust_id:
        if subsession_id:
            filename = 'subsession_' + str(subsession_id) + '_cust_' + str(cust_id) + '_consistency.csv'
            laps_filename = 'subsession_' + str(subsession_id) + '_cust_' + str(cust_id) + '_consistency_laps.csv'
        else:
            filename = 'cust_' + str(cust_id) + '_consistency.csv'
            laps_filename = 'cust_' + str(cust_id) + '_consistency_laps.csv'
        rows.append(_title_row_session_only)

        data, laps = get_cust_data(cust_id, subsession_id)

        rows = rows + data
        lap_rows = lap_rows + laps
    else:
        filename = 'subsession_' + str(subsession_id) + '_info.csv'
        laps_filename = 'subsession_' + str(subsession_id) + '_info_laps.csv'

        session_results, laps = get_all_single_session_data(subsession_id)

        rows.append(_title_row_session_only)
        rows = rows + session_results
        lap_rows = lap_rows + laps

    write_to_file(filename, rows)
    write_to_file(laps_filename, lap_rows)

#call main (include a specific subsession ID for single race analysis)
main(cust_id=_cust_id, subsession_id=_subsession_id)