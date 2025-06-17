import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os
import numpy as np
from collections import Counter

# Set output directory
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)

# Read the CSV file
df = pd.read_csv("WiT Studio Episodes Word Cloud Frequencies.csv", header=0)

# Show the actual column names for debugging
print("Actual column names in CSV:", df.columns.tolist())

# Filter for rows with "y" in the "Keep ?" column - note the space at the end of the column name
filtered_df = df[df["Keep ? "] == "y"]

# Create a dictionary of word frequencies
word_freq = {}
for _, row in filtered_df.iterrows():
    word = row["Word/Phrase"]
    freq = row["Frequency"]
    if pd.notna(word) and pd.notna(freq):
        word_freq[word] = int(freq)

# Custom color mapping for specific words with sophisticated colors
# Define category to color mapping using elegant color palette
category_colors = {
    "red": "#E63946",        # Sophisticated red
    "blue": "#457B9D",       # Sophisticated blue
    "green": "#2A9D8F",      # Sophisticated green
    "cyan": "#48CAE4",       # Sophisticated cyan
    "magenta": "#D90429",    # Sophisticated magenta
    "orange": "#FB8500",     # Sophisticated orange
    "purple": "#7209B7",     # Sophisticated purple
    "gray": "#6C757D"        # Default gray
}

# Category descriptions in English
category_names = {
    "red": "Travel Companies",
    "blue": "Geographic Locations",
    "green": "Technology Terms",
    "cyan": "Time/Trends",
    "magenta": "Travel Key Brands",
    "orange": "Industry Terms",
    "purple": "Customer/Business"
}

