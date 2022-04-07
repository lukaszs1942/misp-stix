# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import json
import subprocess
import traceback
from .exceptions import (SynonymsResourceJSONError, UnavailableGalaxyResourcesError,
    UnavailableSynonymsResourceError)
from collections import defaultdict
from pathlib import Path
from typing import Union

_ROOT_PATH = Path(__file__).parents[2].resolve()


class STIXtoMISPParser:
    def __init__(self, synonyms_path: Union[None, str]):
        if synonyms_path is not None:
            self.__synonyms_path = Path(synonyms_path)
        self.__errors = defaultdict(set)
        self.__warnings = defaultdict(set)

    @property
    def errors(self) -> dict:
        return self.__errors

    @property
    def synonyms_mapping(self) -> dict:
        try:
            return self.__synonyms_mapping
        except AttributeError:
            self.__get_synonyms_mapping()
            return self.__synonyms_mapping

    @property
    def warnings(self) -> set:
        return self.__warnings

    ################################################################################
    #                    ERRORS AND WARNINGS HANDLING FUNCTIONS                    #
    ################################################################################

    def _attack_pattern_error(self, attack_pattern_id: str, exception: Exception):
        tb = self._parse_traceback(exception)
        message = f"Error with the Attack Pattern object with id {attack_pattern_id}: {tb}"
        self.__errors[self._identifier].add(message)

    def _attribute_from_pattern_parsing_error(self, indicator_id: str):
        message = f"Error while parsing pattern from indicator with id {indicator_id}"
        self.__errors[self._identifier].add(message)

    def _course_of_action_error(self, course_of_action_id: str, exception: Exception):
        tb = self._parse_traceback(exception)
        message = f"Error with the Course of Action object with id {course_of_action_id}: {tb}"
        self.__error[self._identifier].add(message)

    def _identity_error(self, identity_id: str, exception: Exception):
        tb = self._parse_traceback(exception)
        message = f"Error with the Identity object with id {identity_id}: {tb}"
        self.__errors[self._identifier].add(message)

    def _malware_error(self, malware_id: str, exception: Exception):
        tb = self._parse_traceback(exception)
        message = f"Error with the Malware object with id {malware_id}: {tb}"
        self.__errors[self._identifier].add(message)

    def _object_ref_loading_error(self, object_ref: str):
        message = f"Error loading the STIX object with id {object_ref}"
        self.__errors[self._identifier].add(message)

    def _object_type_loading_error(self, object_type: str):
        message = f"Error loading the STIX object of type {object_type}"
        self.__errors[self._identifier].add(message)

    def _observed_data_error(self, observed_data_id: str, exception: Exception):
        tb = self._parse_traceback(exception)
        message = f"Error with the Observed Data object with id {observed_data_id}: {tb}"
        self.__errors[self._identifier].add(message)

    @staticmethod
    def _parse_traceback(exception: Exception) -> str:
        tb = ''.join(traceback.format_tb(exception.__traceback__))
        return f'{tb}{exception.__str__()}'

    def _tool_error(self, tool_id: str, exception: Exception):
        tb = self._parse_traceback(exception)
        message = f"Error with the Tool object with id {tool_id}: {tb}"
        self.__errors[self._identifier].add(message)

    def _unable_to_load_stix_object_type_error(self, object_type: str):
        message = f"Unable to load STIX object type: {object_type}"
        self.__errors[self._identifier].add(message)

    def _undefined_object_error(self, object_id: str):
        message = f"Unable to define the object identified with the id: {object_id}"
        self.__errors[self._identifier].add(message)

    def _unknown_attribute_type_warning(self, attribute_type: str):
        message = f"MISP attribute type not mapped: {attribute_type}"
        self.__warnings[self._identifier].add(message)

    def _unknown_object_name_warning(self, name: str):
        message = f"MISP object name not mapped: {name}"
        self.__warnings[self._identifier].add(message)

    def _unknown_parsing_function_error(self, feature: str):
        message = f"Unknown STIX parsing function name: {feature}"
        self.__errors[self._identifier].add(message)

    def _unknown_pattern_mapping_warning(self, indicator_id: str, observable_types: tuple):
        types = f"containing the following types: {', '.join(observable_types)}"
        message = f"Unable to map pattern from the indicator with id {indicator_id}, {types}"
        self.__warnings[self._identifier].add(message)

    def _unknown_pattern_type_error(self, indicator_id: str, pattern_type: str):
        message = f"Unknown pattern type in indicator with id {indicator_id}: {pattern_type}"
        self.__errors[self._identifier].add(message)

    def _unknown_stix_object_type_error(self, object_type: str):
        message = f"Unknown STIX object type: {object_type}"
        self.__errors[self._identifier].add(message)

    def _vulnerability_error(self, vulnerability_id: str, exception: Exception):
        tb = self._parse_traceback(exception)
        message = f"Error with the Vulnerability object with id {vulnerability_id}: {tb}"
        self.__errors[self._identifier].add(message)

    ################################################################################
    #           SYNONYMS TO GALAXY TAG NAMES MAPPING HANDLING FUNCTIONS.           #
    ################################################################################

    def __galaxies_up_to_date(self) -> bool:
        fingerprint_path = _ROOT_PATH / 'tmp' / 'synonymsToTagNames.fingerprint'
        if not fingerprint_path.exists():
            return False
        with open(fingerprint_path, 'rt', encoding='utf-8') as f:
            fingerprint = f.read()
        return fingerprint == self.__get_misp_galaxy_fingerprint()

    def __generate_synonyms_mapping(self):
        data_path = _ROOT_PATH / 'data' / 'misp-galaxy' / 'clusters'
        if not data_path.exists():

            raise UnavailableGalaxyResourcesError(data_path)
        synonyms_mapping = defaultdict(list)
        for filename in data_path.glob('*.json'):
            with open(filename, 'rt', encoding='utf-8') as f:
                cluster_definition = json.loads(f.read())
            cluster_type = f"misp-galaxy:{cluster_definition['type']}"
            for cluster in cluster_definition['values']:
                value = cluster['value']
                tag_name = f'{cluster_type}="{value}"'
                synonyms_mapping[value].append(tag_name)
                if cluster.get('meta') is not None and cluster['meta'].get('synonyms') is not None:
                    for synonym in cluster['meta']['synonyms']:
                        synonyms_mapping[synonym].append(tag_name)
        with open(self.__synonyms_path, 'wt', encoding='utf-8') as f:
            f.write(json.dumps(synonyms_mapping))
        fingerprint_path = _ROOT_PATH / 'tmp' / 'synonymsToTagNames.fingerprint'
        with open(fingerprint_path, 'rt', encoding='utf-8') as f:
            f.write(self.__get_misp_galaxy_fingerprint())

    @staticmethod
    def __get_misp_galaxy_fingerprint():
        galaxy_path = _ROOT_PATH / 'data' / 'misp-galaxy'
        status = subprocess.Popen(
            [
                'git',
                'submodule',
                'status',
                galaxy_path
            ],
            stdout=subprocess.PIPE
        )
        stdout = status.communicate()[0]
        return stdout.decode().split(' ')[1]

    def __get_synonyms_mapping(self):
        if not hasattr(self, '__synonyms_path'):
            self.__synonyms_path = _ROOT_PATH / 'tmp' / 'synonymsToTagNames.json'
            if not self.__synonyms_path.exists() or not self.__galaxies_up_to_date():
                self.__generate_synonyms_mapping()
        else:
            if not self.__synonyms_path.exists():
                self.__generate_synonyms_mapping()
        self.__load_synonyms_mapping()

    def __load_synonyms_mapping(self):
        try:
            with open(self.__synonyms_path, 'rt', encoding='utf-8') as f:
                self.__synonyms_mapping = json.loads(f.read())
        except FileNotFoundError:
            message = f""
            raise UnavailableSynonymsResourceError(message)
        except json.JSONDecodeError:
            message = f""
            raise SynonymsResourceJSONError(message)
