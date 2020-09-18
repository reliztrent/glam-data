#!/usr/bin/python3

import sys 
import os
import getopt
import time
import json
import requests
import pandas as pd

def generate_output_folder(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)


def query(url, items=[],x=0):
    max_retries = 5
    if x < max_retries:
        params = {"fo": "json", "c": 200, "at": "results,pagination,facets"}
        request = requests.get(url, params=params)
        if (request.status_code==200) & ('json' in request.headers.get('content-type')):
            data = request.json()
            results = data['results']
            for result in results:
                filter_out = ("collection" in result.get("original_format")) \
                        or ("web page" in result.get("original_format"))
                if not filter_out:
                    items.append(result)
            # Repeat the loop on the next page, unless we're on the last page. 
            if data["pagination"]["next"] is not None: 
                next_url = data["pagination"]["next"]
                query(next_url, items)

            return items
        elif request.status_code in range(500, 505):
            x += 1
            time.sleep(10)
            query(url,items,x)
        else:
            return items
    else:
        return items

def json_output(items): 
    print('Making a json file of new gmd.mar items at: '+ 
        directory + 'new_gmdmar_items_' + end_date + '.json')
    #Create df from items
    modified = pd.DataFrame(items)
    #Create df from existing json of all gmdmar items
    baseline = pd.read_json('docs/_data/gmdmar-all-items.json')
    #Update metadata in baseline rows that have been modified
    modified.set_index('id', inplace=True)
    baseline.set_index('id', inplace=True)
    baseline.update(modified)
    baseline.reset_index(inplace=True)
    #Add new rows to baseline
    match = pd.merge(
        baseline,
        modified,
        on='id',
        how='left',
        suffixes = ('', '_drop'),
        indicator=True
    )
    #Drop extra columns created from modified rows
    match.drop(match.filter(regex='_drop').columns, axis=1, inplace=True)
    #New items are those not already in the baseline
    new=match[match['_merge']=="right_only"].copy()
    new.drop('_merge', axis=1, inplace=True)
    #Save new items to json file
    new.to_json(
        directory + 'new_gmdmar_items_' + end_date + '.json', 
        orient='records'
        )
    #Update the baseline file with new items and updated metadata on mod'd items
    print('Updating the baseline file of all gmd.mar items at: \
        docs/_data/gmdmar-all-items.json')
    match.drop('_merge', axis=1, inplace=True)
    match.to_json('docs/_data/gmdmar-all-items.json', orient='records')
    
def main(argv):
    start_date = ''
    end_date = ''
    try:
        opts, args = getopt.getopt(argv,"hs:e:d:",["start=","end=","directory="])
    except getopt.GetoptError:
        print ('loc_json.py -s <start_date (YYYY-MM-DD)> -e <end_date (YYYY-MM-DD)> -d <directory>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('loc_json.py -s <start_date (YYYY-MM-DD)> -e <end_date (YYYY-MM-DD)> -d <directory>')
            sys.exit()
        elif opt in ("-s", "--start_date"):
            start_date = arg
        elif opt in ("-e", "--end_date"):
            end_date = arg
        elif opt in ("-d", "--directory"):
            directory = arg
    print ('Start date is ', start_date)
    print ('End date is ', end_date)
    url = 'https://www.loc.gov/search/?fo=json&sb=shelf-id&sq=group:gmd.mar+AND+number_source_modified:[' + start_date + ' TO ' + end_date + ']'
    print("Query URL is: ", url)
    items = query (url,[])

    if len(items) > 0:
    	json_output(items)

    


if __name__ == "__main__":
    main(sys.argv[1:])

