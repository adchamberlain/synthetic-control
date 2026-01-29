"""
Synthetic Control Visualization for Pricing Experiment
Uses pysyncon package to fit actual synthetic control model
Shows France (treated) vs Synthetic Control (weighted donor pool)
For presentation slide on causal inference methods
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving files

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pysyncon import Dataprep, Synth

# Set random seed for reproducibility
np.random.seed(42)

# ============== PARAMETERS ==============
n_pre = 20   # 20 weeks pre-treatment
n_post = 8   # 8 weeks post-treatment
n_total = n_pre + n_post
treatment_week = n_pre + 1  # Treatment starts at week 21

# Define countries (France = treated, others = donor pool)
countries = ['France', 'Germany', 'Spain', 'Italy', 'Netherlands', 'Belgium']
treated_unit = 'France'
control_units = [c for c in countries if c != treated_unit]

# ============== SIMULATE PANEL DATA ==============
def generate_country_data(country, is_treated=False):
    """Generate revenue time series for a country."""
    weeks = np.arange(1, n_total + 1)
    
    # Base revenue with country-specific offset
    country_offsets = {
        'France': 0,
        'Germany': 0.8,
        'Spain': -0.5,
        'Italy': -0.3,
        'Netherlands': 0.6,
        'Belgium': 0.2
    }
    base = 45 + country_offsets.get(country, 0)
    
    # Common trend component (all countries share)
    trend = 0.04 * weeks
    
    # Seasonal pattern (slightly different phases per country)
    phase_offsets = {
        'France': 0,
        'Germany': 0.2,
        'Spain': 0.4,
        'Italy': 0.3,
        'Netherlands': 0.1,
        'Belgium': 0.25
    }
    seasonal = 0.5 * np.sin(2 * np.pi * weeks / 13 + phase_offsets.get(country, 0))
    
    # Country-specific noise
    noise = np.random.normal(0, 0.15, n_total)
    
    # Base revenue series
    revenue = base + trend + seasonal + noise
    
    # Add treatment effect for France (gradual lift from 0% to ~2%)
    if is_treated:
        treatment_effect = np.zeros(n_total)
        post_weeks = weeks[n_pre:] - n_pre
        lift_curve = 0.02 * (post_weeks / n_post)  # Gradually builds to 2%
        treatment_effect[n_pre:] = revenue[n_pre:] * lift_curve
        revenue = revenue + treatment_effect
    
    return revenue

# Build panel DataFrame
data_records = []
for country in countries:
    is_treated = (country == treated_unit)
    revenue = generate_country_data(country, is_treated=is_treated)
    
    for week in range(1, n_total + 1):
        data_records.append({
            'country': country,
            'week': week,
            'revenue': revenue[week - 1]
        })

df = pd.DataFrame(data_records)

# Add a numeric country ID for pysyncon
country_ids = {c: i+1 for i, c in enumerate(countries)}
df['country_id'] = df['country'].map(country_ids)
treated_id = country_ids[treated_unit]
control_ids = [country_ids[c] for c in control_units]

# ============== FIT SYNTHETIC CONTROL ==============
# Prepare data for pysyncon
dataprep = Dataprep(
    foo=df,
    predictors=['revenue'],
    predictors_op='mean',
    time_predictors_prior=range(1, treatment_week),
    dependent='revenue',
    unit_variable='country_id',
    time_variable='week',
    treatment_identifier=treated_id,
    controls_identifier=control_ids,
    time_optimize_ssr=range(1, treatment_week),
)

# Fit the synthetic control model
synth = Synth()
synth.fit(dataprep=dataprep)

# Get the weights
weights = synth.weights(round=4)
print("\nDonor Pool Weights:")
for idx, weight in weights.items():
    country_name = [c for c, cid in country_ids.items() if cid == idx][0]
    print(f"  {country_name}: {weight:.4f}")

# Extract treated path
treated_path = df[df['country'] == treated_unit].set_index('week')['revenue']

# Compute synthetic control path using weights
# Get outcome matrices for full time period
Z0, Z1 = dataprep.make_outcome_mats(time_period=range(1, n_total + 1))
# Synthetic control is weighted combination of control units
synthetic_path = (Z0 @ weights).values

# ============== PLOTTING ==============
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(9, 7))

weeks = np.arange(1, n_total + 1)

# Plot lines
ax.plot(weeks, synthetic_path, color='#27AE60', linewidth=2.5, 
        label='Synthetic Control (Weighted Donor Pool)', linestyle='--', alpha=0.9)
ax.plot(weeks, treated_path.values, color='#2471A3', linewidth=2.5, 
        label='France (Treated Market)')

# Shade the treatment period
ax.axvspan(n_pre + 0.5, n_total + 0.5, alpha=0.15, color='#E74C3C', 
           label='Treatment Period')

# Add vertical line at treatment start
ax.axvline(x=n_pre + 0.5, color='#E74C3C', linestyle='-', linewidth=1.5, alpha=0.7)

# Add annotation for treatment start (positioned inside chart area)
ax.annotate('Price Change\nImplemented', 
            xy=(n_pre + 0.5, 47), 
            xytext=(n_pre - 3, 48),
            fontsize=13, ha='center',
            arrowprops=dict(arrowstyle='->', color='#E74C3C', lw=1.5),
            color='#E74C3C', fontweight='bold')

# Labels and title
ax.set_xlabel('Week', fontsize=16, fontweight='bold')
ax.set_ylabel('Revenue per User (€)', fontsize=16, fontweight='bold')
ax.set_title('Synthetic Control Method: France Pricing Experiment', 
             fontsize=18, fontweight='bold', pad=15)

# Increase tick label sizes
ax.tick_params(axis='both', labelsize=12)

# Customize x-axis (show every week)
ax.set_xticks(weeks)
ax.set_xlim(0.5, n_total + 1.5)

# Set y-axis limits
ax.set_ylim(43, 49)

# Add period labels
ax.text(n_pre / 2, ax.get_ylim()[0] + 0.5, 'Pre-Treatment Period', 
        ha='center', fontsize=13, color='#555555', style='italic')
ax.text(n_pre + (n_post / 2) + 0.5, ax.get_ylim()[0] + 0.5, 'Post-Treatment Period', 
        ha='center', fontsize=13, color='#555555', style='italic')

# Legend
ax.legend(loc='upper left', fontsize=13, framealpha=0.95)

# Add donor weights note
weight_str = ', '.join([f"{c}: {weights.get(country_ids[c], 0):.2f}" 
                        for c in control_units])
ax.text(0.98, 0.02, f'Donor Weights: {weight_str}', 
        transform=ax.transAxes, fontsize=10, ha='right', va='bottom',
        color='#888888', style='italic')

# Clean up
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()

# Save high-resolution image for presentation
plt.savefig('synthetic_control_chart.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.savefig('synthetic_control_chart.pdf', bbox_inches='tight', 
            facecolor='white', edgecolor='none')

print(f"\nChart saved as 'synthetic_control_chart.png' and 'synthetic_control_chart.pdf'")
print(f"\nKey metrics:")
print(f"  - Pre-treatment periods: {n_pre} weeks")
print(f"  - Post-treatment periods: {n_post} weeks")

# Calculate and report treatment effect
post_treated = treated_path.loc[treatment_week:n_total].mean()
post_synthetic = np.mean(synthetic_path[n_pre:])
att = post_treated - post_synthetic
att_pct = (att / post_synthetic) * 100
print(f"  - Average Treatment Effect (ATT): €{att:.3f} ({att_pct:.2f}%)")
