import os
import shutil
import pandas as pd
import argparse

def organize_files(csv_file, source_directory, destination_directory):
    """
    Organizes files from a common directory into category folders based on a CSV file.

    Args:
        csv_file (str): Path to the CSV file containing 'category' and 'filename' columns.
        source_directory (str): Directory where all files are located.
        destination_directory (str): Directory where files will be organized into category folders.
    """
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Iterate through each row in the CSV
    for _, row in df.iterrows():
        category = row['category']
        filename = row['filename']
        
        # Define paths
        source_file = os.path.join(source_directory, filename)
        category_folder = os.path.join(destination_directory, category)
        
        # Ensure the category folder exists
        os.makedirs(category_folder, exist_ok=True)
        
        # Move the file
        if os.path.exists(source_file):
            shutil.copy(source_file, category_folder)  # Use shutil.move to move instead of copy
            print(f"Copied {filename} to {category_folder}")
        else:
            print(f"File not found: {source_file}")

    print("File organization complete.")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Organize files into category folders based on a CSV file.")
    parser.add_argument("--csv_file", help="Path to the CSV file containing 'category' and 'filename' columns.")
    parser.add_argument("--source_directory", help="Directory where all files are located.")
    parser.add_argument("--destination_directory", help="Directory where files will be organized into category folders.")
    args = parser.parse_args()

    # Call the function with parsed arguments
    organize_files(args.csv_file, args.source_directory, args.destination_directory)
