# Reddit to Social Media Automation

## Overview

This project automates posting content from Reddit to Instagram, Facebook, and X (Twitter). It periodically checks a list of configured subreddits, selects the highest-ranked post that hasn't been shared before, downloads the associated media, and publishes it to each configured social media account.

The automation keeps track of previously posted Reddit submissions to prevent duplicate posts and supports multiple Instagram accounts, Facebook pages, and X accounts through configuration files.

## Features

* Monitors multiple subreddits on a schedule
* Selects the highest-ranked unposted submission
* Prevents duplicate posts by maintaining a post history
* Supports images and videos
* Posts to:

  * Instagram
  * Facebook
  * X (Twitter)
* Supports multiple accounts/pages per platform
* Configurable posting schedule
* Simple text-based configuration for accounts and subreddits

## Requirements

* Python 3.7+
* FFmpeg
* Python packages listed in `requirements.txt`

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

FFmpeg is required for media processing. Install it and make sure it is available in your system's PATH.

## Configuration

Most settings are stored in `settings.ini`, including:

* Reddit API credentials
* Instagram Graph API credentials
* Facebook Graph API credentials
* Posting schedule
* Other application settings

### X (Twitter)

X credentials are stored separately in `x_creds.json`.

Each account should have its own set of API credentials.

### Instagram Accounts

Add Instagram User IDs to:

```
instagram_user_ids.txt
```

One ID per line.

### Facebook Pages

Add Facebook Page IDs to:

```
facebook_pages.txt
```

One ID per line.

### Subreddits

The monitored subreddits are listed in:

```
subreddits.txt
```

Add or remove subreddits by editing this file. Use one subreddit per line.

## Running the Project

From the project directory, start the scheduler with:

```bash
python scheduler.py
```

The scheduler handles running the automation according to the configured posting times.

## Project Workflow

1. Read the configured list of subreddits.
2. Fetch the highest-ranked Reddit submission that has not been posted before.
3. Download the image or video.
4. Publish the content to the configured Instagram, Facebook, and X accounts.
5. Record the Reddit post ID to prevent future duplicates.
6. Wait until the next scheduled run.

## Notes

* The script is designed so that most changes can be made without modifying the source code.
* New subreddits can be added by editing `subreddits.txt`.
* Additional Facebook pages and Instagram accounts can be added by updating their respective text files.
* X accounts can be added by including another set of credentials in `x_creds.json`.
* Posting times can be adjusted through `settings.ini`.
