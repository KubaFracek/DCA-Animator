import argparse
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
import matplotlib.patheffects as pe
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.widgets import Button
from PIL import Image
import warnings
from datetime import timedelta
import os

warnings.simplefilter(action='ignore')

def parse_args():
    parser = argparse.ArgumentParser(description="DCA Strategy Visualizer")
    parser.add_argument('--symbol', type=str, default="MCD", help="Stock or Crypto ticker symbol (e.g., 'MCD', 'BTC-USD', 'AAPL')")
    parser.add_argument('--title', type=str, default="MCDONALD'S", help="Title to display on the video")
    parser.add_argument('--start', type=str, default="2008-01-01", help="Start Date (YYYY-MM-DD)")
    parser.add_argument('--end', type=str, default="2026-01-01", help="End Date (YYYY-MM-DD)")
    parser.add_argument('--monthly', type=int, default=100, help="Monthly investment amount ($)")
    parser.add_argument('--color', type=str, default="#FFC72C", help="Brand HEX color (e.g. '#FFC72C' for McDonald's)")
    parser.add_argument('--output', type=str, default="MCDONALDS_DCA_Final.mp4", help="Output MP4 filename")
    parser.add_argument('--step', type=int, default=3, help="Step size for animation")
    parser.add_argument('--speed', type=int, default=15, help="Animation speed (ms per frame)")
    parser.add_argument('--logo', type=str, default="logo.png", help="Path to logo file (optional)")
    return parser.parse_args()

def get_logo_image(logo_path):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(script_dir, logo_path)
        if os.path.exists(full_path):
            return Image.open(full_path).convert("RGBA")
        return None
    except Exception:
        return None

def prepare_data(args):
    print(f"1. Pobieranie danych dla {args.symbol}...")
    try:
        ticker_obj = yf.Ticker(args.symbol)
        data = ticker_obj.history(start=args.start, end=args.end)
        if data.empty: return None

        df = pd.DataFrame(index=data.index)
        df['Price'] = data['Close']
        df['Month'] = df.index.to_period('M')

        buy_dates = df.groupby('Month').head(1).index
        df['Cash_Flow'] = 0.0
        df.loc[buy_dates, 'Cash_Flow'] = args.monthly

        df['New_Shares'] = df['Cash_Flow'] / df['Price']
        df['Total_Shares'] = df['New_Shares'].fillna(0).cumsum()

        df['Raw_Value'] = df['Total_Shares'] * df['Price']
        df['Portfolio_Value'] = df['Raw_Value'].rolling(window=14, min_periods=1).mean()
        df['Total_Invested'] = df['Cash_Flow'].cumsum()

        df_resampled = df.iloc[::args.step].copy()
        return df_resampled
    except Exception as e:
        print(f"Błąd danych: {e}")
        return None

