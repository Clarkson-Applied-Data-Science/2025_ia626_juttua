
# Potsdam Weather Dashboard

A web-based data analytics dashboard built using Flask and DuckDB to provide a visual and statistical analysis of historical weather data for Potsdam, NY. This project demonstrates an end-to-end ETL pipeline and data visualization interface optimized for over one million weather observations.

---

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Data Gathering](#data-gathering)  
3. [ETL Process](#etl-process)  
4. [Database Overview](#database-overview)  
5. [Dashboard Routes](#dashboard-routes)  
6. [How to Run](#how-to-run)  
7. [Technologies Used](#technologies-used)  
8. [License](#license)

---

## Project Overview

This application offers a suite of weather visualizations for Potsdam, NY. The dataset originates from official U.S. weather logs, transformed and stored in a local analytical DuckDB database. The web interface provides plots and summaries across temperature, dew point, visibility, and more.

---

## Data Gathering

- Raw CSV files were retrieved from SFTP endpoints and include hourly weather data for various years.
- Only files from stations in geographic proximity to Potsdam, NY were retained.
- Selected station IDs based on longitude/latitude matching:
  
| Station ID     | Latitude     | Longitude    |
|----------------|--------------|--------------|
| 72518699999    | 44.681854    | -75.465500   |
| 72622394725    | 44.933410    | -74.848360   |
| 72622894740    | 44.392790    | -74.202880   |
| 74370014715    | 44.050000    | -75.733330   |
| 99822399999    | 44.333333    | -75.933333   |
| 99843599999    | 44.703000    | -75.495000   |

---

## ETL Process

The `ETL.ipynb` and `Data.ipynb` notebooks handle extraction, transformation, and loading.

### Cleaning and Transformation Steps:

| Step                | Description |
|---------------------|-------------|
| **Null Handling**   | Removed or ignored rows where key columns were null or contained invalid thresholds (e.g., TEMP_C > 999). |
| **Outlier Removal** | Filtered erroneous visibility and temperature values. |
| **Date Parsing**    | Standardized dates to DuckDB TIMESTAMP for grouping. |
| **Schema Alignment**| Ensured uniform schema across all year-wise files. |
| **Format Conversion** | Converted cleaned CSVs into Parquet and imported them into DuckDB. |

---

## Database Overview

Final database: `weather.duckdb`  
Main table: `potsdam_weather_final`

### Table Schema

| Column Name    | Data Type     | Description                           |
|----------------|---------------|---------------------------------------|
| DATE           | TIMESTAMP     | Date and time of record               |
| TEMP_C         | DOUBLE        | Temperature in Celsius                |
| VIS_M          | DOUBLE        | Visibility in meters                  |
| DEW_C          | DOUBLE        | Dew point in Celsius                  |
| SLP_HPA        | DOUBLE        | Sea Level Pressure (hPa)              |
| WIND_MPS       | DOUBLE        | Wind speed in meters per second       |
| GUST_MPS       | DOUBLE        | Wind gusts in meters per second       |
| PRECIP_MM      | DOUBLE        | Precipitation in millimeters          |
| SNOW_MM        | DOUBLE        | Snow depth in millimeters             |
| RH_PERCENT     | DOUBLE        | Relative humidity (%)                 |
| QC_FLAGS       | VARCHAR       | Quality control flags                 |

- The table contains ~1 million rows after consolidation.
- All NULLs are accounted for and documented via `/missing-data` route.

---

## Dashboard Routes

The Flask app (`app.py`) defines multiple endpoints with live DuckDB queries and image-based plots.

| Route                   | Description                            |
|-------------------------|----------------------------------------|
| `/`                     | Homepage with route links              |
| `/temperature-trend`    | Avg temperature trend by year          |
| `/visibility-trend`     | Avg visibility trend by year           |
| `/dew-point-analysis`   | Avg dew point trend by year            |
| `/daily-avg-temp`       | Daily average temperature (timeline)   |
| `/min-max-temp`         | Daily min & max temperatures           |
| `/temp-vs-visibility`   | Scatter plot of temp vs visibility     |
| `/outlier-temp`         | Boxplot for temp outliers              |
| `/missing-data`         | Count of missing values by column      |
| `/data-summary`         | Head and `describe()` output of data   |

- Rendered with `matplotlib`, `seaborn`, and Jinja2 templates (`plot.html`, `summary.html`).
- Outputs are served as images or HTML-rendered tables (summary).

---

## How to Run

1. Clone the repository:
```bash
git clone https://github.com/your-username/potsdam-weather-dashboard.git
cd potsdam-weather-dashboard
```

2. Install dependencies:
```bash
pip install flask duckdb matplotlib seaborn pandas
```

3. Verify the `weather.duckdb` file exists. If not, run the Jupyter notebooks:
```bash
jupyter notebook ETL.ipynb
```

4. Start the Flask server:
```bash
python app.py
```

5. Open in browser:
```
http://127.0.0.1:5000/
```

---

## Technologies Used

- **Python 3.10+**
- **DuckDB** for high-speed SQL analytics
- **Flask** for interactive web dashboard
- **Matplotlib & Seaborn** for visualizations
- **HTML + Jinja2** templating engine
- **Parquet** for intermediate data storage

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
