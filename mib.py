
file_path = 'ADSL-LINE-MIB-V1SMI.my'
import json

mib_data = {}
current_object = None
append=False
description=""
with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("--"):
                continue
            #current_object=None
            # Look for object definitions
            if 'OBJECT-TYPE' in line:
                current_object = line.split()
                if len(current_object)>1:
                    #print(current_object[0])
                    current_object = current_object[0]
                    mib_data[current_object] = {}

            # Look for description
            if append==True:
                description=description+line.strip()
                if line[-1]=='"':
                    append=False
                    #print(description)

                    mib_data[current_object]['description'] = description
                    description=""
            if line.startswith('DESCRIPTION'):
                append=True

            # Look for syntax/type
            if line.startswith('SYNTAX'):
                data_type = line.split('SYNTAX')[-1].strip()
                if current_object:
                    mib_data[current_object]['data_type'] = data_type
                    

with open('badraout.json', 'w') as json_file:
        json.dump(mib_data, json_file, indent=4)