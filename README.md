# DCA Investment Animator

A Python script that generates engaging, animated vertical videos (perfect for TikTok, Instagram Reels, and YouTube Shorts) visualizing the **Dollar Cost Averaging (DCA)** investment strategy for various stocks and cryptocurrencies.

## 📈 Example Output

The script generates an MP4 video showing the growth of a portfolio over time, comparing the total invested amount (cash) against the actual value of the portfolio (asset value), complete with a dynamic chart and percent return.

## 🛠️ Features

- Fetches historical market data automatically via Yahoo Finance (`yfinance`).
- Accurately tracks shares accumulated and dollar-cost averaging metrics over time.
- Smoothly animates the timeline using `matplotlib.animation`.
- High-quality vertical output format (9:16 vertical).
- Multi-asset configuration via command line arguments (no need to edit code!).
- Interactive preview before final `ffmpeg` rendering.

## 🚀 Installation & Requirements

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/dca-animator.git
   cd dca-animator
   ```

2. **Install Python dependencies:**
   Make sure you have Python 3.8+ installed. Install the required libraries using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg:**
   The script requires `ffmpeg` to render the `.mp4` video files. 
   - **Windows:** Download the `ffmpeg.exe` binary and place it in the same directory as the script, or add it to your system PATH.
   - **Mac:** `brew install ffmpeg`
   - **Linux:** `sudo apt install ffmpeg`

## ⚙️ Usage (Command Line)

You no longer need to edit the script to change assets! Use standard command line arguments to generate any asset visualization. 

**Basic Run (Defaults to McDonald's):**
```bash
python wizualizacja.py
```

**Generate a Custom DCA Simulation:**
```bash
python wizualizacja.py --symbol AAPL --title "APPLE" --color "#A3AAAE" --monthly 200 --output APPLE_DCA.mp4
```

**Crypto Example (Bitcoin):**
```bash
python wizualizacja.py --symbol BTC-USD --title "BITCOIN" --start 2014-01-01 --color "#F2A900" --output BTC_DCA.mp4
```

### Available Arguments:
- `--symbol` : Stock or Crypto ticker used by Yahoo Finance (e.g., `MCD`, `AAPL`, `BTC-USD`). Default is `MCD`.
- `--title` : Text string of the title on the video. Default is `MCDONALD'S`.
- `--start` : Simulation start date (YYYY-MM-DD). Default `2008-01-01`.
- `--end` : Simulation end date (YYYY-MM-DD). Default `2026-01-01`.
- `--monthly` : Monthly investment amount in USD. Default is `100`.
- `--color` : Hex color used for the brand chart. Default is `#FFC72C`.
- `--output` : The target file name for rendering. Default is `MCDONALDS_DCA_Final.mp4`.
- `--logo` : Path to a custom logo PNG. Default `logo.png`.
- `--step` : Interval steps (for animation speed). Default `3`.
- `--speed` : Milliseconds per frame (ms). Default `15`.


A window will pop up showing a live preview of the animation. If you're happy with the alignment and colors, click the **"RENDER MP4"** button in the top right corner. The script will close the preview and begin rendering the high-quality video in the background.

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).