# Custom color mapping for specific words
color_mapping = {
  "ai": "green",
  "asia": "blue",
  "wit": "red",
  "booking": "red",
  "china": "blue",
  "expedia": "red",
  "content": "purple",
  "covid": "cyan",
  "otas": "orange",
  "experiences": "purple",
  "chinese": "blue",
  "hotel": "orange",
  "customers": "purple",
  "indonesia": "blue",
  "social": "purple",
  "singapore": "blue",
  "japan": "blue",
  "southeast": "blue",
  "destinations": "orange",
  "korean": "blue",
  "partners": "orange",
  "needs": "purple",
  "southeast asia": "blue",
  "price": "purple",
  "social media": "purple",
  "asian": "blue",
  "corporate": "purple",
  "india": "blue",
  "community": "magenta",
  "brands": "purple",
  "brand": "purple",
  "traveloka": "red",
  "airlines": "orange",
  "consumers": "purple",
  "american": "blue",
  "korea": "blue",
  "infrastructure": "orange",
  "pioneers": "magenta",
  "agoda": "red",
  "hong kong": "blue",
  "gen": "magenta",
  "activities": "orange",
  "20th": "cyan",
  "meta": "green",
  "mirror rise": "cyan",
  "history mirror": "cyan",
  "rise fall": "cyan",
  "以古为鉴": "cyan",
  "ceo": "magenta",
  "crisis": "cyan",
  "offline": "cyan",
  "priceline": "red",
  "accommodation": "orange",
  "investment": "purple",
  "europe": "blue",
  "english": "blue",
  "middle east": "blue",
  "trend": "cyan",
  "america": "blue",
  "marketing": "purple",
  "airline": "orange",
  "pricing": "purple",
  "kids": "magenta",
  "revenue": "purple",
  "thailand": "blue",
  "personalized": "purple",
  "relationships": "purple",
  "pandemic": "cyan",
  "website": "purple",
  "wego": "red",
  "economy": "cyan",
  "banyan": "red",
  "mainland china": "blue",
  "carriers": "orange",
  "transactions": "orange",
  "users": "purple",
  "japanese": "blue",
  "ctrip": "red",
  "indonesians": "blue",
  "viator": "red",
  "civilization": "blue",
  "tensions": "blue",
  "financial crisis": "cyan",
  "government": "blue",
  "travelocity": "red",
  "vision": "cyan",
  "bangkok": "blue",
  "partnerships": "orange",
  "premium": "purple",
  "asia pacific": "blue",
  "entrepreneur": "magenta",
  "gds": "orange",
  "deepseek": "red",
  "instagram": "red",
  "disrupt": "green",
  "excitement": "cyan",
  "hybrid": "green",
  "wit seoul": "red",
  "seoul": "blue",
  "reviews": "purple",
  "funnel": "purple",
  "commerce": "purple",
  "competitors": "purple",
  "desert": "magenta",
  "phuket": "blue",
  "tripadvisor": "red",
  "christmas eve": "magenta",
  "joint venture": "orange",
  "booking holdings": "red",
  "asian century": "blue",
  "itinerary": "orange",
  "planning": "orange",
  "science": "green",
  "humans": "magenta",
  "research": "purple",
  "orbitz": "red",
  "competitive": "purple",
  "personalization": "purple",
  "headquarters": "purple",
  "swim": "magenta",
  "competition": "purple",
  "likes": "purple",
  "hoteliers": "orange",
  "london": "blue",
  "bubble": "cyan",
  "meaningful": "purple",
  "experienced": "magenta",
  "airasia": "red",
  "tokyo": "blue",
  "bali": "blue",
  "fast forward": "cyan",
  "restaurant": "orange",
  "american airlines": "red",
  "ups downs": "cyan",
  "stay gentle": "magenta",
  "brand karma": "red",
  "americana": "blue",
  "philippines": "blue",
  "karma": "magenta",
  "firewalls": "green",
  "property": "orange",
  "location": "orange",
  "engineering": "green",
  "pivoted": "green",
  "talent": "magenta",
  "powerful": "green",
  "australia": "blue",
  "suppliers": "orange",
  "2000s": "cyan",
  "stronger": "cyan",
  "ownership": "orange",
  "weekend": "magenta",
  "philosophy": "magenta",
  "knowledge": "magenta",
  "trips": "orange",
  "thai": "blue",
  "transport": "orange",
  "elon": "green",
  "public": "purple",
  "specialist": "magenta",
  "generations": "magenta",
  "optimistic": "cyan",
  "mantra": "magenta",
  "discover": "purple",
  "vice president": "magenta",
  "1%": "purple",
  "consumer behavior": "purple",
  "super apps": "green",
  "credit card": "purple",
  "flights hotels": "orange",
  "barry diller": "magenta",
  "search engine": "purple",
  "meaning life": "magenta",
  "east asia": "blue",
  "accessible indonesians": "blue",
  "remove friction": "purple",
  "contact center": "purple",
  "predict": "purple",
  "opening": "cyan",
  "normal": "cyan",
  "trends": "cyan",
  "penetration": "purple",
  "entrepreneurial": "magenta",
  "planes": "orange",
  "pivot": "green",
  "diversified": "cyan",
  "pivoting": "green",
  "malaysia": "blue",
  "coding": "green",
  "intelligence": "green",
  "expensive": "purple",
  "complicated": "purple",
  "amazon": "red",
  "metasearch": "green",
  "near death": "cyan",
  "capital markets": "cyan",
  "untold story": "magenta",
  "cost carrier": "orange",
  "annoyed optimist": "magenta",
  "booking engine": "orange",
  "cranky optimist": "magenta",
  "chinese government": "blue",
  "inbound china": "blue",
  "managing director": "magenta",
  "dot bust": "cyan",
  "expedia priceline": "red",
  "american players": "blue",
  "cowboy stories": "magenta",
  "dynamic pricing": "purple",
  "tours activities": "orange",
  "meta ota": "green",
  "tourism boards": "orange",
  "defining moments": "cyan",
  "bank transfer": "purple",
  "niche communities": "magenta",
  "startup story": "green",
  "wit helped": "red",
  "tiktok": "red",
  "makemytrip": "red",
  "geopolitical": "blue",
  "generation fails": "magenta",
  "china india": "blue",
  "brad pitt": "magenta",
  "meta search": "green",
  "eiffel tower": "blue",
  "science fiction": "green",
  "mixed reality": "green",
  "21st century": "cyan",
  "otas booking": "red",
  "made booking": "orange",
  "expedia asia": "red",
  "india china": "blue",
  "artificial intelligence": "green",
  "price premium": "purple",
  "google less": "red",
  "tech startups": "green",
  "visit places": "orange",
  "expand internationally": "orange",
  "asia europe": "blue",
  "llm model": "green",
  "grow faster": "cyan",
  "ceo founder": "magenta",
  "orbitz travelocity": "red",
  "travelocity expedia": "red",
  "accommodation providers": "orange",
  "yahoo japan": "red",
  "rocket booster": "green",
  "booking tools": "orange",
  "relationships critical": "purple",
  "lower cost": "cyan",
  "protect communities": "magenta",
  "korean startups": "blue",
  "southeast asian": "blue",
  "inbound travelers": "orange",
  "expedia london": "red",
  "post covid": "cyan",
  "kayak": "red",
  "flying cars": "green",
  "pivot meta": "green",
  "gds systems": "orange",
  "content marketing": "purple",
  "demand partners": "orange",
  "ota model": "orange",
  "evolution otas": "orange",
  "road ahead": "cyan",
  "center stage": "cyan",
  "pricing optimization": "purple",
  "optimization guest": "purple",
  "guest personalization": "purple",
  "hotels investing": "orange",
  "loyalty strategies": "purple",
  "accelerated covid": "cyan",
  "hospitality distribution": "orange",
  "shift towards": "cyan",
  "direct indirect": "orange",
  "indirect distribution": "orange",
  "travelers directly": "orange",
  "wego singapore": "red",
  "malaysia indonesia": "blue",
  "speed rail": "orange",
  "japan original": "blue",
  "los angeles": "blue",
  "hospitality tech": "orange",
  "asia southeast": "blue",
  "western civilization": "blue",
  "western values": "blue",
  "talking climate": "cyan",
  "david bowie": "magenta",
  "skyscanner": "red",
  "pivoting model initially": "green",
  "geographically pivoting model": "green",
  "pivoting geographically pivoting": "green",
  "pretty pivoting geographically": "green",
  "pivoted meta ota": "green",
  "traveloka pivoted meta": "green",
  "imagine the future": "cyan",
  "travel and technology": "green",
  "rise and fall": "cyan",
  "future of travel": "cyan",
  "low cost carrier": "orange",
  "global financial crisis": "cyan"
}

