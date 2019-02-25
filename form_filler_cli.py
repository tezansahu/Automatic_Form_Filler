import argparse
import urllib
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os.path
 
def main(args):
    if args.url == None or args.csv_input == None:
        print("Please enter valid Form URL and CSV Input File")
        exit()
    if not os.path.isfile(args.csv_input):
        print("CSV file does not exist! Please check the file name...")
        exit()
    if args.max_delay < args.min_delay:
        print("Maximum Delay cannot be less than Minimum Delay!")
        exit()
    try:
        # url = "https://docs.google.com/forms/d/e/1FAIpQLSfNo0-VE_B7jB1I7bBz8HrtkN9VbCZ-eiMb1U72AzBzk0vSQQ/viewform"
        url = args.url
        res = urllib.request.urlopen(url)

        df = pd.read_csv(args.csv_input)
        avg_delay = (args.min_delay + args.max_delay)/2
        if args.start_index > df.shape[0] - 1:
            print("No entry to be submitted!")
            exit()

        if args.num_entries == None:
            num_entries = df.shape[0] - args.start_index
        elif args.num_entries > df.shape[0]:
            num_entries = df.shape[0]
        else:
            num_entries = args.num_entries

        est_time = avg_delay * num_entries  # in s
        print("------------------------------------------------------")
        if est_time > 60:
            print("Total Entries: ", num_entries, "\tEstimated time of Completion: ", est_time/60, " min")
        else:
            print("Total Entries: ", num_entries, "\tEstimated time of Completion: ", est_time, " s")
        print("------------------------------------------------------")

        

        soup = BeautifulSoup(res.read(), 'html.parser')
        get_names = lambda f: [v for k,v in f.attrs.items() if 'label' in k]
        get_name = lambda f: get_names(f)[0] if len(get_names(f))>0 else 'unknown'
        all_questions = soup.form.findChildren(attrs={'name': lambda x: x and x.startswith('entry.')})
        fields = {get_name(q): q['name'] for q in all_questions}
        # print(fields)
        user_agent = {'Referer':url,'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}

        
        for i in range(args.start_index, args.start_index + num_entries):
            form_data = {'draftResponse':[],
                            'pageHistory':0}
            for v in fields.values():
                    form_data[v] = ''
            for k in fields.keys():
                for col in df.columns:
                    if k.lower() == col.lower():
                        form_data[fields[k]] = df.iloc[i][col]
            requests.post(url.replace('/viewform', '/formResponse'), data=form_data, headers=user_agent)
            est_time -= avg_delay
            if est_time > 60:
                print("Entry ", i, "submitted \tEstimated time of Completion: ", est_time/60, " min")
            else:
                print("Entry ", i, "submitted \tEstimated time of Completion: ", est_time, " s")

            if i != args.start_index + num_entries-1:
                delay = random.randint(args.min_delay, args.max_delay+1)
                time.sleep(delay)
        
        print("------------------------------------------------------")
        print("All entries submitted successfully!!!")
    except Exception as e:
        if str(e) == "HTTP Error 404: Not Found":
            print("Invalid URL: Google form not found!")
        else:
            # print(e)
            print("Sorry! Unexpected Error!")

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