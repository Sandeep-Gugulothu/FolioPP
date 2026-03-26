"""Technical Analyzer - Institutional Manual Quant Strategy Processor."""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import plotly.utils
from pykalman import KalmanFilter
from hurst import compute_Hc

class TechnicalAnalyzer:
    """Calculates manual 10+ professional indicators using the Indicators class logic."""

    class Indicators:
        """Calculates technical indicators manually on OHLCV data."""
        data = None  

        @classmethod
        def initialize(cls, data: pd.DataFrame):
            """Initialize with OHLCV data."""
            # Ensure columns are lowercase for our math
            data.columns = [str(c).lower() for c in data.columns]
            cls.data = data.copy()

        @classmethod
        def calculate_prev_ohlcv(cls):
            """Calculate previous OHLCV columns by shifting current values."""
            cls.data['prev_open'] = cls.data['open'].shift(1)
            cls.data['prev_high'] = cls.data['high'].shift(1)
            cls.data['prev_low'] = cls.data['low'].shift(1)
            cls.data['prev_close'] = cls.data['close'].shift(1)
            cls.data['prev_volume'] = cls.data['volume'].shift(1)
            cls.data.dropna(subset=['prev_open', 'prev_high', 'prev_low', 'prev_close', 'prev_volume'], inplace=True)

        @classmethod
        def apply_kalman_filter(cls, transition_covariance: float = 0.01):
            """Apply Kalman Filter to prev_close."""
            prices = cls.data['prev_close'].dropna().values.reshape(-1, 1)
            if len(prices) == 0: return
            kf = KalmanFilter(
                transition_matrices=[1],
                observation_matrices=[1],
                initial_state_mean=prices[0],
                initial_state_covariance=1,
                observation_covariance=0.1,
                transition_covariance=transition_covariance
            )
            state_means, _ = kf.filter(prices)
            cls.data['prev_filtered_close'] = pd.Series(state_means.flatten(), index=cls.data['prev_close'].dropna().index)

        @classmethod
        def rolling_hurst_exponent(cls, window: int = 100):
            """Calculate Hurst Exponent in a rolling window."""
            def hurst_exponent(ts):
                if len(ts) < 20 or np.any(np.isnan(ts)) or np.std(ts) == 0:
                    return np.nan
                try:
                    H, _, _ = compute_Hc(ts)
                    return H if 0 <= H <= 1 else np.nan
                except:
                    return np.nan
            cls.data['hurst'] = cls.data['prev_close'].rolling(window=window, min_periods=window).apply(hurst_exponent, raw=True)

        @classmethod
        def calculate_cusum(cls, window: int = 4, delta: float = 0.8):
            """Calculate CUSUM indicators."""
            rolling_sigma = cls.data['prev_close'].rolling(window=window).std()
            k = delta * rolling_sigma.fillna(0)
            price = cls.data['prev_close'].values
            mu = cls.data['prev_filtered_close'].values
            S_hi = np.zeros(len(cls.data))
            S_lo = np.zeros(len(cls.data))
            for i in range(1, len(cls.data)):
                S_hi[i] = max(0, S_hi[i-1] + (price[i] - mu[i] - k.iloc[i]))
                S_lo[i] = max(0, S_lo[i-1] + (-price[i] + mu[i] - k.iloc[i]))
            cls.data['cusum_hi'] = S_hi
            cls.data['cusum_lo'] = S_lo

        @classmethod
        def calculate_fdi(cls, window: int = 35):
            """Calculate Fractal Dimension Index."""
            def fractal_dimension(series):
                n = len(series)
                if n <= 1 or np.all(np.isnan(series)):
                    return np.nan
                L = np.sum(np.abs(np.diff(series)))
                d = np.max(np.abs(series - series[0]))
                return np.log(n) / (np.log(n) + np.log(d / L)) if L != 0 and d != 0 else np.nan
            cls.data['fdi'] = cls.data['prev_filtered_close'].rolling(window=window, min_periods=window).apply(fractal_dimension, raw=True)

        @classmethod
        def calculate_supertrend(cls, atr_length=14, factor=3.0):
            """Calculate Supertrend indicator."""
            cls.data['tr'] = np.maximum(
                cls.data['prev_high'] - cls.data['prev_low'],
                np.maximum(
                    abs(cls.data['prev_high'] - cls.data['prev_close'].shift(1)),
                    abs(cls.data['prev_low'] - cls.data['prev_close'].shift(1))
                )
            )
            cls.data['atr'] = cls.data['tr'].rolling(window=atr_length).mean()
            hl2 = (cls.data['prev_high'] + cls.data['prev_low']) / 2
            upper_band = hl2 + (factor * cls.data['atr'])
            lower_band = hl2 - (factor * cls.data['atr'])
            supertrend = [0] * len(cls.data)
            direction = [1] * len(cls.data)
            for i in range(1, len(cls.data)):
                if cls.data['prev_close'].iloc[i] > upper_band.iloc[i-1]:
                    supertrend[i] = lower_band.iloc[i]
                    direction[i] = -1
                elif cls.data['prev_close'].iloc[i] < lower_band.iloc[i-1]:
                    supertrend[i] = upper_band.iloc[i]
                    direction[i] = 1
                else:
                    supertrend[i] = supertrend[i-1]
                    direction[i] = direction[i-1]
            cls.data['supertrend'] = supertrend
            cls.data['supertrend_direction'] = direction

        @classmethod
        def calculate_rsi(cls, lengths=[14, 7]):
            """Calculate RSI for multiple lengths."""
            for length in lengths:
                delta = cls.data['prev_close'].diff()
                gain = np.where(delta > 0, delta, 0)
                loss = np.where(delta < 0, -delta, 0)
                avg_gain = pd.Series(gain, index=cls.data.index).rolling(window=length, min_periods=1).mean()
                avg_loss = pd.Series(loss, index=cls.data.index).rolling(window=length, min_periods=1).mean()
                rs = avg_gain / avg_loss
                cls.data[f'rsi_{length}'] = 100 - (100 / (1 + rs))

        @classmethod
        def calculate_macd(cls, fast_length=6, slow_length=12, signal_length=18):
            """Calculate MACD indicator."""
            fast_ema = cls.data['prev_close'].ewm(span=fast_length, adjust=False).mean()
            slow_ema = cls.data['prev_close'].ewm(span=slow_length, adjust=False).mean()
            cls.data['macd'] = fast_ema - slow_ema
            cls.data['macd_signal'] = cls.data['macd'].ewm(span=signal_length, adjust=False).mean()
            cls.data['macd_histogram'] = cls.data['macd'] - cls.data['macd_signal']

        @classmethod
        def calculate_moving_averages(cls, windows=[20, 50, 100, 200]):
            """Calculate institutional SMA baselines."""
            for w in windows:
                cls.data[f'sma_{w}'] = cls.data['prev_close'].rolling(window=w, min_periods=1).mean()

        @classmethod
        def calculate_bollinger_bands(cls, 
                                    window1: int = 14, num_std1: float = 2.5,
                                    window2: int = 7, num_std2: float = 1.5):
            """Calculate Bollinger Bands (uses bb_middle for SMA14)."""
            cls.data['bb_middle'] = cls.data['prev_close'].rolling(window=window1, min_periods=1).mean()
            rolling_std1 = cls.data['prev_close'].rolling(window=window1).std()
            cls.data['bb_upper'] = cls.data['bb_middle'] + (rolling_std1 * num_std1)
            cls.data['bb_lower'] = cls.data['bb_middle'] - (rolling_std1 * num_std1)

        @classmethod
        def identify_regimes(cls, window: int = 5, delta: float = 0.8, h_factor=1.5):
            """Identify market regimes with fallbacks for short datasets."""
            rolling_sigma = cls.data['prev_close'].rolling(window=window).std()
            rolling_h = h_factor * rolling_sigma
            
            # Primary Neural-Quant Conditions (Requires Hurst/FDI)
            cond_bull = (cls.data['cusum_hi'] > rolling_h) & (cls.data['hurst'] > 0.5) & (cls.data['fdi'] < 1.5)
            cond_bear = (cls.data['cusum_lo'] > rolling_h) & (cls.data['hurst'] > 0.5) & (cls.data['fdi'] < 1.5)
            
            # Secondary Fallback: SMA Cross & RSI
            # Used if Hurst/FDI are NaN (common in short history)
            price = cls.data['prev_close']
            sma20 = cls.data.get('sma_20', price)
            rsi14 = cls.data.get('rsi_14', 50)
            
            fallback_bull = (price > sma20) & (rsi14 > 55)
            fallback_bear = (price < sma20) & (rsi14 < 45)

            cls.data['regime'] = np.select(
                [
                    cond_bull,
                    cond_bear,
                    (cls.data['hurst'].isna() | cls.data['fdi'].isna()) & fallback_bull,
                    (cls.data['hurst'].isna() | cls.data['fdi'].isna()) & fallback_bear
                ],
                ['Bullish (Neural)', 'Bearish (Neural)', 'Bullish (Trend)', 'Bearish (Trend)'],
                default='Neutral (No Trend)'
            )

    @classmethod
    def process_data(cls, data: list):
        """Processes historical data using the manual Indicators suite."""
        df = pd.DataFrame(data)
        # Ensure date is a string for absolute Plotly alignment
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        elif 'timestamp' in df.columns:
            df['date'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d')
            
        cls.Indicators.initialize(df)
        cls.Indicators.calculate_prev_ohlcv()
        cls.Indicators.apply_kalman_filter()
        cls.Indicators.rolling_hurst_exponent()
        cls.Indicators.calculate_cusum()
        cls.Indicators.calculate_fdi()
        cls.Indicators.calculate_supertrend()
        cls.Indicators.calculate_rsi()
        cls.Indicators.calculate_macd()
        cls.Indicators.calculate_moving_averages() 
        cls.Indicators.calculate_bollinger_bands()
        cls.Indicators.identify_regimes()
        return cls.Indicators.data

    @classmethod
    def generate_technical_plot(cls, data: list, symbol: str) -> dict:
        """Generates the multi-pane Plotly figure using manual indicators."""
        df = cls.process_data(data)
        if df.empty:
            return {"error": "Processing failed: Data empty after shift/dropna"}

        # 🔹 Setup Dashboard: Main (70%) + Momentum (30%)
        fig = make_subplots(
            rows=2, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.03, 
            row_heights=[0.7, 0.3]
        )

        # 1. 🕯️ Main Candlestick Chart (prev_ohlcv)
        fig.add_trace(go.Candlestick(
            x=df['date'],
            open=df['prev_open'], high=df['prev_high'], low=df['prev_low'], close=df['prev_close'],
            name=f"{symbol} OHLC",
            increasing_line_color='#10b981', 
            decreasing_line_color='#f43f5e'
        ), row=1, col=1)

        # 2. Kalman Smoothed Price
        if 'prev_filtered_close' in df.columns:
            fig.add_trace(go.Scatter(x=df['date'], y=df['prev_filtered_close'], name='Kalman Filter', line=dict(color='#8b5cf6', width=1.5)), row=1, col=1)

        # 3. Supertrend Overlay
        if 'supertrend' in df.columns:
            fig.add_trace(go.Scatter(x=df['date'], y=df['supertrend'], name='Supertrend', mode='lines', line=dict(width=2, color='#fcd34d')), row=1, col=1)

        # 4. Bollinger Bands
        if 'bb_upper' in df.columns:
            fig.add_trace(go.Scatter(x=df['date'], y=df['bb_upper'], name='BB Upper', line=dict(color='rgba(255,255,255,0.2)', width=0.5), showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(x=df['date'], y=df['bb_lower'], name='BB Lower', fill='tonexty', fillcolor='rgba(255,255,255,0.03)', line=dict(color='rgba(255,255,255,0.2)', width=0.5), showlegend=False), row=1, col=1)

        # 5. RSI (Dual-Band) In Subplot
        if 'rsi_14' in df.columns:
            fig.add_trace(go.Scatter(x=df['date'], y=df['rsi_14'], name='RSI 14', line=dict(color='#c084fc', width=1.5)), row=2, col=1)
            if 'rsi_7' in df.columns:
                fig.add_trace(go.Scatter(x=df['date'], y=df['rsi_7'], name='RSI 7', line=dict(color='#38bdf8', width=1, dash='dot')), row=2, col=1)
            
            fig.add_hline(y=70, line_dash="dash", line_color="rgba(244,63,94,0.3)", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="rgba(16,185,129,0.3)", row=2, col=1)

        # Matte Styling
        fig.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, r=40, b=40, l=40),
            font=dict(color='#ffffff', family='var(--outfit-font)'),
            xaxis=dict(showgrid=False, rangeslider=dict(visible=False), tickfont=dict(color='#ffffff')),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)', side='right', tickfont=dict(color='#ffffff')),
            yaxis2=dict(showgrid=False, range=[0, 100], tickfont=dict(color='#ffffff')),
            dragmode='pan',
            height=600,
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor='rgba(215, 215, 215, 0.9)', # Institutional grey card
                font_size=11,
                font_color='black', # Pure black text for high contrast
                font_family='var(--outfit-font)',
                bordercolor='rgba(0,0,0,0)'
            ),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, 
                font=dict(size=10, color='black'),
                bgcolor='rgba(215, 215, 215, 0.9)', # High-contrast institutional grey
                borderwidth=0
            )
        )

        return json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

technical_analyzer = TechnicalAnalyzer()
