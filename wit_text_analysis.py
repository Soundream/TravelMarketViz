import os
import jieba
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
import seaborn as sns
from pathlib import Path
import re
from docx import Document  # Add support for Word documents

class TextAnalyzer:
    def __init__(self, input_dir):
        self.input_dir = input_dir
        
        # Basic Chinese stopwords
        self.stopwords = set({
            
        })
        # Basic English stopwords
        self.stopwords.update({
            'days', 'started', 'move', 'little', 'away',
            'travel', 'podcasts', 'people', 'thank', 'us', 'go', 'talk', 'today',
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", 
            "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 
            'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 
            'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those',
            'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
            'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with',
            'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
            'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
            'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
            'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
            'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've",
            'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn',
            "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn',
            "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn',
            "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn',
            "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
        })
        # Industry-specific stopwords
        self.stopwords.update({
            'web', 'years', 'said', 'says', 'will', 'new', 'also', 'one', 'two', 'may', 'now', 'use',
            'using', 'used', 'can', 'could', 'would', 'should', 'get', 'many', 'much',
            'year', 'month', 'day', 'time', 'way', 'week', 'need', 'make', 'see', 'look',
            'even', 'first', 'last', 'still', 'going', 'however', 'including', 'according',
            'inc', 'ltd', 'co', 'com', 'org', 'net', 'www'
        })

        # Filler words and expressions
        self.stopwords.update({
            'um', 'uh', 'ah', 'oh', 'yeah', 'yes', 'no', 'right', 'okay', 'ok',
            'like', 'sort', 'kind', 'lot', 'lots', 'thing', 'things', 'way', 'ways',
            'actually', 'basically', 'literally', 'really', 'stuff', 'mean', 'means',
            'know', 'think', 'thought', 'thinking', 'going', 'goes', 'went', 'gone',
            'come', 'comes', 'coming', 'came', 'get', 'gets', 'getting', 'got',
            'want', 'wants', 'wanting', 'wanted', 'look', 'looks', 'looking', 'looked',
            'well', 'good', 'great', 'nice', 'better', 'best', 'sure', 'guess',
            'maybe', 'perhaps', 'probably', 'obviously', 'course', 'etc',
            # Additional common words
            'able', 'back', 'take', 'say', 'something', 'early', 'next', 'across',
            # User-specified stopwords
            'different', 'always', 'point', 'build', 'work', 'change',
            # Additional stopwords
            'around', 'somebody', 'bit', 'quickly',
            # Special characters
            '...', '…'
        })

        # Names and related words
        self.stopwords.update({
            'timothy', 'tim', 'neil', 'dunne', 'ross', 'veitch', 'hoon', 'siew',
            'mr', 'mrs', 'ms', 'dr', 'prof', 'sir', 'madam', 'miss',
            'name', 'names', 'called', 'call', 'calls', 'calling'
        })
        
        # Initialize frequency counters
        self.word_freq = None
        self.bigram_freq = None
        self.trigram_freq = None
        
    def read_word_doc(self, file_path):
        """Read content from a Word document"""
        try:
            doc = Document(file_path)
            return ' '.join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            print(f"Error reading Word document {file_path}: {e}")
            return ""

    def read_files(self):
        """Read all text files and Word documents and combine their content"""
        all_text = []
        # Search for both txt and Word files
        found_files = list(Path(self.input_dir).rglob('*.txt')) + \
                     list(Path(self.input_dir).rglob('*.doc')) + \
                     list(Path(self.input_dir).rglob('*.docx'))
        
        if not found_files:
            raise FileNotFoundError(f"No .txt or Word files found in directory: {self.input_dir}")
            
        for file in found_files:
            try:
                if file.suffix.lower() in ['.doc', '.docx']:
                    text = self.read_word_doc(file)
                    if text:
                        all_text.append(text)
                        print(f"Successfully read Word document {file}")
                else:  # txt files
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            text = f.read()
                            all_text.append(text)
                            print(f"Successfully read {file}")
                    except UnicodeDecodeError:
                        try:
                            # Try alternative encoding
                            with open(file, 'r', encoding='gbk') as f:
                                text = f.read()
                                all_text.append(text)
                                print(f"Successfully read {file} with GBK encoding")
                        except Exception as e:
                            print(f"Failed to read {file} with both UTF-8 and GBK encodings")
                            
            except Exception as e:
                print(f"Error processing file {file}: {e}")
                continue
                
        if not all_text:
            raise ValueError(f"No valid text content found in {self.input_dir}")
            
        return ' '.join(all_text)

    def is_number(self, word):
        """Check if a string is purely numeric"""
        return word.replace('.', '').isdigit()

    def get_filtered_words(self, text):
        """Get filtered word list"""
        # Preprocess text to remove ellipsis
        text = re.sub(r'\.{3,}|…', ' ', text)
        
        # Use jieba for word segmentation
        words = list(jieba.cut(text))
        # Filter and return word list
        filtered = []
        for word in words:
            word = word.strip().lower()
            # For single words, exclude stopwords and pure numbers
            if word and word not in self.stopwords and len(word) > 1 and not self.is_number(word):
                filtered.append(word)
        return filtered

    def get_ngrams(self, words, n):
        """Generate n-gram sequences"""
        # For n-grams, don't filter numbers to keep combinations like "20 years"
        ngrams = []
        for i in range(len(words)-n+1):
            ngram = tuple(words[i:i+n])
            # Check if all words in n-gram are stopwords
            if not all(word in self.stopwords for word in ngram):
                ngrams.append(ngram)
        return ngrams

    def filter_redundant_unigrams(self):
        """Filter out words that mainly appear as part of n-grams"""
        if not self.word_freq:
            return
            
        # Set frequency similarity threshold (adjusted to be more strict)
        similarity_threshold = 0.95  # Increased threshold
        min_freq_threshold = 3  # Minimum frequency threshold to avoid filtering low-frequency words
        words_to_remove = set()
        
        # Check bigrams
        for bigram, bigram_freq in self.bigram_freq.items():
            # Only process word pairs that meet the threshold
            if bigram_freq < min_freq_threshold:
                continue
                
            word1, word2 = bigram
            # Check if these words always or almost always appear together
            if word1 in self.word_freq and word2 in self.word_freq:
                word1_freq = self.word_freq[word1]
                word2_freq = self.word_freq[word2]
                
                # If both words have very similar frequencies and close to bigram frequency
                if (abs(word1_freq - word2_freq) <= 2 and  # Word frequency difference not more than 2
                    min(word1_freq, word2_freq) >= bigram_freq * similarity_threshold):
                    # Check if these words mainly appear in this bigram
                    if (bigram_freq / word1_freq >= 0.8 and  # 80% appearances are in this bigram
                        bigram_freq / word2_freq >= 0.8):
                        words_to_remove.add(word1)
                        words_to_remove.add(word2)
        
        # Check trigrams
        for trigram, trigram_freq in self.trigram_freq.items():
            # Only process word groups that meet the threshold
            if trigram_freq < min_freq_threshold:
                continue
                
            word1, word2, word3 = trigram
            # Check if these three words always or almost always appear together
            if (word1 in self.word_freq and word2 in self.word_freq and 
                word3 in self.word_freq):
                word1_freq = self.word_freq[word1]
                word2_freq = self.word_freq[word2]
                word3_freq = self.word_freq[word3]
                
                # If all three words have very similar frequencies and close to trigram frequency
                if (max(abs(word1_freq - word2_freq), 
                       abs(word2_freq - word3_freq),
                       abs(word1_freq - word3_freq)) <= 2 and  # Word frequency difference not more than 2
                    min(word1_freq, word2_freq, word3_freq) >= trigram_freq * similarity_threshold):
                    # Check if these words mainly appear in this trigram
                    if (trigram_freq / word1_freq >= 0.8 and
                        trigram_freq / word2_freq >= 0.8 and
                        trigram_freq / word3_freq >= 0.8):
                        words_to_remove.add(word1)
                        words_to_remove.add(word2)
                        words_to_remove.add(word3)
        
        # Remove these words from word_freq
        for word in words_to_remove:
            if word in self.word_freq:
                del self.word_freq[word]
                
        print(f"Filtered {len(words_to_remove)} redundant words that mainly appear in n-grams")

    def analyze_text(self):
        """Analyze text content, including words, bigrams, and trigrams"""
        try:
            text = self.read_files()
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}")
            return Counter(), Counter(), Counter()
            
        # Get filtered word list
        filtered_words = self.get_filtered_words(text)
        
        if not filtered_words:
            print("Warning: No valid words found after filtering")
            return Counter(), Counter(), Counter()
            
        # Count word frequencies
        self.word_freq = Counter(filtered_words)
        
        # Count bigram frequencies
        self.bigram_freq = Counter(self.get_ngrams(filtered_words, 2))
        
        # Count trigram frequencies
        self.trigram_freq = Counter(self.get_ngrams(filtered_words, 3))
        
        # Filter out redundant words
        self.filter_redundant_unigrams()
        
        return self.word_freq, self.bigram_freq, self.trigram_freq

    def plot_top_words(self, top_n=20, ngram_type='unigram'):
        """Plot bar chart of top N frequent words/phrases"""
        if not self.word_freq:
            self.word_freq, self.bigram_freq, self.trigram_freq = self.analyze_text()
            
        # Select n-gram type to display
        if ngram_type == 'unigram':
            freq_data = self.word_freq
            title = 'Word Frequency Statistics (Top {})'.format(top_n)
            xlabel = 'Word'
        elif ngram_type == 'bigram':
            freq_data = self.bigram_freq
            title = 'Bigram Frequency Statistics (Top {})'.format(top_n)
            xlabel = 'Phrase'
        else:  # trigram
            freq_data = self.trigram_freq
            title = 'Trigram Frequency Statistics (Top {})'.format(top_n)
            xlabel = 'Phrase'
            
        if not freq_data:
            print(f"No data to plot for {ngram_type}")
            return
            
        # Get top N frequent words/phrases
        if ngram_type == 'unigram':
            top_items = pd.DataFrame(
                [(word, freq) for word, freq in freq_data.most_common(top_n)],
                columns=['Word', 'Frequency']
            )
        else:
            # For bigrams and trigrams, convert tuples to strings
            top_items = pd.DataFrame(
                [(' '.join(k), v) for k, v in freq_data.most_common(top_n)],
                columns=['Word', 'Frequency']
            )
        
        # Set chart style
        try:
            plt.style.use('seaborn')  # Updated style name
        except:
            print("Warning: Could not set seaborn style, using default style")
            
        plt.figure(figsize=(15, 8))
        
        # Create bar chart
        sns.barplot(data=top_items, x='Word', y='Frequency')
        plt.xticks(rotation=45, ha='right')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel('Frequency')
        plt.tight_layout()
        
        # Save chart
        output_file = f'word_frequency_{ngram_type}.png'
        plt.savefig(output_file)
        plt.close()
        print(f"Saved {ngram_type} plot to {output_file}")

    def generate_wordcloud(self):
        """Generate word cloud"""
        if not self.word_freq:
            self.word_freq, self.bigram_freq, self.trigram_freq = self.analyze_text()
            
        if not self.word_freq:
            print("No data to generate word cloud")
            return
            
        # Combine frequencies of words, bigrams, and trigrams with higher weights for multi-word phrases
        combined_freq = self.word_freq.copy()
        # Add bigrams with higher weight
        for words, freq in self.bigram_freq.items():
            combined_freq[' '.join(words)] = freq * 1.2
        # Add trigrams with higher weight
        for words, freq in self.trigram_freq.items():
            combined_freq[' '.join(words)] = freq * 1.5
            
        # Define possible font paths
        possible_fonts = [
            '/System/Library/Fonts/PingFang.ttc',  # macOS
            '/System/Library/Fonts/Arial Unicode.ttf',  # macOS
            '/Library/Fonts/Arial Unicode.ttf',  # macOS
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
            'C:\\Windows\\Fonts\\arial.ttf',  # Windows
            'arial'  # Default fallback
        ]
        
        # Find available font
        font_path = None
        for font in possible_fonts:
            try:
                if font == 'arial':
                    font_path = font
                    break
                if os.path.exists(font):
                    font_path = font
                    break
            except:
                continue
        
        try:
            # Create WordCloud object
            wordcloud = WordCloud(
                width=1200,
                height=800,
                background_color='white',
                font_path=font_path,
                max_words=100,
                collocations=False,
                prefer_horizontal=0.7
            )
            
            # Generate word cloud
            wordcloud.generate_from_frequencies(combined_freq)
            
            # Display word cloud
            plt.figure(figsize=(15, 10))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Word Cloud (Including Words, Bigrams, and Trigrams)')
            plt.tight_layout(pad=0)
            
            # Save word cloud
            plt.savefig('wordcloud.png')
            plt.close()
            
            print("Successfully generated word cloud with words, bigrams, and trigrams")
            
        except Exception as e:
            print(f"Error generating word cloud: {e}")
            print("Continuing with other visualizations...")

    def save_word_frequency(self, ngram_type='all'):
        """Save word frequency statistics to CSV file"""
        if not self.word_freq:
            self.word_freq, self.bigram_freq, self.trigram_freq = self.analyze_text()
            
        # Create a list containing all results
        all_results = []
        
        # Add word frequencies
        for word, freq in self.word_freq.most_common():
            all_results.append({
                'Type': 'Word',
                'Word/Phrase': word,
                'Frequency': freq
            })
            
        # Add bigram frequencies
        for word_pair, freq in self.bigram_freq.most_common():
            all_results.append({
                'Type': 'Bigram',
                'Word/Phrase': ' '.join(word_pair),
                'Frequency': freq
            })
            
        # Add trigram frequencies
        for word_triplet, freq in self.trigram_freq.most_common():
            all_results.append({
                'Type': 'Trigram',
                'Word/Phrase': ' '.join(word_triplet),
                'Frequency': freq
            })
            
        # Create DataFrame and sort by frequency
        df_all = pd.DataFrame(all_results)
        df_all = df_all.sort_values('Frequency', ascending=False)
        
        # Save to CSV file
        df_all.to_csv('word_frequency_all.csv', index=False, encoding='utf-8-sig')
        print("\nWord frequency statistics saved to word_frequency_all.csv")
        
        # Print some statistics
        print("\nWord Frequency Summary:")
        print(f"Total unique words: {len(self.word_freq)}")
        print(f"Total unique bigrams: {len(self.bigram_freq)}")
        print(f"Total unique trigrams: {len(self.trigram_freq)}")
        
        # Print top 20 most common words/phrases
        print("\nTop 20 most common words/phrases:")
        top_20 = df_all.head(20)
        for _, row in top_20.iterrows():
            print(f"{row['Type']} - {row['Word/Phrase']}: {row['Frequency']}")

    def save_sentences_for_top_keywords(self, top_n=20):
        """Save sentences for all keywords appearing in the top frequency list into a single CSV file
        
        Args:
            top_n (int): Number of top frequency words/phrases to process
        """
        # Prepare all keywords from word frequencies
        all_results = []
        
        # Add word frequencies
        for word, freq in self.word_freq.most_common(top_n):
            all_results.append({
                'Type': 'Word',
                'Word/Phrase': word,
                'Frequency': freq
            })
            
        # Add bigram frequencies
        for word_pair, freq in self.bigram_freq.most_common(top_n):
            all_results.append({
                'Type': 'Bigram',
                'Word/Phrase': ' '.join(word_pair),
                'Frequency': freq
            })
            
        # Add trigram frequencies
        for word_triplet, freq in self.trigram_freq.most_common(top_n):
            all_results.append({
                'Type': 'Trigram',
                'Word/Phrase': ' '.join(word_triplet),
                'Frequency': freq
            })
            
        # Sort by frequency and get unique keywords
        df_all = pd.DataFrame(all_results)
        df_all = df_all.sort_values('Frequency', ascending=False)
        
        print("\nSearching sentences for all top keywords...")
        # Process each keyword and collect all sentences
        all_sentences = []
        for _, row in df_all.iterrows():
            keyword = row['Word/Phrase']
            print(f"\nProcessing keyword: '{keyword}'")
            sentences = self.find_sentences_with_keyword(keyword)
            all_sentences.extend(sentences)
        
        # Save all sentences to a single CSV file
        if all_sentences:
            df_sentences = pd.DataFrame(all_sentences)
            df_sentences = df_sentences[['keyword', 'source_file', 'sentence']]  # Ensure column order
            output_filename = 'all_keyword_sentences.csv'
            df_sentences.to_csv(output_filename, index=False, encoding='utf-8-sig')
            print(f"\nAll sentences saved to {output_filename}")
            print(f"Total sentences found: {len(all_sentences)}")
        else:
            print("\nNo sentences found for any keywords")

    def plot_combined_frequencies(self, top_n=20):
        """Plot combined frequency statistics"""
        if not self.word_freq:
            self.word_freq, self.bigram_freq, self.trigram_freq = self.analyze_text()
            
        # Prepare data
        all_results = []
        
        # Add word frequencies
        for word, freq in self.word_freq.most_common(top_n):
            all_results.append({
                'Type': 'Word',
                'Word/Phrase': word,
                'Frequency': freq
            })
            
        # Add bigram frequencies
        for word_pair, freq in self.bigram_freq.most_common(top_n):
            all_results.append({
                'Type': 'Bigram',
                'Word/Phrase': ' '.join(word_pair),
                'Frequency': freq
            })
            
        # Add trigram frequencies
        for word_triplet, freq in self.trigram_freq.most_common(top_n):
            all_results.append({
                'Type': 'Trigram',
                'Word/Phrase': ' '.join(word_triplet),
                'Frequency': freq
            })
            
        # Create DataFrame and sort by frequency
        df_all = pd.DataFrame(all_results)
        df_all = df_all.sort_values('Frequency', ascending=False)
        
        # Set chart style
        try:
            plt.style.use('seaborn')  # Updated style name
        except:
            print("Warning: Could not set seaborn style, using default style")
            
        plt.figure(figsize=(15, 10))
        
        # Create bar chart
        sns.barplot(data=df_all.head(top_n), x='Word/Phrase', y='Frequency', hue='Type')
        plt.xticks(rotation=45, ha='right')
        plt.title(f'Word Frequency Statistics Top {top_n}')
        plt.xlabel('Word/Phrase')
        plt.ylabel('Frequency')
        plt.legend(title='Type')
        plt.tight_layout()
        
        # Save chart
        plt.savefig('word_frequency_combined.png')
        plt.close()
        print(f"Saved combined frequency plot to word_frequency_combined.png")
        
        # Generate sentence files for all keywords
        self.save_sentences_for_top_keywords(top_n)

    def find_sentences_with_keyword(self, keyword, text=None):
        """Find sentences containing keywords
        
        Args:
            keyword (str): Keyword or phrase to search for
            text (str, optional): Text to search in. If None, will read files again.
            
        Returns:
            list: List of sentences containing the keyword, each element is a dictionary with sentence content and file name
        """
        found_sentences = []
        
        # Iterate through all txt files in directory
        for file_path in Path(self.input_dir).rglob('*.txt'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='gbk') as f:
                        text = f.read()
                except Exception as e:
                    print(f"Cannot read file {file_path}: {e}")
                    continue

            # Convert keyword to lowercase for case-insensitive search
            keyword = keyword.lower()
            
            # Use regex to split sentences
            # This pattern splits at periods, question marks, exclamation marks, considering spaces after them
            sentences = re.split(r'[.!?]+\s*', text)
            
            for sentence in sentences:
                # Clean and normalize sentence
                cleaned_sentence = sentence.strip()
                if not cleaned_sentence:  # Skip empty sentences
                    continue
                    
                # Remove extra whitespace and newlines
                cleaned_sentence = re.sub(r'\s+', ' ', cleaned_sentence)
                
                # If sentence is longer than 150 characters, take context around keyword
                if len(cleaned_sentence) > 150:
                    # Find keyword position
                    keyword_pos = cleaned_sentence.lower().find(keyword)
                    if keyword_pos != -1:
                        # Take 50 characters before and after keyword
                        start = max(0, keyword_pos - 50)
                        end = min(len(cleaned_sentence), keyword_pos + len(keyword) + 50)
                        
                        # Adjust start position to word beginning
                        while start > 0 and cleaned_sentence[start - 1].isalnum():
                            start -= 1
                            
                        # Adjust end position to word ending
                        while end < len(cleaned_sentence) and cleaned_sentence[end - 1].isalnum():
                            end += 1
                            
                        cleaned_sentence = ('...' if start > 0 else '') + \
                                        cleaned_sentence[start:end] + \
                                        ('...' if end < len(cleaned_sentence) else '')
                
                # Case-insensitive keyword check
                if keyword in cleaned_sentence.lower():
                    found_sentences.append({
                        'keyword': keyword,
                        'source_file': file_path.name,
                        'sentence': cleaned_sentence
                    })
        
        return found_sentences

    def save_keyword_sentences(self, keyword):
        """Save sentences containing keywords to CSV file
        
        Args:
            keyword (str): Keyword or phrase to search for
        """
        # Get sentences containing keyword
        sentences = self.find_sentences_with_keyword(keyword)
        
        if not sentences:
            print(f"\nNo sentences found containing keyword '{keyword}'")
            return
        
        # Create DataFrame and specify column order
        df = pd.DataFrame(sentences)
        df = df[['keyword', 'source_file', 'sentence']]
        
        # Save to CSV file
        output_filename = f'sentences_with_{keyword.replace(" ", "_")}.csv'
        df.to_csv(output_filename, index=False, encoding='utf-8-sig')
        print(f"\nSentences containing keyword '{keyword}' saved to {output_filename}")
        print(f"Found {len(sentences)} sentences containing this keyword")

