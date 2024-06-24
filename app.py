import os
import shutil

from src.service.process import IProcess
from src.service.process_html import ProcessHtml
from src.service.process_xml import ProcessXML


def process_xml_files(process_object: IProcess, input_xml_folder, output_html_folder, input_type, out_type):
    # Ensure the output folder exists
    os.makedirs(output_html_folder, exist_ok=True)

    # Iterate over items in the current input folder
    for item in os.listdir(input_xml_folder):
        input_path = os.path.join(input_xml_folder, item)
        output_path = os.path.join(output_html_folder, item)

        if os.path.isdir(input_path):
            # If the item is a directory, create a corresponding directory in the output folder
            os.makedirs(output_path, exist_ok=True)
            # Recursively process the subdirectory
            process_xml_files(process_object, input_path, output_path, input_type, out_type)
        elif item.endswith(input_type):
            # If the item is an XML file, process it
            process_object.process_file(input_path, output_path.replace(input_type, out_type))
        else:
            # If the item is not an XML file, copy it to the output folder
            shutil.copy2(input_path, output_path)


INPUT_FOLDER = 'input'
OUTPUT_FOLDER = 'output'
INPUT_TYPE = '.html'  #.xml
OUTPUT_TYPE = '.json'  #.html
if __name__ == '__main__':
    process = ProcessHtml()  # uncomment if you want to process html for legislature
    # process = ProcessXML()  # uncomment if you want to process xml for case
    process_xml_files(process, INPUT_FOLDER, OUTPUT_FOLDER, INPUT_TYPE, OUTPUT_TYPE)
