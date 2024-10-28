import logging
from pysnmp.smi import builder, view
from pysmi.reader.localfile import FileReader
from pysmi.writer.pyfile import PyFileWriter
from pysmi.parser.smi import SmiV2Parser
from pysmi.compiler import MibCompiler
from pysmi.codegen.pysnmp import PySnmpCodeGen

# Configure logging for DEBUG level
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# initialize the directory
mib_directory = './mibs'

# Create MIB builder
mibBuilder = builder.MibBuilder()
mibBuilder.set_mib_sources(
    builder.DirMibSource('myenv/lib/python3.12/site-packages/pysnmp/smi/mibs'),  # Default location first
    builder.DirMibSource('mibs')
)
mibBuilder.loadTexts = True

#Initialize MIB compiler for compilation
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

# Get and log all MIB symbols for IF-MIB
mibSymbols = mibBuilder.mibSymbols
for modName, modSymbols in mibSymbols.items():
    #   if modName == "IF-MIB":  # Filter for IF-MIB symbols only
        logging.info(f'MIB Module: {modName}')
        for symName, sym in modSymbols.items():
            # Access other attributes as needed
            if hasattr(sym, 'name'):
                oid = sym.getName()
                print(f"OID: {'.'.join(map(str, oid))}")
            
            # if hasattr(sym,'getLabel')and callable(sym.getLabel):
            #     try:
            #         label=sym.getLabel()
            #         print(f"Device Name: {sym.getLabel()}")
            #     except Exception as e:
            #          print("Error getting Device name.")

            if hasattr(sym, 'getSyntax') and callable(getattr(sym, 'getSyntax', None)):
                try:
                    syntax = sym.getSyntax()
                    # list=[]
                    # list.append(syntax)
                    # print(list)
                    print(f"Type of OID: {syntax.__class__.__name__}")
                except Exception as e:
                    print(f"Error getting OID type: {e}")


            # if hasattr(sym, 'getDescription') and callable(sym.getDescription):
            #     try:
            #         description = sym.getDescription()
            #         print(f"Description: {description}")
            #     except Exception as e:
            #         print(f"Error getting description for: {e}")
            # else:
            #     print(f"does not have a valid getDescription method.")
                