def main():
    try:
        # Use correct folder path
        input_dir = input("Enter the path to the text files folder (press Enter for default path): ").strip()
        if not input_dir:
            input_dir = "05.project-word-swarm/WiT Studio Episodes"  # Default path
            
        analyzer = TextAnalyzer(input_dir)
        
        # Ask if want to search for specific keyword
        keyword = input("\nEnter keyword or phrase to search (press Enter to skip): ").strip()
        if keyword:
            print(f"\nSearching for sentences containing '{keyword}'...")
            analyzer.save_keyword_sentences(keyword)
        
        # Analyze text
        print("\nAnalyzing text...")
        word_freq, bigram_freq, trigram_freq = analyzer.analyze_text()
        
        if not word_freq and not bigram_freq and not trigram_freq:
            print("No valid text data found. Please check input directory and file contents.")
            return
        
        # Save word frequency statistics
        print("\nSaving word frequency statistics...")
        analyzer.save_word_frequency()
        
        # Generate combined frequency plot and sentence files for all keywords
        print("\nGenerating frequency plot and searching sentences for all keywords...")
        analyzer.plot_combined_frequencies()
        
        # Generate word cloud
        print("\nGenerating word cloud...")
        analyzer.generate_wordcloud()
        
        print("\nAnalysis complete! Please check the following files:")
        if keyword:
            print(f"- sentences_with_{keyword.replace(' ', '_')}.csv (Sentences containing user-specified keyword)")
        print("- word_frequency_all.csv (Word frequency statistics)")
        print("- word_frequency_combined.png (Frequency plot)")
        print("- wordcloud.png (Word cloud)")
        print("- all_keyword_sentences.csv (Sentences for all top keywords)")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    main() 