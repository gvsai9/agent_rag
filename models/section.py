from dataclasses import dataclass


@dataclass
class Section:
    title: str #The title of the section, which is a string that represents the heading of the section in the paper. This can be used to identify the main topic or theme of the section.
    text: str #The text of the section, which is a string that contains the content of the section. This can be used to extract information and answer questions related to the topic of the section.