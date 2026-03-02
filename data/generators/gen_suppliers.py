"""
Generates the Suppliers table (15 suppliers, varied ratings and lead times).
No FK dependencies — build first alongside gen_products.py.
"""
import numpy as np
import pandas as pd
from faker import Faker

from config.settings import NUM_SUPPLIERS, RANDOM_SEED

# Supplier countries with realistic distribution weights
_COUNTRIES = [
    "United States", "China", "Germany", "Mexico", "India",
    "South Korea", "Taiwan", "Japan", "Canada", "Vietnam",
]
_COUNTRY_WEIGHTS = [0.20, 0.20, 0.10, 0.10, 0.10, 0.08, 0.08, 0.06, 0.05, 0.03]

# Lead time distribution: mean and std per country cluster
_LEAD_TIME_PARAMS = {
    "United States": (5,  2),
    "Canada":        (6,  2),
    "Mexico":        (8,  3),
    "Germany":       (12, 3),
    "Japan":         (15, 4),
    "South Korea":   (14, 4),
    "Taiwan":        (14, 4),
    "China":         (20, 5),
    "India":         (18, 5),
    "Vietnam":       (16, 5),
}

# Rating: draw from Beta distribution, scale to [1, 5]
_RATING_ALPHA = 5.0   # skewed toward higher ratings
_RATING_BETA  = 2.0


def generate_suppliers(seed: int = RANDOM_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    fake = Faker()
    Faker.seed(seed)

    countries = rng.choice(
        _COUNTRIES, size=NUM_SUPPLIERS, p=_COUNTRY_WEIGHTS
    ).tolist()

    records = []
    for i, country in enumerate(countries):
        # Unique company name
        name = f"{fake.company()} Supply"

        # Lead time from country-specific normal distribution (clipped to [2, 45])
        mu, sigma = _LEAD_TIME_PARAMS[country]
        lead_time = int(np.clip(rng.normal(mu, sigma), 2, 45))

        # Rating in [1.0, 5.0] using Beta distribution
        raw = rng.beta(_RATING_ALPHA, _RATING_BETA)
        rating = round(float(1.0 + raw * 4.0), 1)

        records.append({
            "SupplierID":      i + 1,
            "SupplierName":    name,
            "Country":         country,
            "AverageLeadTime": lead_time,
            "Rating":          rating,
        })

    df = pd.DataFrame(records)
    assert len(df) == NUM_SUPPLIERS, f"Expected {NUM_SUPPLIERS} suppliers, got {len(df)}"
    return df


if __name__ == "__main__":
    df = generate_suppliers()
    print(df.to_string())
