import pandas as pd
import random
import string
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(message)s',
                   handlers=[
                       logging.FileHandler('matching.log'),
                       logging.StreamHandler()
                   ])

class UniqueCodeGenerator:
    def __init__(self):
        self.used_codes = set()
    
    def generate_unique_code(self):
        """Generate a unique 2-letter code that hasn't been used."""
        while True:
            # Generate a random 2-letter code using uppercase letters
            code = ''.join(random.choices(string.ascii_uppercase, k=2))
            if code not in self.used_codes:
                self.used_codes.add(code)
                return code

def main():
    # Initialize code generator
    code_generator = UniqueCodeGenerator()
    
    # Read the CSV files
    mena_df = pd.read_csv('mena_with_itat_new.csv')
    usa_df = pd.read_csv('usa_with_itat_new.csv')
    
    def replace_unresolved(code):
        if code == 'unresolved':
            # Generate a new unique code for each unresolved entry
            return code_generator.generate_unique_code()
        return code
    
    # Replace unresolved codes
    mena_df['iata_code'] = mena_df['iata_code'].apply(replace_unresolved)
    usa_df['iata_code'] = usa_df['iata_code'].apply(replace_unresolved)
    
    # Save results
    mena_df.to_csv('mena_with_iata_new.csv', index=False)
    usa_df.to_csv('usa_with_iata_new.csv', index=False)
    
    # Print summary
    logging.info("\nProcessing Summary:")
    logging.info(f"Total random codes generated: {len(code_generator.used_codes)}")
    logging.info("\nGenerated codes:")
    for code in sorted(code_generator.used_codes):
        logging.info(f"Generated code: {code}")

if __name__ == "__main__":
    main()
