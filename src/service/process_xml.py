import xml
import xml.etree.ElementTree as et
from jinja2 import Template
import re

from src.parser.html_template import html_template
from src.service.process import IProcess

namespaces = {
    'akomaNtoso': 'http://docs.oasis-open.org/legaldocml/ns/akn/3.0',
    'uk': 'https://caselaw.nationalarchives.gov.uk/akn'
}


def get_case_id(header):
    case_id_element = header.find(".//neutralCitation")
    return case_id_element.text if case_id_element is not None else 'No CaseId'


def create_paragraph(text):
    return f"<p>{text}</p>"


def create_div(text):
    return f"<div>{text}</div>"


def create_p_with_id(text, id):
    return f"<p id=\"{id}\">{text}</p>"


def extract_inner_text(element_string):
    if isinstance(element_string, bytes):
        element_string = element_string.decode('utf-8').replace("<ns0:br />", "@")
    text_content = re.sub(r'<.*?>', ' ', element_string)
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    return text_content


def replace_with_p(element: str):
    paragram = []
    for child in element.split("@"):
        if len(child.strip()) > 0:
            paragram.append(create_paragraph(child))
    return ' '.join(paragram)


def extract_specific_text(element):
    paragraphs = []
    words = []

    for child in element.iter():
        if child.tag == '{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}br':
            if words:
                paragraphs.append(create_paragraph(' '.join(words)))
                words = []
        else:
            if child.text and child.text.strip():
                words.append(child.text.strip())
            if child.tail and child.tail.strip():
                words.append(child.tail.strip())
    if words:
        paragraphs.append(create_paragraph(' '.join(words)))
    return ' '.join(paragraphs)


def get_head_note(header_children):
    notes_map = []
    for note in header_children.findall('.//akomaNtoso:p', namespaces):
        text = extract_inner_text(xml.etree.ElementTree.tostring(element=note))
        if len(re.sub(r'[^a-zA-Z]', '', text)) > 0:
            notes_map.append(replace_with_p(text))
    return ' '.join(notes_map)


def get_case_no(header_children):
    notes_map = ''
    for note in header_children.findall('.//akomaNtoso:p', namespaces):
        p_text = extract_inner_text(xml.etree.ElementTree.tostring(element=note))
        if 'Case No:' in p_text:
            notes_map = p_text.replace('Case No:', '').strip()
    return notes_map


def get_parties(parties_root):
    parties_element = parties_root.find('.//akomaNtoso:header', namespaces)
    judges_map = []
    for party in parties_element.iter():
        if party.tag.endswith('role') or party.tag.endswith('party'):
            judges_map.append(extract_specific_text(party))
    return ''.join(judges_map) if judges_map and len(judges_map) >= 3 else extract_to_p(parties_root)


def extract_to_p(parties_root):
    title = get_title(parties_root)
    text = re.split(r' [Vv] ', title)
    return (create_paragraph(text[0]) + create_paragraph("v") + create_paragraph(text[1])) if len(text) > 1 \
        else create_paragraph(title)


def get_judges(judges_root):
    judges_element = judges_root.findall('.//akomaNtoso:judge', namespaces)
    judges_map = []
    for judge in judges_element:
        judges_map.append(create_paragraph(judge.text))
    return ''.join(judges_map) if judges_map else get_judges_from_header(judges_root)


def is_username_valid(username):
    if not isinstance(username, str):
        return False
    if not (2 <= len(username.split(" ")) <= 8):
        return False
    if not re.match(r'^[A-Za-z][A-Za-z ,.]*', username):
        return False
    if not len(re.sub(r'[^a-zA-Z]', '', username)) > 10:
        return False
    return True


