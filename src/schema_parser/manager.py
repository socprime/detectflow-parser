import copy
import logging

from flatten_dict import flatten as flatten_dict_func

from schema_parser.functions import CORE_FUNCTIONS
from schema_parser.parsers import PREDEFINED_PARSERS
from schema_parser.query_normalizer import QueryNormalizer

logger = logging.getLogger(__name__)


class ParserManager:
    """
    Manages parsing operations for events using configured or predefined parsers.

    Provides methods to parse events using:
    - Configured parsers with custom function chains
    - Predefined parsers (e.g., windows_event)
    - Query-based parsers that are normalized from string queries
    """

    query_normalizer = QueryNormalizer()
    predefined_parsers = PREDEFINED_PARSERS
    core_functions = CORE_FUNCTIONS

    def configured_parser(
        self,
        event: dict,
        parser_config: dict,
        suppress_errors: bool = False,
        log_errors: bool = False,
        flatten: bool = False,
    ) -> dict:
        steps = parser_config["steps"]
        args = parser_config["args"]
        result = copy.deepcopy(event)

        try:
            for step in steps:
                step_function = self.core_functions.get(step)
                if not step_function:
                    raise ValueError(f"Function {step} not found")

                step_args = args.get(step, {})
                result = step_function.execute(data=result, **step_args)

            if flatten:
                result = flatten_dict_func(result, reducer="dot")
            return result
        except Exception as e:
            if suppress_errors:
                if log_errors:
                    logger.error(f"Error parsing event: {e}")
                return event
            raise e

    def predefined_parser(self, event: dict, parser_name: str) -> dict:
        parser = self.predefined_parsers.get(parser_name)
        if not parser:
            raise ValueError(f"Parser {parser_name} not found")
        return parser.parse(event)

    def query_parser(self, query: str) -> dict:
        parser_config = self.query_normalizer.parse_query(query)
        return parser_config
