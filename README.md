![PortSwigger Progress](https://i.imgur.com/kdZjayp.jpeg)

# PortSwigger Academy Tracker

## Table of Contents
- [PortSwigger Academy Tracker](#portswigger-academy-tracker)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
    - [Cookie Management](#cookie-management)
  - [Usage](#usage)
    - [Command-Line Arguments](#command-line-arguments)
    - [Update Progress Table](#update-progress-table)
    - [Schedule Automated Updates](#schedule-automated-updates)
  - [Progress Tracking](#progress-tracking)
    - [Progress File](#progress-file)
    - [Generated README](#generated-readme)
      - [PortSwigger Academy Progress](#portswigger-academy-progress)
        - [Overall Progress](#overall-progress)
        - [Topic Progress](#topic-progress)
  - [Project Structure](#project-structure)
  - [Contributing](#contributing)
  - [License](#license)
  - [Contact](#contact)

## Overview

The PortSwigger Academy Tracker is a Python script designed to monitor and track your progress on the PortSwigger Academy platform. It automatically fetches your progress across various web security topics and updates a comprehensive README.md file, providing a clear overview of your achievements and remaining challenges. Additionally, it supports automated weekly updates to ensure your progress is always up-to-date.

## Features

* Automatic Progress Tracking: Fetches and parses your progress across multiple web security topics
* Level Progress Monitoring: Tracks your advancement through different proficiency levels (Apprentice, Practitioner, Expert)
* Scheduled Updates: Automatically updates your progress table on a weekly basis
* Customizable Output: Generates a well-formatted README.md showcasing your progress
* Cookie Management: Securely handles authentication cookies to maintain session integrity

## Prerequisites

Before you begin, ensure you have met the following requirements:

* Python 3.7 or higher installed on your system. You can download Python from [here](https://www.python.org/downloads/)
* A PortSwigger Academy account with active progress
* Basic knowledge of using the command line

## Installation

1. Clone the Repository
   ```bash
   git clone https://github.com/L0WK3Y-IAAN/portswigger-academy-tracker.git
   cd portswigger-academy-tracker
   ```

2. Create a Virtual Environment (Optional but Recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Required Dependencies
   ```bash
   pip install -r requirements.txt
   ```

   If a requirements.txt file is not provided, you can install the necessary packages manually:
   ```bash
   pip install argparse requests beautifulsoup4 schedule
   ```

## Configuration

### Cookie Management

To authenticate your session with PortSwigger Academy, the tracker requires valid cookies. Follow these steps to manage your cookies:

1. Navigate to the cookie_manager.py Script
   * Ensure you have the cookie_manager.py script in the project directory
   * This script handles storing and validating your cookies

2. Store Your Cookies
   ```bash
   python cookie_manager.py store
   ```
   * You will be prompted to enter your cookies manually
   * Ensure you provide accurate cookie data to avoid authentication issues

3. Validate Stored Cookies
   * The tracker automatically validates stored cookies before fetching progress
   * If cookies are invalid or expired, you will be prompted to update them

## Usage

The PortSwigger Academy Tracker can be operated via the command line with various options.

### Command-Line Arguments
* `--update`: Fetches the latest progress and updates the README.md
* `--schedule`: Initiates scheduled weekly updates

### Update Progress Table

To manually update your progress table, use the --update flag:

```bash
python tracker.py --update
```

What Happens:
* Initializes the session using stored cookies
* Fetches the latest progress data from PortSwigger Academy
* Parses and updates the README.md with current progress

### Schedule Automated Updates

To enable automated weekly updates, use the --schedule flag:

```bash
python tracker.py --schedule
```

What Happens:
* Initializes the session using stored cookies
* Schedules the update_progress_table job to run every Monday at 09:00 AM
* Continuously runs in the background, checking for scheduled tasks hourly

**Note:** Ensure that the script remains running for scheduled updates to function. You might consider using a process manager like nohup, screen, or tmux to keep the script active.

## Progress Tracking

### Progress File
* Filename: `progress.json`
* Purpose: Stores detailed progress data, including topics, completed labs, levels, and last updated timestamps
* Structure:

```json
{
  "topics": {
    "SQL injection": {
      "total_labs": 10,
      "completed": 7,
      "last_updated": "2025-01-02T14:30:00"
    }
  },
  "level_progress": {
    "apprentice": {"completed": 5, "total": 10},
    "practitioner": {"completed": 3, "total": 5},
    "expert": {"completed": 0, "total": 0}
  },
  "last_updated": "01/02/2025"
}
```

### Generated README
* Filename: `README.md`
* Purpose: Presents a well-formatted overview of your PortSwigger Academy progress
* Features:
  * Displays overall level progress with completion percentages
  * Lists individual topics with the number of completed labs, total labs, progress status, and the date of the last update
  * Uses emojis to visually represent progress status

Sample Output:

![PortSwigger Progress](https://i.imgur.com/kdZjayp.jpeg)

#### PortSwigger Academy Progress

##### Overall Progress
- **Apprentice**: 5/10 (50.0%)
- **Practitioner**: 3/5 (60.0%)
- **Expert**: 0/0 (0.0%)

##### Topic Progress
| Topic 📖 | Labs 🔬 | Progress ✅ | Status ⭕️ | Last Updated 🗓️ |
|----------|---------|------------|:---------:|----------------|
| **Server-side topics 🟧** | | | | |
| SQL injection | 10 | 7/10 | 🔵 | 01/02/2025 |
| Authentication | 8 | 8/8 | 🟢 | 01/02/2025 |

## Project Structure

```
portswigger-academy-tracker/
├── cookie_manager.py
├── tracker.py
├── progress.json
├── README.md
├── requirements.txt
└── README.md  # Generated by the tracker
```

* `cookie_manager.py`: Handles storing and validating authentication cookies
* `tracker.py`: Main script for tracking progress and updating the README
* `progress.json`: Stores the latest progress data
* `README.md`: Generated markdown file showcasing your progress
* `requirements.txt`: Lists all Python dependencies

## Contributing

Contributions are welcome! If you have suggestions, bug fixes, or improvements, please follow these steps:

1. Fork the Repository
2. Create a New Branch
   ```bash
   git checkout -b feature/YourFeatureName
   ```
3. Commit Your Changes
   ```bash
   git commit -m "Add your message here"
   ```
4. Push to the Branch
   ```bash
   git push origin feature/YourFeatureName
   ```
5. Open a Pull Request

Please ensure your code adheres to the project's coding standards and includes relevant documentation.

## License

This project is licensed under the MIT License.

## Contact

For any questions or feedback, please reach out to jonny@iaansec.com.

Happy Tracking!
