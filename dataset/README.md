# NASA Space App Dataset

This directory contains all datasets used in the NASA Space App project.

## Directory Structure

```
dataset/
├── raw/           # Original, unmodified data files
├── processed/     # Cleaned and processed data
├── external/      # External data sources and APIs
└── metadata/      # Data descriptions and schemas
```

## Data Categories

### Raw Data (`raw/`)
- Original data files from NASA APIs
- Satellite imagery
- Telemetry data
- Mission data
- Astronomical observations

### Processed Data (`processed/`)
- Cleaned datasets ready for analysis
- Feature-engineered data
- Normalized and scaled data
- Train/validation/test splits

### External Data (`external/`)
- Third-party data sources
- API responses
- Reference datasets
- Supplementary information

### Metadata (`metadata/`)
- Data dictionaries
- Schema definitions
- Data lineage information
- Quality reports

## Data Sources

Common NASA data sources:
- NASA Open Data Portal
- NASA APIs (Earth, Mars, ISS, etc.)
- Satellite missions data
- Space weather data
- Exoplanet data

## Data Formats

Supported formats:
- CSV files
- JSON files
- Parquet files
- HDF5 files
- NetCDF files (for climate/weather data)
- FITS files (for astronomical data)

## Usage Guidelines

1. Always place original data in the `raw/` directory
2. Document data sources in `metadata/`
3. Keep processed data separate from raw data
4. Use consistent naming conventions
5. Include data validation scripts

## Data Privacy and Compliance

- Ensure all data usage complies with NASA's data policies
- Check licensing requirements for external data
- Document data provenance and attribution
- Remove any sensitive or personal information