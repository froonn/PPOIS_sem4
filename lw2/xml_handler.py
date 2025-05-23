import xml.etree.ElementTree as ET
import xml.sax


class XMLWriter:
    """
    Writes teacher records to an XML file using DOM (ElementTree).
    """

    @staticmethod
    def write_records_to_xml(records, file_path):
        """
        Writes a list of teacher records to an XML file.
        :param records: List of dictionaries, each representing a teacher record.
                        Example: [{'id': 1, 'faculty': 'F1', ...}, ...]
        :param file_path: Path to the output XML file.
        """
        root = ET.Element("Teachers")
        for record in records:
            teacher_element = ET.SubElement(root, "Teacher")
            for key, value in record.items():
                field_element = ET.SubElement(teacher_element, key)
                field_element.text = str(value)

        tree = ET.ElementTree(root)
        ET.indent(tree, space="\t", level=0)
        tree.write(file_path, encoding="utf-8", xml_declaration=True)


class TeacherHandler(xml.sax.ContentHandler):
    """
    SAX content handler for parsing teacher records from an XML file.
    """

    def __init__(self):
        self.records = []
        self.current_element = ""
        self.current_record = {}

    def startElement(self, name, attrs):
        self.current_element = name
        if name == "Teacher":
            self.current_record = {}

    def characters(self, content):
        if self.current_element and content.strip():
            self.current_record[self.current_element] = content.strip()

    def endElement(self, name):
        if name == "Teacher":
            if 'experience' in self.current_record:
                try:
                    self.current_record['experience'] = int(self.current_record['experience'])
                except ValueError:
                    self.current_record['experience'] = 0  # Default or handle error
            if 'id' in self.current_record:
                del self.current_record['id']

            self.records.append(self.current_record)
        self.current_element = ""  # Reset current element


class XMLReader:
    """
    Reads teacher records from an XML file using SAX.
    """

    @staticmethod
    def read_records_from_xml(file_path):
        """
        Reads teacher records from an XML file using SAX parser.
        :param file_path: Path to the input XML file.
        :return: List of dictionaries, each representing a teacher record.
        """
        parser = xml.sax.make_parser()
        handler = TeacherHandler()
        parser.setContentHandler(handler)
        parser.parse(file_path)
        return handler.records
