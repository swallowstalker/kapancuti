from pymongo import MongoClient, ASCENDING
import json
from datetime import datetime
import os.path
from dateutil import tz
from dotenv import load_dotenv, find_dotenv
import argparse


load_dotenv(find_dotenv())

# init db to mongo
db = MongoClient(host=os.getenv('MONGO_HOST', "localhost"), port=int(os.getenv('MONGO_PORT', 27017))).get_database("kapancuti")
db.get_collection('holidays').create_index([('foremost_date', ASCENDING)])

parser = argparse.ArgumentParser(description='Import holiday data from JSON')
parser.add_argument('--file', '-f', help='import by filename', required=True)
args = parser.parse_args()

print('Import holiday data file at {location}'.format_map({'location': args.file}))

if args.file is None or not os.path.isfile(args.file):
    print('Holiday data file cannot be found at {location}'.format_map({'location': args.file}))
    exit(1)

jakarta_timezone = tz.gettz('Asia/Jakarta')

# retrieve holiday data from json
with open(args.file) as fp:
    json_bytes = fp.read()
    yearly_holidays = json.loads(json_bytes)

    for holiday in yearly_holidays:
        holiday['foremost_date'] = datetime.strptime(holiday['date_list'][0], '%Y-%m-%d').astimezone(jakarta_timezone)
        holiday_exist = db.get_collection('holidays').find_one({'foremost_date': holiday['foremost_date']})
        if holiday_exist:
            print("Holiday already exists: {name}".format_map({'name': holiday['description']}))
            continue

        holiday_datetimes = []
        for date_string in holiday['date_list']:
            holiday_datetimes.append(datetime.strptime(date_string, '%Y-%m-%d').astimezone(jakarta_timezone))
        holiday['date_list'] = holiday_datetimes

        if holiday['holiday_streak']['start'] is not None and holiday['holiday_streak']['end'] is not None:
            holiday['holiday_streak']['start'] = datetime.strptime(holiday['holiday_streak']['start'], '%Y-%m-%d')\
                .astimezone(jakarta_timezone)
            holiday['holiday_streak']['end'] = datetime.strptime(holiday['holiday_streak']['end'], '%Y-%m-%d')\
                .astimezone(jakarta_timezone)
        else:
            del holiday['holiday_streak']

        leave_recommendations_datetimes = []
        for date_string in holiday['leave_recommendation']:
            leave_recommendations_datetimes.append(datetime.strptime(date_string, '%Y-%m-%d').astimezone(jakarta_timezone))
        holiday['leave_recommendation'] = leave_recommendations_datetimes

        # insert holiday data to collections
        db.get_collection('holidays').insert_one(holiday)

print("Finished processing " + args.file + " holiday data")
