# api-endpoint-for-database-requests
Django based Rest API endpoint for retrieving specified information from a database

This is a Rest API written in Django and Python, with a custom handler, capable of receiving GET requests and sending back information from a database according to the parameters specified in the request URL.

The base URL is: (your local Django server host)/clicks_info/
With API flags: (your local Django server host)/clicks_info/<str:api_flags>

My local Django server host as of writing this is 127.0.0.1:8000/ therefore I will be using this in the URLS below, for ease of demonstration.

API flags:

**1:
date_from
date_to**

The date_to and date_from flags are by default inclusive. If a date_to is set to 2017-06-01, for instance, then dates before and including the first of June will be shown.

Example: date_from=2017-05-20&date_to=2017-06-20 <- will show tables with dates from 2017-05-20 until 2017-06-20, including.

**2:
columns**

The columns flag specifies which columns to include.
If a column name is not included in columns, but is requested elsewhere - it will be included in columns automatically.

Example: columns=country,channel,os,impressions <- will show the country, channel, os and impressions columns of the table.

**3:
group**

The group flag specifies which columns to group by.
Grouping groups together the tables which share the same values in the grouping columns. It does not sum or add any of the values to show a summary, due to potential loss of information from other columns which cannot be summated (such as country, channel, date, etc).

Multiple columns specified in group will group together tables which share the same values under all of those multiple columns.

Example: group=os,country <- will group tables which have the same os and country, as well as display the os and country columns if those aren't already specified in columns.

**4:
sorted**

The sorted flag specifies which column to sort by, and in what order (ascending or descending).
Columns containing string values (country, channel, os, etc) are sorted alphabetically.
Columns containing numerical values (impressions, date, installs, etc) are sorted numerically.

Example: sorted=date,descending <- will sort the tables by date, in descending order

**5:
cpi**

The cpi flag can be either true or false, and decides whether cpi is also calculated according to the formula: cpi = spend / installs
The cpi column is displayed in addition to all other requested columns if cpi is true.

Example: cpi=true <- will calculate cpi for each table and display it alongside the other columns

**6:
include_only**

The include_only flag is a special flag that allows to flexibly input any string or set of strings separated by comma, with the expectation that the output data will contain those strings.
For example: include_only=ios will ensure that the output will only show models which have "ios" in one of their fields.
Second example: include_only=ios,US will ensure that only models which have "US" and "ios" will be returned in the response.
It is case sensitive.
The user should be careful to make sure to include the column the expect to find the include_only string in, either in columns, group, or sorted.

Example: include_only=US,2017-06-01 <- will show only tables whose requested columns contain US and 2017-06-01

**Format:**
Each flag is separated by the symbol &.
The symbol = denotes the value of the flag.
Commas (,) represent multiples of values.

Example of a URL using the API:

127.0.0.1:8000/clicks_info/date_from=2017-05-20&date_to=2017-06-20&columns=date,country

The API parser is robust - the order of flags does not matter, and it can handle if a column is requested in group or in sorted, but not specified in columns, by assuming that columns grouped or sorted by are also expected to be seen.

When the request URL is simply 127.0.0.1:8000/clicks_info/, the returned tables will show up in their default form.
The default is: All dates, all columns, no grouping, no cpi, sorted by date in descending order.

### Specific use case urls:

**1. Show the number of impressions and clicks that occurred before the 1st of June 2017, broken down by channel and country, sorted by clicks in descending order.**

127.0.0.1:8000/clicks_info/date_to=2017-05-31&group=channel,country&sorted=clicks,descending&columns=impressions,clicks,channel,country

Or

127.0.0.1:8000/clicks_info/date_to=2017-05-31&group=channel,country&sorted=clicks,descending&columns=impressions

As the parser will auto complete clicks, channel, and country into the columns since they are requested elsewhere.


**2. Show the number of installs that occurred in May of 2017 on iOS, broken down by date, sorted by date in ascending order.**

127.0.0.1:8000/clicks_info/date_from=2017-05-01&date_to=2017-05-31&group=date,os&sorted=date,ascending&columns=os,installs,date&incude_only=ios


**3. Show revenue, earned on June 1, 2017 in US, broken down by operating system and sorted by revenue in descending order.**

127.0.0.1:8000/clicks_info/include_only=2017-06-01,US&group=os&sorted=revenue,descending&columns=revenue,date,os,country


**4. Show CPI and spend for Canada (CA) broken down by channel ordered by CPI in descending order.**

127.0.0.1:8000/clicks_info/include_only=CA&group=channel&cpi=true&sorted=cpi,descending&columns=country

Note that cpi and channel are not included in columns, because the columns returned will always correspond to columns requested in group and sorted, and if cpi is true, cpi will also be an included column.
However the url:

127.0.0.1:8000/clicks_info/include_only=CA&group=channel&cpi=true&sorted=cpi,descending&columns=country,cpi,channel

Is also perfectly valid and will return the same results.


*The API endpoint was tested and confirmed working both in browser and in postman.*

## The Database

The database in question is a small sample of a database of clicks and impressions, with the columns:
date, channel, country, os, impressions, clicks, installs, spend, revenue.

The database resides in the database folder, under the name clicksinfo_db.sqlite3. It is also stored as the original CSV in the same folder.
When loaded, it is loaded from the sqlite3 db file, so the CSV file can be disregarded.
The database is already loaded. However, if you wish to re-load the database, you can do so by first flushing it:

**Flushing the Database**
```
python manage.py flush
```
And type yes when prompted.
After it is flushed, you can load the database.

**Loading the Database**
```
python manage.py shell

from handler.load_db import LoadDB

import_log = LoadDB('database/clicksinfo_db.sqlite3').load_db()
```
Where import_log contains all row numbers and their import status.
During the import each row will also give real-time feedback to it's import status.

# Further details:
The superuser is: admin
Password is: admin

This repo was made in response to a task by Adjust.

It is worth noting that this is a task I have learned to execute over the span of two days, as I had not done this or anything like this before, and hope that this speaks to my fast learning and dedication.