def get_judges_from_header(judges_root, take_one=False):
    judges_element = judges_root.find('.//akomaNtoso:header', namespaces).findall('.//akomaNtoso:p', namespaces)
    judges_map = []
    start = False
    for judge in judges_element:
        inner_text = extract_inner_text(extract_specific_text(judge))
        if inner_text.lower().strip().startswith("between"):
            break
        if start:
            if start and not is_username_valid(inner_text):
                break
            judges_map.append(create_paragraph(inner_text))
            if len(judges_map) == 1 and take_one:
                break
        if (inner_text.lower().strip().startswith("before") or
                inner_text.lower().strip().startswith("tribunal")):
            start = True
    return ''.join(judges_map) if judges_map else ''


def get_content(contents_element):
    judges_map = []
    for element_content in list(contents_element):
        content_tag = element_content.tag
        if content_tag.endswith('paragraph'):
            judges_map.extend(handle_paragraph(element_content))
        elif content_tag.endswith('level'):
            judges_map.append(create_div(handle_level(element_content)))
    return ''.join(judges_map) if judges_map else ''


def handle_level(element_content):
    children = list(element_content)
    level = []
    for child in children:
        if child.tag.endswith('paragraph'):
            level.extend(handle_paragraph(child))
        else:
            level.append(extract_specific_text(child))
    return ''.join(level) if level else ''


def handle_paragraph(paragraph):
    dev_id = None
    dev_text = None
    for child in list(paragraph):
        if child.tag.endswith('num') and child.text is not None:
            text = child.text
            cleaned_text = re.sub(r'\W+', '', text)
            dev_id = cleaned_text.strip()
        else:
            dev_text = extract_inner_text(extract_specific_text(child))
    return create_p_with_id(dev_text, id=dev_id)


def get_first_judge(judge_elements):
    all_judges = get_judges(judge_elements)
    return all_judges[0] if all_judges else None


def get_title(root):
    return root.find('.//akomaNtoso:FRBRname', namespaces).attrib.get('value') if root.find(
        './/akomaNtoso:FRBRname', namespaces) is not None else ''


def get_cort_name(root):
    cort_element = root.find('.//akomaNtoso:TLCOrganization', namespaces)
    if cort_element is not None:
        return create_paragraph(cort_element.attrib.get('shortForm')) if cort_element.attrib.get(
            'shortForm') is not None else create_paragraph(cort_element.attrib.get('showAs'))
    return ''


class ProcessXML(IProcess):
    def process_file(self, xml_path, output_path):
        # Parse XML file
        tree = et.parse(xml_path)
        root = tree.getroot()

        # Extract content using namespace
        title = create_paragraph(get_title(root))
        date = create_paragraph(root.find('.//akomaNtoso:FRBRdate', namespaces).attrib.get('date')) if root.find(
            './/akomaNtoso:FRBRdate', namespaces) is not None else ''
        source = create_paragraph('UK CASE LAW NATIONAL ARCHIVES')
        court = get_cort_name(root)
        court_location = create_paragraph('United Kingdom')
        media_nuetral_citation = create_paragraph(
            root.find('.//akomaNtoso:neutralCitation', namespaces).text) if root.find(
            './/akomaNtoso:neutralCitation', namespaces) is not None else ''
        headnotes = get_head_note(root.find('.//akomaNtoso:header', namespaces))
        content = get_content(root.find('.//akomaNtoso:decision', namespaces))
        case_id = get_case_no(root.find('.//akomaNtoso:header', namespaces))

        judges = get_judges(root)
        presiding_judge = create_paragraph(root.find('.//akomaNtoso:judge', namespaces).text) if root.find(
            './/akomaNtoso:judge', namespaces) is not None else get_judges_from_header(root, True)

        parties = get_parties(root)

        # Render HTML using the template
        template = Template(html_template)
        html_content = template.render(
            title=title,
            date=date,
            case_id=case_id,
            court=court,
            court_location=court_location,
            judges=judges,
            presiding_judge=presiding_judge,
            parties=parties,
            source=source,
            media_nuetral_citation=media_nuetral_citation,
            headnotes=headnotes,
            content=content
        )

        # Write to output HTML file
        with open(output_path, 'w') as file:
            file.write(html_content)
