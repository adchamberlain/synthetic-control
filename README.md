# Synthetic Control Method: Pricing Experiment Demo

A Python teaching example demonstrating the **synthetic control method** for causal inference, applied to a simulated pricing experiment in France.

## What is the Synthetic Control Method?

The synthetic control method is a statistical technique for estimating causal effects in observational studies, particularly useful when:

- You have a single treated unit (e.g., one country, one region)
- You have panel data with multiple time periods
- Randomized experiments aren't feasible

The method constructs a "synthetic" version of the treated unit by finding a weighted combination of control units that best matches the treated unit's pre-treatment trajectory. The treatment effect is then estimated as the difference between the treated unit and its synthetic counterpart in the post-treatment period.

**Key paper:** Abadie, A., Diamond, A., & Hainmueller, J. (2010). "Synthetic Control Methods for Comparative Case Studies." *Journal of the American Statistical Association*, 105(490), 493-505.

## This Example

This script simulates a pricing experiment scenario:

- **Treated unit:** France (where a price change was implemented)
- **Donor pool:** Germany, Spain, Italy, Netherlands, Belgium
- **Outcome:** Revenue per user
- **Timeline:** 20 weeks pre-treatment, 8 weeks post-treatment

The script:
1. Generates simulated panel data with realistic country-level variation
2. Fits a synthetic control model using `pysyncon`
3. Produces a visualization comparing France to its synthetic control
4. Reports the estimated average treatment effect (ATT)

## Installation

```bash
# Clone the repository
git clone https://github.com/adchamberlain/synthetic-control.git
cd synthetic-control

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python synthetic_control_viz.py
```

### Output

The script produces:
- `synthetic_control_chart.png` - High-resolution PNG (300 DPI)
- `synthetic_control_chart.pdf` - Vector PDF for presentations
- Console output with donor weights and treatment effect estimates

Example console output:
```
Donor Pool Weights:
  Germany: 0.4521
  Spain: 0.0000
  Italy: 0.1832
  Netherlands: 0.3647
  Belgium: 0.0000

Chart saved as 'synthetic_control_chart.png' and 'synthetic_control_chart.pdf'

Key metrics:
  - Pre-treatment periods: 20 weeks
  - Post-treatment periods: 8 weeks
  - Average Treatment Effect (ATT): €0.523 (1.12%)
```

## Visualization

The chart shows:
- **Blue line:** France (the treated market)
- **Green dashed line:** Synthetic control (weighted combination of donor countries)
- **Red shaded area:** Post-treatment period

A successful synthetic control fit will show the two lines tracking closely in the pre-treatment period, with any divergence in the post-treatment period representing the causal effect of the intervention.

## Customization

Key parameters in the script that can be modified:

```python
n_pre = 20           # Number of pre-treatment periods
n_post = 8           # Number of post-treatment periods
countries = [...]    # List of countries (first is treated by default)
```

## Dependencies

- Python 3.8+
- numpy
- pandas
- matplotlib
- pysyncon

## License

MIT License - see [LICENSE](LICENSE) for details.

## References

- [pysyncon documentation](https://pysyncon.readthedocs.io/)
- Abadie, A., Diamond, A., & Hainmueller, J. (2010). Synthetic Control Methods for Comparative Case Studies. *JASA*, 105(490), 493-505.
- Abadie, A. (2021). Using Synthetic Controls: Feasibility, Data Requirements, and Methodological Aspects. *Journal of Economic Literature*, 59(2), 391-425.
