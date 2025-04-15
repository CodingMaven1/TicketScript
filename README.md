# RCB Ticket Monitor

This script monitors the RCB ticket website for specific dates and notifies you when tickets become available.

## Prerequisites

1. Python 3.7 or higher
2. Chrome browser installed
3. Twilio account (for SMS and call notifications)

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a Twilio account and get your credentials:
   - Sign up at https://www.twilio.com/
   - Get your Account SID and Auth Token
   - Get a Twilio phone number

3. Create a `.env` file:
   - Copy `.env.example` to `.env`
   - Fill in your Twilio credentials and phone numbers

## Usage

Run the script:
```bash
python ticket_monitor.py
```

The script will:
- Check the RCB ticket website every minute
- Monitor for tickets on May 3rd and May 13th
- Send an SMS and make a call when tickets become available

## Features

- Headless browser operation
- SMS and voice call notifications
- Continuous monitoring
- Error handling and logging 