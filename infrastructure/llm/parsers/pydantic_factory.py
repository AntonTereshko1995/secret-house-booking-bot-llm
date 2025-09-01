from langchain.output_parsers import PydanticOutputParser


def make_parser(schema_cls):
    return PydanticOutputParser(pydantic_object=schema_cls)
