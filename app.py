from flask import Flask, render_template, send_file, make_response
import duckdb
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO

app = Flask(__name__)
conn = duckdb.connect('weather.duckdb', read_only=True)

# Utility: render matplotlib figure to PNG
def render_png(fig):
    output = BytesIO()
    fig.savefig(output, format='png', bbox_inches='tight')
    plt.close(fig)
    output.seek(0)
    return send_file(output, mimetype='image/png')

@app.route("/")
def index():
    routes = [
        ("temperature-trend", "Avg Temperature by Year"),
        ("visibility-trend", "Avg Visibility by Year"),
        ("dew-point-analysis", "Avg Dew Point by Year"),
        ("daily-avg-temp", "Daily Avg Temperature"),
        ("min-max-temp", "Daily Min & Max Temp"),
        ("temp-vs-visibility", "Temp vs Visibility"),
        ("outlier-temp", "Temperature Outliers"),
        ("missing-data", "Missing Data"),
        ("data-summary", "Data Summary")
    ]
    return render_template("index.html", routes=routes)

@app.route("/temperature-trend")
def temperature_trend():
    df = conn.execute("""
        SELECT STRFTIME('%Y', CAST(DATE AS TIMESTAMP)) AS year,
               AVG(TEMP_C) AS avg_temp
        FROM potsdam_weather_final
        WHERE TEMP_C IS NOT NULL AND TEMP_C < 999
        GROUP BY year ORDER BY year
    """).fetchdf()
    fig, ax = plt.subplots()
    sns.lineplot(data=df, x='year', y='avg_temp', marker='o', ax=ax)
    ax.set_title("Avg Temperature by Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Temperature (°C)")
    return render_png(fig)


@app.route("/visibility-trend")
def visibility_trend():
    df = conn.execute("""
        SELECT STRFTIME('%Y', CAST(DATE AS TIMESTAMP)) AS year,
               AVG(VIS_M) AS avg_vis
        FROM potsdam_weather_final
        WHERE VIS_M IS NOT NULL AND VIS_M < 999999
        GROUP BY year ORDER BY year
    """).fetchdf()
    fig, ax = plt.subplots()
    sns.lineplot(data=df, x='year', y='avg_vis', marker='o', ax=ax)
    ax.set_title("Avg Visibility by Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Visibility (m)")
    return render_png(fig)


@app.route("/dew-point-analysis")
def dew_point_analysis():
    df = conn.execute("""
        SELECT STRFTIME('%Y', CAST(DATE AS TIMESTAMP)) AS year,
               AVG(DEW_C) AS avg_dew
        FROM potsdam_weather_final
        WHERE DEW_C IS NOT NULL AND DEW_C < 999
        GROUP BY year ORDER BY year
    """).fetchdf()
    fig, ax = plt.subplots()
    sns.lineplot(data=df, x='year', y='avg_dew', marker='o', ax=ax)
    ax.set_title("Avg Dew Point by Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Dew Point (°C)")
    return render_png(fig)


@app.route("/daily-avg-temp")
def daily_avg_temp():
    df = conn.execute("""
        SELECT DATE_TRUNC('day', CAST(DATE AS TIMESTAMP)) AS day, AVG(TEMP_C) AS avg_temp
        FROM potsdam_weather_final
        WHERE TEMP_C IS NOT NULL
        GROUP BY day ORDER BY day
    """).fetchdf()
    df['day'] = pd.to_datetime(df['day'])
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(data=df, x='day', y='avg_temp', ax=ax)
    ax.set_title("Daily Avg Temperature")
    ax.set_xlabel("Date")
    ax.set_ylabel("Temperature (°C)")
    return render_png(fig)

@app.route("/min-max-temp")
def min_max_temp():
    df = conn.execute("""
        SELECT DATE_TRUNC('day', CAST(DATE AS TIMESTAMP)) AS day,
               MIN(TEMP_C) AS min_temp, MAX(TEMP_C) AS max_temp
        FROM potsdam_weather_final
        WHERE TEMP_C IS NOT NULL
        GROUP BY day ORDER BY day
    """).fetchdf()
    df['day'] = pd.to_datetime(df['day'])
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(x='day', y='min_temp', data=df, label='Min Temp', ax=ax)
    sns.lineplot(x='day', y='max_temp', data=df, label='Max Temp', ax=ax)
    ax.set_title("Min & Max Temperature by Day")
    ax.set_xlabel("Date")
    ax.set_ylabel("Temperature (°C)")
    return render_png(fig)

@app.route("/temp-vs-visibility")
def temp_vs_visibility():
    df = conn.execute("""
        SELECT TEMP_C, VIS_M
        FROM potsdam_weather_final
        WHERE TEMP_C IS NOT NULL AND TEMP_C < 999
          AND VIS_M IS NOT NULL AND VIS_M < 999999
    """).fetchdf()
    fig, ax = plt.subplots()
    sns.scatterplot(x='TEMP_C', y='VIS_M', data=df, ax=ax)
    ax.set_title("Temperature vs Visibility")
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Visibility (m)")
    return render_png(fig)

@app.route("/outlier-temp")
def outlier_temp():
    df = conn.execute("SELECT TEMP_C FROM potsdam_weather_final WHERE TEMP_C IS NOT NULL AND TEMP_C < 999").fetchdf()
    fig, ax = plt.subplots()
    sns.boxplot(y='TEMP_C', data=df, ax=ax)
    ax.set_title("Temperature Outliers")
    ax.set_ylabel("Temperature (°C)")
    return render_png(fig)

@app.route("/missing-data")
def missing_data():
    df = conn.execute("SELECT * FROM potsdam_weather_final").fetchdf()
    fig, ax = plt.subplots()
    missing = df.isna().sum()
    sns.barplot(x=missing.index, y=missing.values, ax=ax)
    ax.set_title("Missing Data by Column")
    ax.set_ylabel("Count of Missing Values")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    return render_png(fig)

@app.route("/data-summary")
def data_summary():
    df = conn.execute("SELECT * FROM potsdam_weather_final").fetchdf()
    head_html = df.head(20).to_html(classes='table table-striped', index=False)
    stats_html = df.describe().to_html(classes='table table-bordered')
    return render_template("summary.html", head=head_html, stats=stats_html, title="Data Summary")

if __name__ == "__main__":
    app.run(debug=True)
