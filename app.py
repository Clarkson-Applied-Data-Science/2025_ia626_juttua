from flask import Flask, render_template_string, request, jsonify
import duckdb

app = Flask(__name__)

# Connect to DuckDB in read-only mode
db_path = 'weather.duckdb'
con = duckdb.connect(database=db_path, read_only=True)

# Pre-fetch dropdown values
data_info = con.execute("SELECT MIN(DATE) as min_date, MAX(DATE) as max_date FROM combined_cleaned").fetchall()
locations = [r[0] for r in con.execute("SELECT DISTINCT NAME FROM combined_cleaned ORDER BY NAME").fetchall()]
min_date = data_info[0][0][:10]
max_date = data_info[0][1][:10]

# HTML Template
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>New York North Country Weather Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <h1>New York North Country Weather Dashboard</h1>

    <form id="controls">
        <label for="location">Select Location:</label>
        <select id="location" name="location">
            {% for loc in locations %}
            <option value="{{ loc }}">{{ loc }}</option>
            {% endfor %}
        </select>

        <label for="start_date">Start Date:</label>
        <input type="date" id="start_date" name="start_date" min="{{ min_date }}" max="{{ max_date }}" value="{{ min_date }}">

        <label for="end_date">End Date:</label>
        <input type="date" id="end_date" name="end_date" min="{{ min_date }}" max="{{ max_date }}" value="{{ max_date }}">

        <button type="button" onclick="updateGraph()">Update</button>
        <button type="button" onclick="updateGraph('temp')">Temperature</button>
        <button type="button" onclick="updateGraph('vis')">Visibility</button>
        <button type="button" onclick="updateGraph('wind')">Wind Speed</button>
        <button type="button" onclick="updateGraph('hot')">Top 5 Hottest</button>
        <button type="button" onclick="updateGraph('cold')">Top 5 Coldest</button>
    </form>

    <div id="chart-container">
        <div id="graph"></div>
        <div id="no-data-message" style="display: none; text-align: center; padding: 40px; font-size: 18px; font-weight: bold; color: red;">
            🚫 No Data Available for selected filters
        </div>
    </div>

    <script>
    var currentChartType = 'temp';

    function updateGraph(type) {
        if (type) {
            currentChartType = type;
        }

        var location = document.getElementById('location').value;
        var start_date = document.getElementById('start_date').value;
        var end_date = document.getElementById('end_date').value;

        let url = '';
        if (currentChartType === 'temp') {
            url = `/data?location=${location}&start_date=${start_date}&end_date=${end_date}`;
        } else if (currentChartType === 'vis') {
            url = `/data_visibility?location=${location}&start_date=${start_date}&end_date=${end_date}`;
        } else if (currentChartType === 'wind') {
            url = `/data_wind?location=${location}&start_date=${start_date}&end_date=${end_date}`;
        } else if (currentChartType === 'hot') {
            url = `/data_top5_hot?location=${location}`;
        } else if (currentChartType === 'cold') {
            url = `/data_top5_cold?location=${location}`;
        }

        fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.dates.length === 0 || data.values.length === 0) {
                document.getElementById('graph').style.display = 'none';
                document.getElementById('no-data-message').style.display = 'block';
                return;
            } else {
                document.getElementById('no-data-message').style.display = 'none';
                document.getElementById('graph').style.display = 'block';
            }

            var trace = {
                x: data.dates,
                y: data.values,
                type: (currentChartType === 'hot' || currentChartType === 'cold') ? 'bar' : 'scatter',
                mode: (currentChartType === 'hot' || currentChartType === 'cold') ? undefined : 'lines+markers',
                name: location
            };

            var layout = {
                title: data.title,
                xaxis: { title: data.xaxis },
                yaxis: { title: data.yaxis, rangemode: 'tozero' },
                margin: { t: 50, l: 50, r: 50, b: 50 }
            };

            Plotly.react('graph', [trace], layout);
        })
        .catch(error => {
            alert('Error loading data: ' + error);
            console.error('Fetch error:', error);
        });
    }

    window.onload = function() {
        var today = new Date();
        var lastYear = new Date();
        lastYear.setFullYear(today.getFullYear() - 1);
        document.getElementById('start_date').value = lastYear.toISOString().split('T')[0];
        document.getElementById('end_date').value = today.toISOString().split('T')[0];
        updateGraph('temp');
    };
    </script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE, locations=locations, min_date=min_date, max_date=max_date)