# Count words and frequencies per category
category_counts = Counter()
category_frequencies = Counter()
for word, freq in word_freq.items():
    word_lower = word.lower()
    if word_lower in color_mapping:
        category = color_mapping[word_lower]
        category_counts[category] += 1
        category_frequencies[category] += freq

# Function to assign colors to words based on the mapping with sophisticated colors
def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    # Convert word to lowercase for case insensitive matching
    word_lower = word.lower()
    
    # Get the category (red, blue, etc.) based on the word
    category = color_mapping.get(word_lower, "gray")
    
    # Return the sophisticated color for that category
    return category_colors.get(category, category_colors["gray"])

# Generate the word cloud with custom coloring
wordcloud = WordCloud(
    width=1600, 
    height=900,
    background_color="white",
    max_words=200,
    prefer_horizontal=0.9,
    scale=3,  # Higher resolution
    color_func=color_func  # Use our custom color function instead of colormap
).generate_from_frequencies(word_freq)

# Create the combined visualization with adjusted layout
plt.figure(figsize=(22, 18))

# Make the wordcloud larger by adjusting the subplot parameters
plt.subplot(2, 1, 1)
plt.subplots_adjust(hspace=0.3)  # Increase space between subplots
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.title("WiT Studio Episodes Word Cloud", fontsize=24, pad=20)

# Sort categories by frequency
sorted_categories = sorted(category_frequencies.items(), key=lambda x: x[1], reverse=True)
categories = [category_names.get(cat, cat) for cat, _ in sorted_categories]
frequencies = [freq for _, freq in sorted_categories]

# Plot the category distribution with proper descending order (highest at top)
plt.subplot(2, 1, 2)

# Matplotlib plots horizontal bars from bottom to top, so we need to reverse the lists
# to have highest frequency at the top
reversed_categories = categories[::-1]
reversed_frequencies = frequencies[::-1]
reversed_category_keys = [cat for cat, _ in sorted_categories][::-1]
reversed_colors = [category_colors.get(cat, "#6C757D") for cat, _ in sorted_categories][::-1]

bars = plt.barh(reversed_categories, reversed_frequencies, color=reversed_colors)

# Add word count as annotations (properly matching the category keys)
for i, category_key in enumerate(reversed_category_keys):
    word_count = category_counts[category_key]
    plt.text(reversed_frequencies[i] + max(frequencies) * 0.02, i, 
             f"{word_count} words", va='center', fontsize=12)

plt.xlabel('Total Frequency', fontsize=14)
plt.title('Word Category Distribution (Highest at Top)', fontsize=20, pad=20)
plt.tight_layout(pad=5)

# Save the combined visualization
output_file = os.path.join(output_dir, "wit_wordcloud_with_categories.png")
plt.savefig(output_file, bbox_inches='tight', dpi=300)
print(f"Word cloud with categories saved to {output_file}")

# Save the original wordcloud separately at full size
plt.figure(figsize=(16, 9), facecolor='white')
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.tight_layout(pad=0)

# Save the word cloud
output_file = os.path.join(output_dir, "wit_wordcloud.png")
plt.savefig(output_file, facecolor='white', bbox_inches='tight', dpi=300)
print(f"Word cloud saved to {output_file}")

# Display statistics
print(f"Total words in original dataset: {len(df)}")
print(f"Words kept for visualization: {len(filtered_df)}")
print(f"Words in frequency dictionary: {len(word_freq)}")
print(f"Top 20 most frequent words:")
top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
for word, freq in top_words:
    print(f"  {word}: {freq}")

# Display category statistics
print(f"\nCategory distribution:")
for cat, count in category_counts.most_common():
    print(f"  {category_names.get(cat, cat)}: {count} words, total frequency: {category_frequencies[cat]}") 