import csv
import os
import sqlite3

import re

# Resolve the resources folder relative to this file, so paths work
# no matter what directory the script is run from.
_RESOURCES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'resources')

# Connect to the SQLite in-memory database
conn = sqlite3.connect(':memory:')

# A cursor object to execute SQL commands
cursor = conn.cursor()


def main():

    # users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        userId INTEGER PRIMARY KEY,
                        firstName TEXT,
                        lastName TEXT
                      )'''
                   )

    # callLogs table (with FK to users table)
    cursor.execute('''CREATE TABLE IF NOT EXISTS callLogs (
        callId INTEGER PRIMARY KEY,
        phoneNumber TEXT,
        startTime INTEGER,
        endTime INTEGER,
        direction TEXT,
        userId INTEGER,
        FOREIGN KEY (userId) REFERENCES users(userId)
    )''')

    # You will implement these methods below. They just print TO-DO messages for now.
    load_and_clean_users(os.path.join(_RESOURCES_DIR, 'users.csv'))
    load_and_clean_call_logs(os.path.join(_RESOURCES_DIR, 'callLogs.csv'))
    write_user_analytics(os.path.join(_RESOURCES_DIR, 'userAnalytics.csv'))
    write_ordered_calls(os.path.join(_RESOURCES_DIR, 'orderedCalls.csv'))

    # Helper method that prints the contents of the users and callLogs tables. Uncomment to see data.
    # select_from_users_and_call_logs()

    # Close the cursor and connection. main function ends here.
    cursor.close()
    conn.close()


# TODO: Implement the following 4 functions. The functions must pass the unit tests to complete the project.


# This function will load the users.csv file into the users table, discarding any records with incomplete data
def load_and_clean_users(file_path):

    raw_users = []
    with open(file_path, "r") as f:
        raw_users = list(csv.DictReader(f))
    
    for raw_user in raw_users:

        # Skip row if incorrect number of fields
        if len(raw_user) != 2:
            continue

        # Skip row if firstName or lastName is not purely alphabetic characters
        if not re.match('[a-zA-Z]+$', raw_user['firstName']) or not re.match('[a-zA-Z]+$', raw_user['lastName']):
            continue

        # Insert row into the users table
        cursor.execute('''
            INSERT INTO users (firstName, lastName)
            VALUES (?, ?);
        ''', (raw_user['firstName'], raw_user['lastName']))


# This function will load the callLogs.csv file into the callLogs table, discarding any records with incomplete data
def load_and_clean_call_logs(file_path):

    raw_call_logs = []
    with open(file_path, "r") as f:
        raw_call_logs = list(csv.DictReader(f))

    for raw_log in raw_call_logs:

        # Skip row if incorrect number of fields
        if len(raw_log) != 5:
            continue

        # Skip row if phone number is invalid
        if not re.match(r'^\d{3}-\d{3}-\d{4}$', raw_log['phoneNumber']):
            continue

        # Skip row if startTime, endTime, or userId are not purely numeric
        if not re.match('^[0-9]+$', raw_log['startTime']) or not re.match('^[0-9]+$', raw_log['endTime']) or not re.match('^[0-9]+$', raw_log['userId']):
            continue

        # Skip row if direction is invalid
        if raw_log['direction'] != 'outbound' and raw_log['direction'] != 'inbound':
            continue

        # Insert the validated row into the callLogs table
        cursor.execute('''
            INSERT INTO callLogs (phoneNumber, startTime, endTime, direction, userId)
            VALUES (?, ?, ?, ?, ?);
        ''', (raw_log['phoneNumber'], raw_log['startTime'], raw_log['endTime'], raw_log['direction'], raw_log['userId']))


# This function will write analytics data to testUserAnalytics.csv - average call time, and number of calls per user.
# You must save records consisting of each userId, avgDuration, and numCalls
# example: 1,105.0,4 - where 1 is the userId, 105.0 is the avgDuration, and 4 is the numCalls.
def write_user_analytics(csv_file_path):

    cursor.execute('''
        SELECT userId, AVG(endTime - startTime), COUNT(*)
        FROM callLogs
        GROUP BY userId;
    ''')
    callLogs = cursor.fetchall()

    with open(csv_file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['userId', 'avgDuration', 'numCalls'])
        writer.writerows(callLogs)


# This function will write the callLogs ordered by userId, then start time.
# Then, write the ordered callLogs to orderedCalls.csv
def write_ordered_calls(csv_file_path):

    cursor.execute('''
        SELECT callId, phoneNumber, startTime, endTime, direction, userId
        FROM callLogs
        ORDER BY userId;
    ''')
    callLogs = cursor.fetchall()

    with open(csv_file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['callId', 'phoneNumber', 'startTime', 'endTime', 'direction', 'userId'])
        writer.writerows(callLogs)



# No need to touch the functions below!------------------------------------------

# This function is for debugs/validation - uncomment the function invocation in main() to see the data in the database.
def select_from_users_and_call_logs():

    print()
    print("PRINTING DATA FROM USERS")
    print("-------------------------")

    # Select and print users data
    cursor.execute('''SELECT * FROM users''')
    for row in cursor:
        print(row)

    # new line
    print()
    print("PRINTING DATA FROM CALLLOGS")
    print("-------------------------")

    # Select and print callLogs data
    cursor.execute('''SELECT * FROM callLogs''')
    for row in cursor:
        print(row)


def return_cursor():
    return cursor


if __name__ == '__main__':
    main()