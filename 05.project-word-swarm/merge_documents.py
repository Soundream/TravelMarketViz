import os
import docx
from pathlib import Path

def extract_text_from_docx(docx_path):
    """Extract text from a .docx file"""
    try:
        doc = docx.Document(docx_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error processing {docx_path}: {str(e)}")
        return ""

def extract_text_from_txt(txt_path):
    """Extract text from a .txt file"""
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error processing {txt_path}: {str(e)}")
        return ""

def merge_documents(input_dir, output_file):
    """Merge all .doc, .docx and .txt files from input directory into one file"""
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize list to store all texts
    all_texts = []
    
    # Walk through the directory
    for root, _, files in os.walk(input_dir):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Process based on file extension
            if file.lower().endswith('.docx'):
                print(f"Processing {file}...")
                text = extract_text_from_docx(file_path)
                if text:
                    all_texts.append(f"\n{'='*50}\nFile: {file}\n{'='*50}\n")
                    all_texts.append(text)
            
            elif file.lower().endswith('.txt'):
                print(f"Processing {file}...")
                text = extract_text_from_txt(file_path)
                if text:
                    all_texts.append(f"\n{'='*50}\nFile: {file}\n{'='*50}\n")
                    all_texts.append(text)

    # Write all texts to the output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_texts))
        print(f"\nSuccessfully merged all documents into {output_file}")
    except Exception as e:
        print(f"Error writing to output file: {str(e)}")

if __name__ == "__main__":
    # Define input and output paths
    input_directory = "WiT Studio Episodes"
    output_file = "output/merged_documents.txt"
    
    # Run the merge operation
    merge_documents(input_directory, output_file) 