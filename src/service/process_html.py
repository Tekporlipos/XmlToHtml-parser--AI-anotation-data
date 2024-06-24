import locale
import math
import re
from datetime import datetime

from src.parser.json_template import Statute
from src.service.process import IProcess
from bs4 import BeautifulSoup


def get_list_sections(soup):
    sections = ''
    leg_p1_containers = soup.find_all(class_=re.compile(r'^LegP1Container'))
    if leg_p1_containers:
        for container in leg_p1_containers:
            sections += extract_space(container.text.strip()) + '\n'
    return sections


def get_section(soup, statute):
    doc_container = soup.find(class_='DocContainer')
    start = False
    all_text = False
    title = ""
    key = ""
    content = ""
    tables = []
    if doc_container:
        for child in doc_container.children:
            if child.name:
                if child.name == 'div':
                    for inner_child in child.children:
                        if inner_child.name:
                            content, key, start, tables, title, all_text = extract_fields(all_text, inner_child,
                                                                                          content, key,
                                                                                          start,
                                                                                          statute,
                                                                                          tables, title)
                else:
                    content, key, start, tables, title, all_text = extract_fields(all_text, child, content, key, start,
                                                                                  statute,
                                                                                  tables, title)

        if start:
            statute.add_section(title=title, content=content, key=key, tables=tables)


def add_image(src, title, count):
    return {
        "altText": title,
        "link": src,
        "name": 'image_' + str(count)
    }


def extract_schedule(soup, statute):
    doc_container = soup.find(class_='DocContainer')
    content = ""
    tables = []
    title = ""
    images = []
    start = False
    if doc_container:
        for child in doc_container.children:
            if child.name:
                image = child.find(class_=re.compile(r'^LegDisplayImage'))
                if image:
                    images.append(add_image(image.get('src'), title, len(images) + 1))
                child_class = child.get('class')
                extract_table(child, child_class, tables)
                if child_class and any(re.search(r'LegSchedule', cls) for cls in child_class):
                    if not start and child.text:
                        title = child.text.strip()
                    start = True
                if start and child.text.strip():
                    content += extract_space(child.text.strip()) + '\n'
        statute.add_schedule(content=content, tables=tables, images=images)


def extract_fields(all_text, child, content, key, start, statute, tables, title):
    child_class = child.get('class')
    child_id = child.get('id')
    text = child.text.strip().lower()
    if (re.match(
            r'^h[1-6]+', child.name) and text and re.match(
        r'^section *[0-9]+', text)) or (child_id and re.match(r'^section[- ][0-9]+$', child_id)):
        if start:
            statute.add_section(title=title, content=content, key=key, tables=tables)

        title = ""
        content = ""
        tables = []
        start = True
        all_text = False
        if child_id and child_id.split('-') and len(child_id.split('-')) == 2:
            key = child_id.split('-')[1]
        else:
            key = extract_number(text)

    extract_table(child, child_class, tables)

    if start and child.find(class_=re.compile(r'^LegP1GroupTitle|LegPblockTitle')):
        title = extract_space(child.find(
            class_=re.compile(r'^LegP1GroupTitle|LegPblockTitle')).text.strip())
        all_text = True
    elif all_text:
        content += extract_space(child.text.strip()) + '\n'
    return content, key, start, tables, title, all_text


def extract_table(child, child_class, tables):
    if child_class and any(re.search(r'LegTabular', cls) for cls in child_class):
        name = child.get('id')
        rows = []
        extract_table_content(child, rows, 'thead')
        extract_table_content(child, rows, 'tbody')
        extract_table_content(child, rows, 'tfoot')
        row_count, col_count = get_row_and_col_counts(rows)
        tables.append({
            "rowCount": row_count,
            "colCount": int(math.ceil(col_count)),
            "name": name,
            "rows": rows,
        })


def get_row_and_col_counts(rows):
    col_counts = 0
    row_count = 0
    if rows and len(rows) > 0:
        row_count = len(rows)
        col_counts = len(rows[0])
    return row_count, col_counts


def extract_table_content(child, rows, class_name):
    table = child.find(class_name)
    if table:
        for table_row in table.children:
            row = []
            if table_row.name == "tr":
                for cell in table_row.children:
                    if cell.text.strip():
                        row.append(extract_space(cell.text.strip()))
            if len(row) > 0:
                rows.append(row)


def extract_space_without_newline(text):
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r' *\n *', '\n', text)
    return text
    # return text


def extract_space(text):
    return re.sub(r'\s{2,}', ' ', re.sub(r'\s*\n\s*', ' ', text.strip()))


def extract_number(text):
    match = re.search(r'\d+', text)
    if match:
        return int(match.group())
    else:
        return None


def convert_date(date_str, input_path):
    date_str = extract_first_date(re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str))
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, '%d %B %Y')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            try:
                return date_str
            except ValueError:
                print(date_str, ValueError, input_path)
            # locale.setlocale(locale.LC_TIME, "welsh")
            # return datetime.strptime(date_str, "%d %B %Y")
    return date_str


def extract_first_date(text):
    date_pattern = r'\b(\d{1,2} [A-Z][a-z]+ \d{4})\b'
    dates = re.findall(date_pattern, text)
    if dates and len(dates) > 1:
        first_date_str = dates[1]
        return first_date_str
    else:
        return text


class ProcessHtml(IProcess):
    def process_file(self, input_path, output_path):
        # Read HTML content from file
        with open(input_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # Extracting information
        title = soup.find('title').text.strip() if soup.find('title') else ""  #okay

        effective_date = convert_date(
            re.sub(r'[\[\]]', ' ', soup.find('p', class_=re.compile(r'^LegDateOfEnactment')).text).strip() if soup.find(
                'p', class_=re.compile(r'^LegDateOfEnactment')) else "", input_path)  # okay

        list_of_sections = get_list_sections(soup)  # okay

        preamble = soup.find(class_='LegLongTitle').text.strip() if soup.find(class_='LegLongTitle') else ""  # okay

        pre_sections_text = re.sub(r'\s{2,}', ' ',
                                   re.sub(r'\s*\n\s*', ' ', soup.find(class_='LegPrelims').text.strip() if soup.find(
                                       class_='LegLongTitle') else ""))  # okay

        statute_id = extract_space(soup.find(class_='LegNo').text.strip() if soup.find(
            class_='LegNo') else "")  # okay

        # Initialize Statute instance
        statute = Statute(
            title=title,
            listOfSections=list_of_sections,
            preamble=preamble,
            effectiveDate=effective_date,
            preSectionsText=pre_sections_text,
            statuteId=statute_id,
        )
        get_section(soup, statute)
        extract_schedule(soup, statute)
        json_content = statute.to_json()

        # Write to output file
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(json_content)
