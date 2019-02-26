import argparse
import urllib
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os.path

def interrupt():
    print("Interrupting process...")
    time.sleep(2)
    exit()
 
def main(args):

    # Check validity & existence of URL and Input CSV File
    if args.url == None or args.csv_input == None:
        print("Please enter valid Form URL and CSV Input File")
        interrupt()
    if not os.path.isfile(args.csv_input):
        print("CSV file does not exist! Please check the file name...")
        interrupt()
    
    # Check if max delay and min delay are correct
    if args.max_delay < args.min_delay:
        print("Maximum Delay cannot be less than Minimum Delay!")
        interrupt()

    # url = "https://docs.google.com/forms/d/e/1FAIpQLSfNo0-VE_B7jB1I7bBz8HrtkN9VbCZ-eiMb1U72AzBzk0vSQQ/viewform"
    url = args.url

    # Check if the Google Form exists
    try:
        res = urllib.request.urlopen(url)
    except Exception as e:
        if str(e) == "HTTP Error 404: Not Found":
            print("Invalid URL: Google form not found!")
        else:
            print("Sorry! Unexpected Error! Please check the URL entered")
        interrupt()

    # Check if CSV file is readable
    try:
        df = pd.read_csv(args.csv_input)
    except Exception as e:
        print("Unable to read the CSV file")
        interrupt()

    avg_delay = (args.min_delay + args.max_delay)/2

    # Check if starting index lies within the range of rows in CSV file
    if args.start_index > df.shape[0] - 1:
        print("No entry to be submitted!")
        interrupt()

    # Set number of entries correctly
    if args.num_entries == None:
        num_entries = df.shape[0] - args.start_index
    elif args.num_entries > df.shape[0]:
        num_entries = df.shape[0]
    else:
        num_entries = args.num_entries

    est_time = avg_delay * num_entries  # in s

    # Print the initial stats of the process
    print("----------------------------------------------------------------")
    if est_time > 60:
        print("Total Entries:", num_entries, "\tEstimated time of Completion:", est_time/60, "min")
    else:
        print("Total Entries:", num_entries, "\tEstimated time of Completion:", est_time, "s")
    print("----------------------------------------------------------------")


    # Get the details of Form Questions and their corresponding IDs
    soup = BeautifulSoup(res.read(), 'html.parser')
    get_names = lambda f: [v for k,v in f.attrs.items() if 'label' in k]
    get_name = lambda f: get_names(f)[0] if len(get_names(f))>0 else 'unknown'
    all_questions = soup.form.findChildren(attrs={'name': lambda x: x and x.startswith('entry.')})
    fields = {get_name(q): q['name'] for q in all_questions}

    user_agent = {'Referer':url,'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}

    # Start filling the form using entries from the CSV File
    for i in range(args.start_index, args.start_index + num_entries):
        form_data = {'draftResponse':[],
                        'pageHistory':0}
        for v in fields.values():
                form_data[v] = ''
        
        # Check for matching column names and form questions
        try:
            for k in fields.keys():
                for col in df.columns:
                    if k.lower().strip() == col.lower().strip():
                        form_data[fields[k]] = df.iloc[i][col]
        except Exception as e:
            print("Entry", i, ": "+ str(e))
            interrupt()
            
        response = requests.post(url.replace('/viewform', '/formResponse'), data=form_data, headers=user_agent)
        
        # Check if response of submission is successful
        if str(response) != "<Response [200]>":
            print("Entry", i, "NOT submitted! Please check CSV File Headers and Submission Enabling in the form")
            interrupt()
            
        est_time -= avg_delay
        if est_time > 60:
            print("Entry", i, "submitted \tEstimated time of Completion:", est_time/60, "min")
        else:
            print("Entry", i, "submitted \tEstimated time of Completion:", est_time, "s")

        if i != args.start_index + num_entries-1:
            delay = random.randint(args.min_delay, args.max_delay+1)
            time.sleep(delay)
    
    print("----------------------------------------------------------------")
    print("All entries submitted successfully!!!")
    
# Receive arguments while running command on terminal
if __name__=="__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--form-url", action="store", dest="url", type=str, help="URL of the form to be filled")
    parser.add_argument("--csv-input", action="store", dest="csv_input", type=str, help="Name of CSV file to be used as input for the form")
    parser.add_argument("--start-index", action="store", dest="start_index", type=int, help="Index in CSV to start from", default=0)
    parser.add_argument("--num-entries", action="store", dest="num_entries", type=int, help="number of entries to be submitted", default = None)
    parser.add_argument("--min-delay", action="store", dest="min_delay", type=int, help="Minimum delay time between 2 POST requests (in seconds)", default=60)
    parser.add_argument("--max-delay", action="store", dest="max_delay", type=int, help="Maximum delay time between 2 POST requests (in seconds)", default=120)    
    args = parser.parse_args()

    main(args)