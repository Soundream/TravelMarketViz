# WiT Studio Episodes Word Cloud Generator

This project generates word cloud visualizations from the WiT Studio Episodes frequency data.

## Setup

1. Install the required dependencies:

```
pip install -r requirements.txt
```

2. Choose one of the scripts to run:

## Available Scripts

### 1. Basic Word Cloud

```
python generate_wordcloud.py
```

Generates a basic word cloud using default settings.

### 2. Customizable Word Cloud

```
python generate_custom_wordcloud.py
```

Allows customization via command line parameters:

```
python generate_custom_wordcloud.py background_color=black colormap=plasma max_words=100 mask_shape=circle output_name=my_wordcloud.png
```

### 3. Multiple Word Clouds

```
python generate_multiple_wordclouds.py
```

Generates 5 different word clouds with various styles:
- Default style (white background, viridis colormap)
- Dark style (black background, plasma colormap)
- Circle shape (white background, YlOrRd colormap)
- Rectangle shape (light yellow background, Blues colormap)
- High contrast (midnight blue background, autumn colormap)

## Output

All word clouds are saved in the `../output` directory.

## About the Data

The data comes from "WiT Studio Episodes Word Cloud Frequencies.csv" and contains words/phrases from WiT Studio episodes. The scripts filter the data to only include words marked with "y" in the "Keep ?" column and sizes words based on their frequency. 