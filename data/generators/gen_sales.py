"""
Generates the Sales table — daily sales per product with:
  - Linear upward trend (business growth)
  - Fourier-encoded annual seasonality (peak in Q4, trough in Q1)
  - Weekly seasonality (weekday peaks, weekend troughs)
  - Product-specific baseline demand
  - Gaussian noise

This is the most important generator for forecasting quality.
Depends on Products (ProductID FK).
"""
import numpy as np
import pandas as pd

from config.settings import END_DATE, RANDOM_SEED, START_DATE


def _fourier_annual(t: np.ndarray, n_terms: int = 3) -> np.ndarray:
    """
    Returns a seasonality signal in [-1, 1] using Fourier series
    with annual period. t is fractional year (0 to 1).
    """
    signal = np.zeros_like(t, dtype=float)
    for k in range(1, n_terms + 1):
        signal += np.sin(2 * np.pi * k * t) / k
    # Normalise to [-1, 1]
    peak = np.max(np.abs(signal)) or 1.0
    return signal / peak


def generate_sales(
    products_df: pd.DataFrame,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Returns Sales DataFrame with one row per (product, date) where sales > 0.
    """
    rng = np.random.default_rng(seed)
    dates = pd.date_range(START_DATE, END_DATE, freq="D")
    n_days = len(dates)

    # Fractional position within year [0, 1]
    year_frac = np.array([
        (d.timetuple().tm_yday - 1) / 365.0 for d in dates
    ])

    # Annual seasonality: Q4 peak (shift by -0.25 so peak lands at day ~275)
    annual_signal = _fourier_annual(year_frac - 0.25)

    # Weekly seasonality: Mon–Fri slightly higher than Sat–Sun
    weekday = np.array([d.weekday() for d in dates])  # 0=Mon, 6=Sun
    weekly_signal = np.where(weekday < 5, 0.15, -0.30)

    # Linear trend: 25% growth over 2 years
    trend = np.linspace(0.0, 0.25, n_days)

    records = []
    sale_id = 1

    for _, row in products_df.iterrows():
        product_id = int(row["ProductID"])
        unit_price = float(row["UnitPrice"])

        # Base daily demand: derived from safety stock (heuristic)
        # Safety stock = 7 days of demand → base_demand = SS / 7
        base_demand = max(1.0, float(row["SafetyStockLevel"]) / 7.0)

        # Scale factors randomised per product so each has distinct pattern
        seasonality_strength = float(rng.uniform(0.10, 0.40))
        weekly_strength = float(rng.uniform(0.05, 0.20))
        noise_std = float(rng.uniform(0.08, 0.25))

        # Demand signal (continuous)
        demand = (
            base_demand
            * (1.0 + trend)
            * (1.0 + seasonality_strength * annual_signal)
            * (1.0 + weekly_strength * weekly_signal)
        )

        # Add multiplicative noise
        noise = rng.normal(1.0, noise_std, size=n_days)
        demand = demand * noise

        # Convert to integer units, clip to >= 1 on sale days
        qty = np.maximum(1, np.round(demand).astype(int))

        # Not every product sells every day (50–90% of days have a sale)
        sale_prob = float(rng.uniform(0.50, 0.90))
        sale_mask = rng.random(size=n_days) < sale_prob

        for i, (date, sold, mask) in enumerate(zip(dates, qty, sale_mask)):
            if not mask:
                continue
            revenue = round(float(sold) * unit_price, 2)
            records.append({
                "SaleID":      sale_id,
                "ProductID":   product_id,
                "SaleDate":    date.date().isoformat(),
                "QuantitySold": int(sold),
                "Revenue":     revenue,
            })
            sale_id += 1

    df = pd.DataFrame(records)
    print(f"[gen_sales] Generated {len(df):,} sales records across {len(products_df)} products")
    return df


if __name__ == "__main__":
    from data.generators.gen_products import generate_products
    products = generate_products()
    sales = generate_sales(products)
    print(sales.head())
    print(f"Total revenue: ${sales['Revenue'].sum():,.2f}")