def create_animation_object(df, logo_img, args, app_state, is_preview=True):
    plt.style.use('dark_background')
    COLOR_BG = '#000000'
    COLOR_ASSET = args.color
    COLOR_WHITE = '#ffffff'
    COLOR_GRAY = '#888888'
    COLOR_CASH = '#aaaaaa'

    current_dpi = 70 if is_preview else 120
    fig = plt.figure(figsize=(9, 16), facecolor=COLOR_BG, dpi=current_dpi)

    outline = [pe.withStroke(linewidth=4, foreground='black')]
    outline_thin = [pe.withStroke(linewidth=3, foreground='black')]

    if logo_img:
        imagebox = OffsetImage(logo_img, zoom=0.18)
        ab = AnnotationBbox(imagebox, (0.5, 0.88), frameon=False, xycoords='figure fraction', box_alignment=(0.5, 0.5))
        fig.add_artist(ab)

    fig.text(0.5, 0.73, args.title, color='white', fontsize=45, ha='center', fontweight='bold', fontname='Arial')
    fig.text(0.5, 0.68, "PORTFOLIO VALUE", color=COLOR_GRAY, fontsize=14, ha='center', fontweight='bold')
    lbl_portfolio = fig.text(0.5, 0.62, "$0", color=COLOR_WHITE, fontsize=65, fontweight='bold', ha='center', fontname='Arial')
    lbl_profit = fig.text(0.5, 0.56, "+0%", color=COLOR_ASSET, fontsize=50, fontweight='bold', ha='center')

    fig.text(0.5, 0.48, "TOTAL INVESTED", color=COLOR_GRAY, fontsize=14, ha='center', fontweight='bold')
    lbl_invested = fig.text(0.5, 0.44, "$0", color=COLOR_CASH, fontsize=32, ha='center', fontname='Arial', fontweight='bold')

    ax = fig.add_axes([0.12, 0.10, 0.83, 0.28], facecolor=COLOR_BG)

    fig.text(0.5, 0.05, "DCA STRATEGY SIMULATION", color=COLOR_GRAY, fontsize=12, ha='center')
    fig.text(0.5, 0.03, f"${args.monthly} / MONTH", color=COLOR_ASSET, fontsize=14, ha='center', fontweight='bold')

    for spine in ax.spines.values(): spine.set_visible(False)
    ax.tick_params(axis='x', colors=COLOR_GRAY, labelsize=10, pad=5)
    ax.tick_params(axis='y', colors=COLOR_GRAY, labelsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mtick.MaxNLocator(nbins=5))
    ax.grid(axis='y', color=COLOR_GRAY, linestyle='-', linewidth=0.5, alpha=0.2)
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))

    lbl_watermark = ax.text(0.5, 0.5, "2010", transform=ax.transAxes,
                            color='white', alpha=0.08, fontsize=90, fontweight='bold',
                            ha='center', va='center', zorder=0)

    line_inv, = ax.plot([], [], color=COLOR_CASH, linestyle='-', linewidth=3, zorder=3)
    line_val, = ax.plot([], [], color=COLOR_ASSET, linewidth=4, zorder=5)
    dot_inv, = ax.plot([], [], 'o', color=COLOR_CASH, markersize=7, zorder=4)
    dot_val, = ax.plot([], [], 'o', color=COLOR_ASSET, markersize=9, zorder=6)

    float_val_text = ax.text(0, 0, "", color=COLOR_ASSET, fontsize=14, fontweight='bold', ha='right', zorder=10)
    float_val_text.set_path_effects(outline)
    float_inv_text = ax.text(0, 0, "", color='white', fontsize=11, fontweight='bold', ha='right', zorder=10)
    float_inv_text.set_path_effects(outline_thin)

    initial_cap = max(500, args.monthly * 3)
    ax.set_ylim(0, initial_cap)
    start_window = df.index[0] + timedelta(days=365)
    ax.set_xlim(df.index[0], start_window)

    def update(frame):
        curr_df = df.iloc[:frame+1]
        if curr_df.empty: return

        last_date = curr_df.index[-1]
        val_smooth = curr_df['Portfolio_Value'].iloc[-1]
        inv_now = curr_df['Total_Invested'].iloc[-1]
        profit_pct = ((val_smooth - inv_now) / inv_now) * 100 if inv_now > 0 else 0

        lbl_portfolio.set_text(f"${val_smooth:,.0f}")
        lbl_profit.set_text(f"{profit_pct:+.0f}%")
        lbl_invested.set_text(f"${inv_now:,.0f}")
        lbl_watermark.set_text(last_date.strftime('%Y'))

        line_val.set_data(curr_df.index, curr_df['Portfolio_Value'])
        line_inv.set_data(curr_df.index, curr_df['Total_Invested'])
        dot_val.set_data([last_date], [val_smooth])
        dot_inv.set_data([last_date], [inv_now])

        float_val_text.set_position((last_date, val_smooth))
        float_val_text.set_text(f"${val_smooth:,.0f}")
        float_inv_text.set_position((last_date, inv_now))
        float_inv_text.set_text(f"${inv_now:,.0f}")

        for c in ax.collections: c.remove()
        ax.fill_between(curr_df.index, 0, curr_df['Portfolio_Value'], color=COLOR_ASSET, alpha=0.25, zorder=2)

        current_ylim = ax.get_ylim()[1]
        max_val_on_screen = max(val_smooth, inv_now)
        if max_val_on_screen > current_ylim * 0.85:
            ax.set_ylim(0, max_val_on_screen * 1.4)

        if len(curr_df) > 1:
            ax.set_xlim(df.index[0], last_date + timedelta(days=90))

        return line_val, line_inv

    btn = None
    if is_preview:
        fig.canvas.manager.set_window_title(f"{args.title} DCA - Simulation")
        btn_ax = fig.add_axes([0.65, 0.94, 0.30, 0.04])
        btn = Button(btn_ax, 'RENDER MP4', color=COLOR_ASSET, hovercolor='#ffffff')
        btn.label.set_color('white')
        btn.label.set_fontweight('bold')

        def on_click(event):
            print("\n>>> START RENDEROWANIA...")
            app_state["render_requested"] = True
            plt.close(fig)

        btn.on_clicked(on_click)

    ani = animation.FuncAnimation(fig, update, frames=len(df), interval=args.speed, repeat=is_preview)
    return fig, ani, btn

def main():
    args = parse_args()
    app_state = {"render_requested": False}

    script_dir = os.path.dirname(os.path.abspath(__file__))
    FFMPEG_PATH = os.path.join(script_dir, "ffmpeg.exe")
    if os.path.exists(FFMPEG_PATH):
        plt.rcParams['animation.ffmpeg_path'] = FFMPEG_PATH

    df = prepare_data(args)
    if df is None: return

    logo_img = get_logo_image(args.logo)

    print(f"2. Uruchamianie podglądu dla {args.title}...")
    fig_prev, ani_prev, btn_prev = create_animation_object(df, logo_img, args, app_state, is_preview=True)
    plt.show()

    if app_state["render_requested"]:
        print("3. Renderowanie pliku wideo...")
        fig_save, ani_save, _ = create_animation_object(df, logo_img, args, app_state, is_preview=False)
        try:
            ani_save.save(args.output, writer='ffmpeg', fps=30, dpi=120, bitrate=6000)
            print(f"\n✅ GOTOWE! Zapisano plik: {args.output}")
        except Exception as e:
            print("\n❌ BŁĄD ZAPISU:", e)

if __name__ == "__main__":
    main()
