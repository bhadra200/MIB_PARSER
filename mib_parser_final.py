import logging
import mysql.connector
from mysql.connector import Error
from pysnmp.smi import builder, view
from pysmi.reader.localfile import FileReader
from pysmi.writer.pyfile import PyFileWriter
from pysmi.parser.smi import SmiV2Parser
from pysmi.compiler import MibCompiler
from pysmi.codegen.pysnmp import PySnmpCodeGen

# Configure logging for DEBUG level
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the directory for MIB files
mib_directory = './mibs'

# Create MIB builder
mibBuilder = builder.MibBuilder()
mibBuilder.set_mib_sources(
    builder.DirMibSource('myenv/lib/python3.12/site-packages/pysnmp/smi/mibs'),  # Default location first
    builder.DirMibSource(mib_directory)
)
mibBuilder.loadTexts = True

# Initialize MIB compiler for compilation
mibCompiler = MibCompiler(
    SmiV2Parser(),
    PySnmpCodeGen(),
    PyFileWriter(mib_directory)
)

# Add file reader for MIB files and enable debug logging for compiler actions
mibCompiler.add_sources(FileReader(mib_directory))

# Compile the IF-MIB file without forcing rebuild
try:
    compiled_modules = mibCompiler.compile('IF-MIB', rebuild=False)
    logging.info(f"Compiled modules: {compiled_modules}")
except Exception as e:
    logging.error(f"Error compiling MIB file: {e}")

mibBuilder.load_modules("IF-MIB")

# Create MIB view controller
mibViewController = view.MibViewController(mibBuilder)

# MySQL connection details
def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

# Function to create a table if it doesn't exist
def create_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS oid_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        oid VARCHAR(255) NOT NULL,
        oid_type VARCHAR(255) NOT NULL
    );
    """
    execute_query(connection, create_table_query)

# Function to execute a query
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Exception as e:
        print(f"The error '{e}' occurred")

# Function to insert OID and its type into the database
def insert_oid_data(connection, oid, oid_type):
    insert_query = f"""
    INSERT INTO oid_data (oid, oid_type)
    VALUES ('{oid}', '{oid_type}');
    """
    execute_query(connection, insert_query)

# Connect to MySQL database
connection = create_connection("localhost", "root", "root", "mib_database")
create_table(connection)

# Get and log all MIB symbols for IF-MIB
mibSymbols = mibBuilder.mibSymbols
for modName, modSymbols in mibSymbols.items():
    logging.info(f'MIB Module: {modName}')
    for symName, sym in modSymbols.items():
        if hasattr(sym, 'name'):
            oid = sym.getName()
            oid_str = '.'.join(map(str, oid))
            # print(f"OID: {oid_str}")

            if hasattr(sym, 'getSyntax') and callable(getattr(sym, 'getSyntax', None)):
                try:
                    syntax = sym.getSyntax()
                    oid_type = syntax.__class__.__name__
                    # print(f"Type of OID: {oid_type}")
                    
                    # Insert into MySQL database
                    insert_oid_data(connection, oid_str, oid_type)
                except Exception as e:
                    print(f"Error getting OID type: {e}")

# Close the MySQL connection
if connection:
    connection.close()
    print("The connection is closed.")
