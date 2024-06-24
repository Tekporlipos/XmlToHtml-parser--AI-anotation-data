import json
from typing import List, Dict, Any


class Statute:
    def __init__(self, title: str = "", dateOfAssent: str = "", effectiveDate: str = "", dateOfGazette: str = "",
                 listOfSections: str = "", preamble: str = "", preSectionsText: str = "", footnotes: str = "",
                 endnotes: str = "", statuteId: str = "", isDateOfAssentUnavailable: bool = False,
                 isEffectiveDateUnavailable: bool = False, isDateOfGazetteUnavailable: bool = False):
        self.title = title
        self.dateOfAssent = dateOfAssent
        self.effectiveDate = effectiveDate
        self.dateOfGazette = dateOfGazette
        self.listOfSections = listOfSections
        self.preamble = preamble
        self.schedule = {
            "content": "",
            "tables": [],
            "images": []
        }
        self.preSectionsText = preSectionsText
        self.sections: List[Dict[str, Any]] = []
        self.footnotes = footnotes
        self.endnotes = endnotes
        self.statuteId = statuteId
        self.isDateOfAssentUnavailable = isDateOfAssentUnavailable
        self.isEffectiveDateUnavailable = isEffectiveDateUnavailable
        self.isDateOfGazetteUnavailable = isDateOfGazetteUnavailable

    def add_section(self, title: str = "", key: str = "", content: str = "", tables: List[dict] = None,
                    images: List[str] = None):
        if tables is None:
            tables = []
        if images is None:
            images = []

        section = {
            "title": title,
            "key": key,
            "content": content,
            "tables": tables,
            "images": images
        }
        self.sections.append(section)

    def add_schedule(self, content: str = "", tables: List[dict] = None,
                     images: List[str] = None):
        if tables is None:
            tables = []
        if images is None:
            images = []
        self.schedule = {
            "content": content,
            "tables": tables,
            "images": images
        }

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)
