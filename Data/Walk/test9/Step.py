import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks

# ==============================================================================
#                 ۱. تنظیمات و پارامترهای اصلی (Main Configuration)
# ==============================================================================
FILE_NAME = "walking_data_9.csv"  # نام فایل CSV ورودی

# --- تنظیمات فیلتر پایین‌گذر (Filter Settings) ---
CUTOFF_FREQ = 3       # فرکانس قطع (Cutoff Frequency - Hz)
FS = 50.0               # فرکانس نمونه‌برداری (Sampling Frequency - Hz)
FILTER_ORDER = 3        # درجه فیلتر (Filter Order)

# --- تنظیمات الگوریتم شمارش قدم (Step Detection Settings) ---
THRESHOLD_HEIGHT = 1.02 # خط آستانه ارتفاع برای تشخیص پیک (Threshold Height)
MIN_DISTANCE_SEC = 0.35 # حداقل فاصله زمانی بین دو قدم متوالی (بر حسب ثانیه)
# ==============================================================================


# تابع فیلتر پایین‌گذر باترورث (Butterworth Low-pass Filter)
def lowpass_filter(data, cutoff, fs, order=3):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)


def main():
    # ساخت مسیر دقیق فایل‌های ورودی و خروجی در فولدر کد
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(SCRIPT_DIR, FILE_NAME)
    filtered_csv_path = os.path.join(SCRIPT_DIR, "filtered_" + FILE_NAME)

    try:
        # ----------------------------------------------------------------------
        # گام ۱: خواندن داده‌ها از فایل CSV
        # ----------------------------------------------------------------------
        df = pd.read_csv(input_path)
        df["Time"] = pd.to_numeric(df["Time"], errors="coerce")
        df["Magnitude"] = pd.to_numeric(df["Magnitude"], errors="coerce")
        df = df.dropna()

        # ----------------------------------------------------------------------
        # گام ۲: رسم نمودار اول - اندازه شتاب خام بر حسب زمان (Raw Magnitude Plot)
        # ----------------------------------------------------------------------
        plt.figure(figsize=(10, 4))
        plt.plot(df["Time"], df["Magnitude"], color="purple", linewidth=1.5, label="Raw Magnitude")
        plt.title("Step 1: Raw Acceleration Magnitude vs Time", fontsize=12, fontweight="bold")
        plt.xlabel("Time (seconds)", fontsize=10)
        plt.ylabel("Magnitude", fontsize=10)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend(loc="upper right")
        plt.tight_layout()
        plt.savefig(os.path.join(SCRIPT_DIR, "1_raw_magnitude.png"), dpi=300)
        plt.show()

        # ----------------------------------------------------------------------
        # گام ۳: اعمال فیلتر پایین‌گذر و ذخیره در فایل CSV جدید
        # ----------------------------------------------------------------------
        df["Filtered_Magnitude"] = lowpass_filter(df["Magnitude"], CUTOFF_FREQ, FS, FILTER_ORDER)
        df.to_csv(filtered_csv_path, index=False)
        print(f"[INFO] Filtered data saved to: {filtered_csv_path}")

        # ----------------------------------------------------------------------
        # گام ۴: رسم نمودار دوم - سیگنال فیلتر شده و سیگنال خام کمرنگ
        # ----------------------------------------------------------------------
        plt.figure(figsize=(12, 5))
        plt.plot(df["Time"], df["Magnitude"], color="gray", alpha=0.4, label="Raw Magnitude (Noisy)")
        plt.plot(df["Time"], df["Filtered_Magnitude"], color="red", linewidth=2, label=f"Filtered Signal (Cutoff: {CUTOFF_FREQ} Hz)")
        plt.title(f"Step 2: Low-Pass Filtered Signal (Cutoff Frequency: {CUTOFF_FREQ} Hz)", fontsize=12, fontweight="bold")
        plt.xlabel("Time (seconds)", fontsize=10)
        plt.ylabel("Magnitude", fontsize=10)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend(loc="upper right")
        plt.tight_layout()
        plt.savefig(os.path.join(SCRIPT_DIR, "2_filtered_signal.png"), dpi=300)
        plt.show()

        # ----------------------------------------------------------------------
        # گام ۵: تشخیص قدم‌ها بر اساس ترشولد (Peak Detection)
        # ----------------------------------------------------------------------
        min_samples_distance = int(MIN_DISTANCE_SEC * FS)
        peak_indices, _ = find_peaks(
            df["Filtered_Magnitude"],
            height=THRESHOLD_HEIGHT,
            distance=min_samples_distance
        )

        # ----------------------------------------------------------------------
        # گام ۶: چاپ خروجی انگلیسی زمان گام‌ها در ترمینال
        # ----------------------------------------------------------------------
        print("\n" + "=" * 45)
        print("         STEP DETECTION RESULTS           ")
        print("=" * 45)
        for step_num, idx in enumerate(peak_indices, start=1):
            step_time = df["Time"].iloc[idx]
            print(f"Step {step_num}: detected at {step_time:.2f} seconds")
        print("-" * 45)
        print(f"Total Steps Detected: {len(peak_indices)}")
        print("=" * 45 + "\n")

        # ----------------------------------------------------------------------
        # گام ۷: رسم نمودار سوم - نمایش قدم‌ها (ضربدر)، خط ترشولد و سیگنال فیلترشده
        # ----------------------------------------------------------------------
        plt.figure(figsize=(12, 5))
        # رسم سیگنال خام کم‌رنگ جهت مقایسه دیداری کامل
        plt.plot(df["Time"], df["Magnitude"], color="gray", alpha=0.3, label="Raw Signal")
        # رسم سیگنال فیلترشده
        plt.plot(df["Time"], df["Filtered_Magnitude"], color="crimson", linewidth=1.8, label="Filtered Signal")
        
        # مشخص کردن قدم‌های کشف شده با علامت ضربدر مشکی
        plt.plot(
            df["Time"].iloc[peak_indices], 
            df["Filtered_Magnitude"].iloc[peak_indices], 
            "x", 
            color="black", 
            markersize=9, 
            markeredgewidth=2, 
            label=f"Detected Steps ({len(peak_indices)})"
        )

        # رسم خط چین ترشولد
        plt.axhline(y=THRESHOLD_HEIGHT, color="blue", linestyle="--", alpha=0.8, label=f"Threshold ({THRESHOLD_HEIGHT})")

        plt.title(f"Step 3: Step Detection Results (Cutoff: {CUTOFF_FREQ} Hz | Threshold: {THRESHOLD_HEIGHT})", fontsize=12, fontweight="bold")
        plt.xlabel("Time (seconds)", fontsize=10)
        plt.ylabel("Magnitude", fontsize=10)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend(loc="upper right")
        plt.tight_layout()
        plt.savefig(os.path.join(SCRIPT_DIR, "3_detected_steps.png"), dpi=300)
        plt.show()

    except FileNotFoundError:
        print(f"[ERROR] Could not find file: '{input_path}'")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()