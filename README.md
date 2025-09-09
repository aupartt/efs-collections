# Collectes EFS

A comprehensive data collection and analysis system for the French Blood Service (EFS) API. This project retrieves, processes, and stores EFS collection data to provide insights into mobile blood donation schedules and locations across Brittany.

## 🤔 What This Project Does

The system automatically:
- 🗺️ **Discovers** blood donation locations across Brittany
- 📅 **Retrieves** collection schedules and availability
- 🕷️ **Crawls** detailed appointment data from EFS websites  
- 💾 **Stores** everything in SQL database
- ⏰ **Schedules** regular updates

So we can:
- 📊 **Analyze** the data using Grafana and Streamlit
- 🚨 **Create alerts** for poorly filled collections
- 👀 **Improve** the visibility of these collections

## 📃 Docs
- [EFS's API details](./docs/efs_api_info.md)
- [Manage Grafana Dashboards](./docs/grafana-dashboards-provisioning.md)

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

### Installation & Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd collectes-efs
   ```

2. **Setup `.env`**
   
   ```bash
   cp .env.example .env

   # ... change variables
   ```

3. **Build all services**

   ```bash
   docker compose build
   ```

4. **Start the infrastructure**

   ```bash
   docker compose up -d
   ```

5. **Init database**

   This service should have started with the previous step
   ```bash
   docker compose run --rm alembic
   ```
   
6. **First run**

   Don't forget to make a first run to initialize **groups** and **locations**
   ```bash
   docker compose run --rm cli --groups --locations
   ```

## 📋 CLI Usage
### Parameters
| Long              | Short  | Type            | Default | Description                               |
| ----------------- | ------ | --------------- | ------- | ----------------------------------------- |
| --ping            | -p     | bool            | False   | Test if the CLI is working                |
| **--file**        | **-f** | str             | `None`  | Path to the data file                     |
| **--format**      | **-F** | `JSON`, `JSONL` | `JSONL` | Format of the data                        |
| **--groups**      | **-g** | bool            | `False` | Update groups database                    |
| **--locations**   | **-l** | bool            | `False` | Update location database                  |
| **--collections** | **-c** | bool            | `False` | Update collection and get events snapshot |
| **--schedules**   | **-s** | bool            | `False` | Get schedules snapshot                    |
| **--crawl**       | **-s** | bool            | `False` | Start the crawler with nargs* urls        |

### Start collecte

```bash
# Start a single collect
docker compose run --rm cli --groups

# Start multiple collecte
docker compose run --rm cli --collections --schedules
```

### Insert data from file
Make sure to put you file into the `./data/` folder

```bash
# The ./data folder of this project is mounted at ../data/ 
docker compose run --rm cli --collections --file ../data/collections.json
```

### Test crawl
You can also test the crawler
```bash
# Test the crawler with some urls - The results will be printed
docker compose run --rm cli --crawl http://foo.bar http://foo.baz

# You can combine the crawl with schedules (usefull if you think there is a problem with a specific collection)
docker compose run --rm cli --crawl --schedules http://url-to.test
```

## ⏰ Automated Scheduling (optional)

You can use `run-collectes.sh` and `crontab-collectes` to schedule automated data collection.

### Default scheduled Tasks
| Task | Frequency | Purpose |
|------|-----------|---------|
| `get-groups` | Weekly (Sun 2 AM) | Update groups database |
| `get-locations` | Weekly (Sun 2:30 AM) | Update location database |
| `get-collections` | Daily (3 AM) | Refresh collection events |
| `get-schedules` | Daily (3:30 AM) | Update appointment availability |

**Setup automated scheduling**
```bash
   # 1. Copy the script
   sudo cp ./conf/scheduling/run-collectes.sh /usr/local/bin/
   sudo chmod +x /usr/local/bin/run-collectes.sh

   # 2. Update the path in the script
   sudo nano /usr/local/bin/run-collectes.sh
   # Change PROJECT_DIR="/path/to/your/collectes-efs"

   # 3. Test the script
   /usr/local/bin/run-collectes.sh schedules

   # 4. Add to crontab
   crontab -e
   # Copy the lines from crontab-collectes file
```

## ⚒️ Development
This project uses uv workspace with a global pyproject.toml so you don't need to change directories to manage packages or run tests.

**Install all project and development dependencies for the entire monorepo.**

```bash
uv sync --dev
```

**Run all tests from the project root.**
```bash
uv run pytest
```

**Start streamlit dashboard**

⚠️ Streamlit dashboard need a .env in `./dashboard/.env` (to avoid conflict with the one at `root`)
```bash
streamlit run dashboard/main.py
```
