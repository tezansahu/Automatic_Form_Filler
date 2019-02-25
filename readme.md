## Automatic Form Filler

#### This is a tool that could be used to automatically fill Google Forms using data from a CSV file.

### To use the CLI version of the tool, follow the following steps:

1. Clone this repository to your local system using `git clone https://github.com/tezansahu/Automatic_Form_Filler.git`</li>

2. Use Pip3 to install all the python dependencies from `requirements.txt`:
```
$ pip3 install -r requirements.txt
```
3. Now, you are ready to use the command line tool by typing the following command:
```
$ python3 form_filler_cli --form-url <URL_of_Google_Form> --csv-input <Input_CSV_file_name> --start-index <Index_of_CSV_file_to_start> --num-entries <Number_of_entries_to_be_submitted> --min-delay <Minimum_delay_time_between_2_POST_requests> --max-delay <Maximum_delay_time_between_2_POST_requests>
```
### Default Values of Parameters:
* **start-index:** 0
* **num-entries:** Total number of rows in the CSV input file
* **min-delay:** 60 seconds (1 min)  
* **max-delay:** 120 seconds (2 min) 