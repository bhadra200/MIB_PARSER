import json
import re

def read_mib_file(file_path):
    try:
        with open(file_path, 'r') as mib_file:
            contents = mib_file.readlines()  # Read the file line by line

        mib_data = []  # List to hold parsed MIB data

        # Define regex patterns to capture OID, description, syntax, and access
        oid_pattern = re.compile(r'^\s*([\w-]+)\s+OBJECT-TYPE\s*')
        desc_pattern = re.compile(r'^\s*DESCRIPTION\s*::=\s*"(.+?)"')
        syntax_pattern = re.compile(r'^\s*SYNTAX\s*::=\s*(.+)')
        access_pattern = re.compile(r'^\s*ACCESS\s*::=\s*(.+)')

        current_oid = None
        current_description = None
        current_syntax = None
        current_access = None

        for line in contents:
            oid_match = oid_pattern.match(line)
            desc_match = desc_pattern.search(line)
            syntax_match = syntax_pattern.search(line)
            access_match = access_pattern.search(line)

            if oid_match:
                if current_oid:  # If we were already on an OID, save the previous one
                    mib_data.append({
                        'oid': current_oid,
                        'description': current_description,
                        'syntax': current_syntax,
                        'access': current_access
                    })
                
                current_oid = oid_match.group(1)
                current_description = None
                current_syntax = None
                current_access = None
            
            elif desc_match and current_oid:
                current_description = desc_match.group(1)
            elif syntax_match and current_oid:
                current_syntax = syntax_match.group(1).strip()
            elif access_match and current_oid:
                current_access = access_match.group(1).strip()

        # Save the last parsed OID
        if current_oid:
            mib_data.append({
                'oid': current_oid,
                'description': current_description,
                'syntax': current_syntax,
                'access': current_access
            })

        # Store the parsed MIB data as JSON
        json_file_path = file_path.replace('.my', '.json')  # Change extension to .json
        with open(json_file_path, 'w') as json_file:
            json.dump(mib_data, json_file, indent=4)  # Save JSON with indentation

        print(f"Parsed MIB data stored in {json_file_path}")

    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
    except IOError:
        print(f"Error: An error occurred while reading the file at {file_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Specify the path to your MIB file
mib_file_path = r"D:\MIB Parser\ADSL_LINE_MIB_V1SMI.my"  # Adjust this path as necessary
read_mib_file(mib_file_path)
