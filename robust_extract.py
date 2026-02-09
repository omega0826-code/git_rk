import pandas as pd
import os
import sys

def robust_extract():
    source_path = r'd:\git_rk\data\seoul hospital\HIRA_강남언니_결합_최종.csv'
    output_dir = r'd:\git_rk\data\seoul hospital'
    output_path = os.path.join(output_dir, 'seoul_extraction.csv')
    
    print(f"Starting extraction from: {source_path}")
    
    # Define allowed hospital types
    allowed_types = ["의원", "병원", "종합병원", "상급종합병원", "상급종합"]
    
    # Try different encodings
    encodings = ['utf-8', 'cp949', 'euc-kr']
    df = None
    
    for enc in encodings:
        try:
            # First, read just the header to get column names
            header_df = pd.read_csv(source_path, nrows=0, encoding=enc)
            print(f"Successfully read header with {enc} encoding.")
            
            # Read in chunks to avoid memory issues and provide progress
            chunk_size = 5000
            chunks = pd.read_csv(source_path, chunksize=chunk_size, encoding=enc)
            
            filtered_chunks = []
            total_processed = 0
            
            for i, chunk in enumerate(chunks):
                total_processed += len(chunk)
                print(f"Processing chunk {i+1} (Total processed: {total_processed})...")
                
                # Filter by hospital type
                mask_type = chunk['종별코드명'].isin(allowed_types)
                
                # Filter by keyword "피부" in any column (or specific ones if known)
                # To be thorough, we check all columns for the keyword
                mask_subject = chunk.astype(str).apply(lambda row: row.str.contains('피부').any(), axis=1)
                
                filtered_chunk = chunk[mask_type & mask_subject]
                filtered_chunks.append(filtered_chunk)
                
                print(f"Found {len(filtered_chunk)} matches in this chunk.")
            
            if filtered_chunks:
                final_df = pd.concat(filtered_chunks)
                print(f"Extraction complete. Total matches: {len(final_df)}")
                
                # Save results
                final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
                print(f"Results saved to: {output_path}")
                return True
            else:
                print("No matching records found.")
                return False
                
        except (UnicodeDecodeError, pd.errors.ParserError):
            print(f"Failed with {enc} encoding. Trying next...")
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            break
            
    return False

if __name__ == "__main__":
    success = robust_extract()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
