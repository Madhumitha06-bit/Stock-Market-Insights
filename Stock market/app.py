from flask import Flask, render_template, request
import yfinance as yf
import plotly.graph_objs as go
import plotly
import json

app = Flask(__name__)

# Predefined stocks with custom date ranges, moving averages, and graph styles
stocks = {
    "TCS": {"ticker": "TCS.NS", "start_date": "2022-01-01", "end_date": "2023-01-01", "ma_period": 20, "line_color": 'blue', "line_style": 'solid', "is_candlestick": False},
    "Infosys": {"ticker": "INFY.NS", "start_date": "2021-01-01", "end_date": "2024-01-01", "ma_period": 50, "line_color": 'green', "line_style": 'dash', "is_candlestick": False},
    "Reliance": {"ticker": "RELIANCE.NS", "start_date": "2020-06-01", "end_date": "2025-01-01", "ma_period": 100, "line_color": 'red', "line_style": 'dot', "is_candlestick": True},  # Reliance is Candlestick
    "HDFC Bank": {"ticker": "HDFCBANK.NS", "start_date": "2019-01-01", "end_date": "2025-01-01", "ma_period": 200, "line_color": 'purple', "line_style": 'dashdot', "is_candlestick": False},
    "Wipro": {"ticker": "WIPRO.NS", "start_date": "2023-01-01", "end_date": "2024-01-01", "ma_period": 7, "line_color": 'orange', "line_style": 'solid', "is_candlestick": False}
}

@app.route("/", methods=["GET", "POST"])
def index():
    charts = []
    selected_stocks = []
    message = ""

    if request.method == "POST":
        selected_stocks = request.form.getlist("stocks")

        if not selected_stocks:
            message = "Please select at least one stock."
        else:
            for stock_name in selected_stocks:
                stock_info = stocks.get(stock_name)
                ticker = stock_info["ticker"]
                start_date = stock_info["start_date"]
                end_date = stock_info["end_date"]
                ma_period = stock_info["ma_period"]
                line_color = stock_info["line_color"]
                line_style = stock_info["line_style"]
                is_candlestick = stock_info["is_candlestick"]

                print(f"\n📥 Downloading: {stock_name} - {ticker} (Date range: {start_date} to {end_date})")

                try:
                    data = yf.download(ticker, start=start_date, end=end_date)
                    print(data.tail(3))  # Print last 3 rows of each stock

                    if data.empty:
                        message += f"No data for {stock_name}. "
                        continue

                    # Create a Plotly chart for each stock with unique styling
                    fig = go.Figure()

                    # If it's a candlestick chart (for Reliance)
                    if is_candlestick:
                        fig.add_trace(go.Candlestick(x=data.index,
                                                     open=data["Open"],
                                                     high=data["High"],
                                                     low=data["Low"],
                                                     close=data["Close"],
                                                     name=f"{stock_name} Candlestick"))

                    # For other stocks, use line charts with moving averages
                    else:
                        fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Close Price",
                                                 line=dict(color=line_color, dash=line_style)))
                        fig.add_trace(go.Scatter(x=data.index, y=data["Close"].rolling(ma_period).mean(),
                                                 mode="lines", name=f"{ma_period}-Day MA",
                                                 line=dict(color=line_color, dash=line_style)))

                    fig.update_layout(
                        title=f"{stock_name} Stock Trend",
                        xaxis_title="Date",
                        yaxis_title="Price (INR)",
                        template="plotly_dark",
                        height=500
                    )

                    chartJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                    charts.append((chartJSON, stock_name))  # Append tuple of (chart data, stock name)

                except Exception as e:
                    message += f"Error loading {stock_name}: {str(e)} "

    return render_template("index.html", charts=charts, stocks=stocks, selected=selected_stocks, message=message)

if __name__ == "__main__":
    app.run(debug=True)