@app.route('/data')
def temp_data():
    location = request.args.get('location')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = """
        SELECT DATE, TEMP_C
        FROM combined_cleaned
        WHERE NAME = ?
          AND DATE BETWEEN ? AND ?
          AND TEMP_C <> 999.9
        ORDER BY DATE ASC
    """
    rows = con.execute(query, [location, start_date, end_date]).fetchall()

    dates = [r[0][:10] for r in rows]  # Slice first 10 characters (YYYY-MM-DD)
    temps = [r[1] for r in rows]

    return jsonify({
        'dates': dates,
        'values': temps,
        'title': f'Temperature Trend - {location}',
        'xaxis': 'Date',
        'yaxis': 'Temperature (Celsius)'
    })

@app.route('/data_visibility')
def vis_data():
    location = request.args.get('location')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = """
        SELECT DATE, VIS_M
        FROM combined_cleaned
        WHERE NAME = ?
          AND DATE BETWEEN ? AND ?
          AND VIS_M < 900000
        ORDER BY DATE ASC
    """
    rows = con.execute(query, [location, start_date, end_date]).fetchall()

    dates = [r[0][:10] for r in rows]  # Slice first 10 characters (YYYY-MM-DD)
    vis = [r[1] for r in rows]

    return jsonify({
        'dates': dates,
        'values': vis,
        'title': f'Visibility Trend - {location}',
        'xaxis': 'Date',
        'yaxis': 'Visibility (meters)'
    })

@app.route('/data_wind')
def wind_data():
    location = request.args.get('location')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = """
        SELECT DATE, TRY_CAST(SPLIT_PART(WND, ',', 4) AS DOUBLE) / 10.0 AS wind_speed
        FROM combined_cleaned
        WHERE NAME = ?
          AND DATE BETWEEN ? AND ?
          AND WND IS NOT NULL
          AND SPLIT_PART(WND, ',', 4) NOT IN ('9999', '999')
        ORDER BY DATE ASC
    """
    rows = con.execute(query, [location, start_date, end_date]).fetchall()

    dates = [r[0][:10] for r in rows]  # Slice first 10 characters (YYYY-MM-DD)
    wind = [r[1] for r in rows]

    return jsonify({
        'dates': dates,
        'values': wind,
        'title': f'Wind Speed Trend - {location}',
        'xaxis': 'Date',
        'yaxis': 'Wind Speed (m/s)'
    })

@app.route('/data_top5_hot')
def top5_hot():
    location = request.args.get('location')

    query = """
        SELECT DATE, TEMP_C
        FROM combined_cleaned
        WHERE NAME = ?
          AND TEMP_C <> 999.9
        ORDER BY TEMP_C DESC
        LIMIT 5
    """
    rows = con.execute(query, [location]).fetchall()

    dates = [r[0][:10] for r in rows]  # Slice first 10 characters (YYYY-MM-DD)
    temps = [r[1] for r in rows]

    return jsonify({
        'dates': dates,
        'values': temps,
        'title': f'Top 5 Hottest Days - {location}',
        'xaxis': 'Date',
        'yaxis': 'Temperature (Celsius)'
    })

@app.route('/data_top5_cold')
def top5_cold():
    location = request.args.get('location')

    query = """
        SELECT DATE, TEMP_C
        FROM combined_cleaned
        WHERE NAME = ?
          AND TEMP_C <> 999.9
        ORDER BY TEMP_C ASC
        LIMIT 5
    """
    rows = con.execute(query, [location]).fetchall()

    dates = [r[0][:10] for r in rows]  # Slice first 10 characters (YYYY-MM-DD)
    temps = [r[1] for r in rows]

    return jsonify({
        'dates': dates,
        'values': temps,
        'title': f'Top 5 Coldest Days - {location}',
        'xaxis': 'Date',
        'yaxis': 'Temperature (Celsius)'
    })

if __name__ == '__main__':
    app.run(debug=True)