# OJ-Challenge
OddsJam Data Ingestion Challenge

## Instructions
Note: This was tested on a windows machine using a venv, the program only requires two basic packages to install (Pandas and requests) so a venv may be unnecessary.

Create venv Windows:
```
py -m venv .venv
```
 or Mac/Linux:
```
python3 -m venv .venv
```
Activate venv Windows:
```
.venv\Scripts\activate
```
or Mac/Linux:
```
source .venv/bin/activate
```
Install Pandas and requests
```
pip install pandas requests
```

Run Program Windows
```
py oj_dk_challenge.py
```
or Mac/Linux
```
python3 oj_dk_challenge.py
```

## Write-Up
This program completes the challenge of pulling DraftKings sportsbook data for one market (MLB), collecting the moneyline, total, and spread (run line in this case) for each game. Each of the pieces of information requested in the challenge are included in the final CSV. I chose to include as much information as possible including unnecessary information like primary keys from the DraftKings API used to merge the data together to demonstrate the transforms performed. Certain columns that might need an explanation are:

`betName`: which is a human readable complete name of the bet

`isSuspended`: represents if a bet is locked or not, meaning its formation still shows on the front-end but bets cannot be placed.

`isOpen`: represents if a bet is even on the front-end or not (this should always be True as closed bets do not return any information).

I chose to use the public API that I found after scraping DK's webpage. I found it to be extremely consistent, only trouble was just joining the different nested groups of data within each other. If I had more time I would work on making the program repeatable and appending the CSV instead of just replacing it entirely. Another step would be to include a more complete row for Closed bets based on the previous data, instead of just removing them entirely. Overall I found this challenge very fun, I really enjoyed pulling data directly from a sportsbook instead of the aggregators I've used previously. With the API being fairly straightforward, the only challenge was the transforms which Pandas handled great. i included a result CSV aswell.