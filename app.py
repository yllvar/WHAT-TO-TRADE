from flask import Flask, render_template, request
import ccxt
import os
import finta
import pandas as pd

app = Flask(__name__)

class OHLCVAnalyzer:
    def __init__(self):
        self.exchange = ccxt.kucoinfutures({
            'apiKey': os.getenv('API_KEY'),
            'secret': os.getenv('SECRET_KEY'),
            'password': os.getenv('PASSPHRASE'),
            'enableRateLimit': True
        })

    def fetch_and_analyze_symbols(self, timeframe='15m'):
        results = []
        try:
            symbols = self.exchange.load_markets().keys()

            for symbol in symbols:
                ohlcv_data = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe)

                if ohlcv_data:
                    df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['rsi'] = finta.TA.RSI(df, period=14)
                    latest_rsi = df['rsi'].iloc[-1]

                    if latest_rsi > 70 or latest_rsi < 30:
                        results.append({'symbol': symbol, 'latest_rsi': latest_rsi})

        except Exception as e:
            print(f"Error fetching and analyzing symbols: {e}")

        return results

@app.route('/')
def index():
    timeframe = request.args.get('timeframe', '15m')
    analyzer = OHLCVAnalyzer()
    results = analyzer.fetch_and_analyze_symbols(timeframe=timeframe)
    return render_template('index.html', results=results, selected_timeframe=timeframe)

if __name__ == '__main__':
    app.run(debug=True)

