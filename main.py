import os
import re
from email import policy
from email.parser import BytesParser
from collections import Counter

#This function reads the names all the .eml files in the given directory
def read_directory(directory_path, list_of_files):
    eml_pattern = re.compile(r'\.eml$')
    for file_name in os.listdir(directory_path):
        if eml_pattern.search(file_name):
            absolute_filename = "Email-Receipts/" + file_name
            list_of_files.append(absolute_filename)

#Helper function to print the contents of an email
def print_email_contents(email_file_name):
    print("Email Contents Ex: ", email_file_name)

    #Open the file in binary mode
    with open(email_file_name, 'rb') as f:
        #Parse the email bytes
        email_contents = BytesParser(policy=policy.default).parse(f)
    
    #Print headers
    print(f"Subject: {email_contents['subject']}")
    print(f"From: {email_contents['from']}")
    print(f"To: {email_contents['to']}")

    #print("Printing body...")
    #Print email body. If multi part print the different parts
    if email_contents.is_multipart():
        #print("Email is multi part")
        for part in email_contents.iter_parts():
            #print("Iterating...")
            if part.get_content_type() == 'text/html':
                #print("Part is html")
                print(part.get_payload(decode=True).decode('utf-8'))
            else:
                print("Part is not html")
    #Print payload directly if not
    else:
        #print("Email is not multipart")
        print(part.get_payload(decode=True).decode('utf-8'))
    
    #print("Printing body done...")

#Helper function that gets the money spent from one receipt as well as the month and year
def get_money_and_date(email_file_name, dates_filled_up):
    money_spent = 0
    money_pattern = re.compile(r"Amount Paid: \$\d+\.\d{2}")
    date_pattern = re.compile(r"\b(0[1-9]|1[0-2])-\d{2}-(\d{4})\b") #Gets the month and year
    fill_date = ""

    #Open file
    with open(email_file_name, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
    
    #Get the body of the email
    email_contents = msg.get_body(preferencelist=('html'))

    if email_contents is None:
        print(f"Warning: No HTML body found in {email_file_name}")
        return 0, None
    
    email_body = email_contents.get_content()

    #Go through body and find the string that has the money spent as well as the date
    money_match = re.search(money_pattern, email_body)
    fill_date = re.search(date_pattern, email_body).group()

    dates_filled_up.append(fill_date)

    #Remove the text in front of the amount paid and convert it to a float
    money_spent = float(money_match.group().replace("Amount Paid: $", ""))
    
    #print("Date: ", fill_date, ", Money Spent: ", money_spent)
    
    return money_spent

#This helper function gets the average amount of times per month we filled up
def get_average_fill_ups(dates_filled_up):
    average_times_filled = 0.0
    times_filled_per_month = []
    
    #Go through dates and remove the day
    for i, date_formatted in enumerate(dates_filled_up):
        date_formatted = date_formatted[:2] + date_formatted[5:]
        dates_filled_up[i] = date_formatted
    
    #Create list with unique dates and how many times each one occurred
    times_filled_per_month = Counter(dates_filled_up)

    #Sort the unique dates
    times_filled_per_month = dict(sorted(times_filled_per_month.items(), key=lambda x: (int(x[0].split('-')[1]), int(x[0].split('-')[0]))))

    #Calculate the average amount of times filled per month
    average_times_filled = len(dates_filled_up)/len(times_filled_per_month)

    #print("Average Times Filled up: ", average_times_filled, ", Total times filled: ", len(dates_filled_up), ", Number of months: ", len(times_filled_per_month))
    print(times_filled_per_month)

    return average_times_filled

#This function reads the given files and calculates the average amount spent a month
def read_emails(list_of_files):
    total_money_spent = 0.0
    average_money_spent = 0.0
    average_times_filled = 0.0
    total_average_spent = 0.0
    dates_filled_up = []

    #Get total spent from all emails
    for file_name in list_of_files:
        total_money_spent += get_money_and_date(file_name, dates_filled_up)

    #Get the average spent across all fill ups
    average_money_spent = total_money_spent/len(list_of_files)

    #Go through all the dates and count how many times per month we filled up on average
    average_times_filled = get_average_fill_ups(dates_filled_up)

    #Calculate the amount of times per month we fill up
    total_average_spent = average_money_spent * average_times_filled

    print("Average Spent Per Fill Up: ", format(average_money_spent, ".2f"))
    print("Average Times Filled Up Per Month: ", format(average_times_filled, ".2f"))

    return total_average_spent

if __name__ == "__main__":
    list_of_files = [] #A list is mutable (passed by reference when passed to a function)
    total_average_spent = 0 #A float is not mutable
    read_directory("Email-Receipts", list_of_files)
    total_average_spent = read_emails(list_of_files)

    print("Number Of Times Filled: ", len(list_of_files))
    print("Average Money Spent On Gas Every Month: $", format(total_average_spent, ".2f"))
    