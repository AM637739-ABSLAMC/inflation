# Inflation Report - Implementation Summary

## Report Structure (11 pages total)

### Section 1: Heatmaps (2 pages)
- **Page 1**: YoY Heatmap (2020-2025)
- **Page 2**: MoM Heatmap (2020-2025)
- 5 years × 12 months = readable cells
- Green-to-red color scheme
- All values visible (9pt font)

### Section 2: Top 5 Changes (2 pages)
- **Page 3**: Top 5 Inflationary Changes
  - Clean table with 4 columns
  - Horizontal bar chart (red)
- **Page 4**: Top 5 Deflationary Changes
  - Clean table with 4 columns
  - Horizontal bar chart (green)
- Based on latest month (Aug → Sept 2025)

### Section 3: Seasonality (7 pages)
- **Page 5**: Seasonal Heatmap Overview (all 5 indicators)
- **Pages 6-10**: Individual seasonal profiles (one per indicator)
  - Left: MoM seasonal pattern (line + shaded std dev)
  - Right: YoY seasonal pattern (line + shaded std dev)
  - Peak months annotated

**5 Indicators:**
1. Overall CPI
2. CPI ExVeggies
3. Core Inflation (Ex Food, Fuel, Light)
4. Personal Care & Effects
5. Food Inflation

## Key Features

✅ **Compact**: 11 focused pages
✅ **Economist-approved**: Line charts with confidence bands, not boxplots
✅ **Green-to-red**: Consistent color scheme
✅ **Seasonal heatmap**: Quick overview of all indicators
✅ **Peak annotations**: Identifies key months
✅ **5-year focus**: 2020-2025 (relevant period)
✅ **Proper tables**: Markdown format with clear columns
✅ **Latest month changes**: What's driving inflation NOW

## To Generate PDF

```bash
quarto render inflation_report_compact.qmd
```

Output: `inflation_report_compact.pdf`

## File Location
`/Users/nakshatragupta/Documents/Coding/inflation/inflation_report_compact.qmd`
