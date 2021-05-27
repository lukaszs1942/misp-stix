#!/usr/bin/env python
# -*- coding: utf-8 -*-

from misp_stix_converter import MISPtoSTIX21Parser
from .test_events import *
from ._test_stix2_export import TestSTIX2Export


class TestSTIX21Export(TestSTIX2Export):
    def setUp(self):
        self.parser = MISPtoSTIX21Parser()

    ################################################################################
    #                              UTILITY FUNCTIONS.                              #
    ################################################################################

    def _check_bundle_features(self, length):
        bundle = self.parser.bundle
        self.assertEqual(bundle.type, 'bundle')
        self.assertEqual(len(bundle.objects), length)
        return bundle.objects

    def _check_grouping_features(self, grouping, event, identity_id):
        timestamp = self._datetime_from_timestamp(event['timestamp'])
        self.assertEqual(grouping.type, 'grouping')
        self.assertEqual(grouping.id, f"grouping--{event['uuid']}")
        self.assertEqual(grouping.created_by_ref, identity_id)
        self.assertEqual(grouping.labels, self._labels)
        self.assertEqual(grouping.name, event['info'])
        self.assertEqual(grouping.created, timestamp)
        self.assertEqual(grouping.modified, timestamp)
        return grouping.object_refs

    def _check_pattern_features(self, indicator):
        self.assertEqual(indicator.pattern_type, 'stix')
        self.assertEqual(indicator.pattern_version, '2.1')

    def _check_spec_versions(self, stix_objects):
        for stix_object in stix_objects:
            self.assertEqual(stix_object.spec_version, '2.1')

    @staticmethod
    def _reorder_observable_objects(observables, ids):
        ordered_observables = []
        ordered_ids = []
        tmp_observable = [observables.pop(0)]
        tmp_id = [ids.pop(0)]
        for observable, _id in zip(observables, ids):
            if observable.type == 'observed-data':
                ordered_observables.append(tmp_observable)
                ordered_ids.append(tmp_id)
                tmp_observable = [observable]
                tmp_id = [_id]
            else:
                tmp_observable.append(observable)
                tmp_id.append(_id)
        ordered_observables.append(tmp_observable)
        ordered_ids.append(tmp_id)
        return ordered_observables, ordered_ids

    def _run_galaxy_tests(self, event, timestamp):
        orgc = event['Event']['Orgc']
        self.parser.parse_misp_event(event)
        stix_objects = self.parser.stix_objects
        self._check_spec_versions(stix_objects)
        identity, grouping, stix_object = stix_objects
        identity_id = self._check_identity_features(identity, orgc, timestamp)
        args = (grouping, event['Event'], identity_id)
        object_ref = self._check_grouping_features(*args)[0]
        self.assertEqual(stix_object.id, object_ref)
        return stix_object

    def _run_indicators_from_objects_tests(self, event):
        self._add_object_ids_flag(event)
        orgc = event['Event']['Orgc']
        misp_objects = deepcopy(event['Event']['Object'])
        self.parser.parse_misp_event(event)
        stix_objects = self.parser.stix_objects
        self._check_spec_versions(stix_objects)
        identity, grouping, *indicators = stix_objects
        identity_id = self._check_identity_features(
            identity,
            orgc,
            self._datetime_from_timestamp(event['Event']['timestamp'])
        )
        args = (grouping, event['Event'], identity_id)
        object_refs = self._check_grouping_features(*args)
        for indicator, misp_object, object_ref in zip(indicators, misp_objects, object_refs):
            self._check_object_indicator_features(indicator, misp_object, identity_id, object_ref)
            self._check_pattern_features(indicator)
        return misp_objects, tuple(indicator.pattern for indicator in indicators)

    def _run_indicator_from_objects_tests(self, event):
        self._add_object_ids_flag(event)
        orgc = event['Event']['Orgc']
        misp_objects = deepcopy(event['Event']['Object'])
        self.parser.parse_misp_event(event)
        stix_objects = self.parser.stix_objects
        self._check_spec_versions(stix_objects)
        identity, grouping, indicator = stix_objects
        identity_id = self._check_identity_features(
            identity,
            orgc,
            self._datetime_from_timestamp(event['Event']['timestamp'])
        )
        args = (grouping, event['Event'], identity_id)
        object_ref = self._check_grouping_features(*args)[0]
        self._check_object_indicator_features(indicator, misp_objects[0], identity_id, object_ref)
        self._check_pattern_features(indicator)
        return misp_objects, indicator.pattern

    def _run_indicator_from_object_tests(self, event):
        self._add_object_ids_flag(event)
        orgc = event['Event']['Orgc']
        misp_object = deepcopy(event['Event']['Object'][0])
        self.parser.parse_misp_event(event)
        stix_objects = self.parser.stix_objects
        self._check_spec_versions(stix_objects)
        identity, grouping, indicator = stix_objects
        identity_id = self._check_identity_features(
            identity,
            orgc,
            self._datetime_from_timestamp(event['Event']['timestamp'])
        )
        args = (grouping, event['Event'], identity_id)
        object_ref = self._check_grouping_features(*args)[0]
        self._check_object_indicator_features(indicator, misp_object, identity_id, object_ref)
        self._check_pattern_features(indicator)
        return misp_object['Attribute'], indicator.pattern

    def _run_indicator_tests(self, event):
        self._add_attribute_ids_flag(event)
        orgc = event['Event']['Orgc']
        attribute = event['Event']['Attribute'][0]
        self.parser.parse_misp_event(event)
        stix_objects = self.parser.stix_objects
        self._check_spec_versions(stix_objects)
        identity, grouping, indicator = stix_objects
        identity_id = self._check_identity_features(
            identity,
            orgc,
            self._datetime_from_timestamp(event['Event']['timestamp'])
        )
        args = (grouping, event['Event'], identity_id)
        object_ref = self._check_grouping_features(*args)[0]
        self._check_attribute_indicator_features(indicator, attribute, identity_id, object_ref)
        self._check_pattern_features(indicator)
        return attribute['value'], indicator.pattern

    def _run_indicators_tests(self, event):
        self._add_attribute_ids_flag(event)
        orgc = event['Event']['Orgc']
        attributes = event['Event']['Attribute']
        self.parser.parse_misp_event(event)
        stix_objects = self.parser.stix_objects
        self._check_spec_versions(stix_objects)
        identity, grouping, *indicators = stix_objects
        identity_id = self._check_identity_features(
            identity,
            orgc,
            self._datetime_from_timestamp(event['Event']['timestamp'])
        )
        args = (grouping, event['Event'], identity_id)
        object_refs = self._check_grouping_features(*args)
        for attribute, indicator, object_ref in zip(attributes, indicators, object_refs):
            self._check_attribute_indicator_features(indicator, attribute, identity_id, object_ref)
            self._check_pattern_features(indicator)
        attribute_values = (attribute['value'] for attribute in attributes)
        patterns = (indicator.pattern for indicator in indicators)
        return attribute_values, patterns

    def _run_observables_from_objects_tests(self, event):
        self._remove_object_ids_flags(event)
        orgc = event['Event']['Orgc']
        misp_objects = deepcopy(event['Event']['Object'])
        self.parser.parse_misp_event(event)
        stix_objects = self.parser.stix_objects
        self._check_spec_versions(stix_objects)
        identity, grouping, *observables = stix_objects
        identity_id = self._check_identity_features(
            identity,
            orgc,
            self._datetime_from_timestamp(event['Event']['timestamp'])
        )
        ids = self._check_grouping_features(grouping, event['Event'], identity_id)
        observables, ids = self._reorder_observable_objects(observables, ids)
        object_refs = []
        for observable, misp_object, observable_id in zip(observables, misp_objects, ids):
            observed_data = observable.pop(0)
            object_refs.append(observed_data['object_refs'])
            self._check_object_observable_features(
                observed_data,
                misp_object,
                identity_id,
                observable_id.pop(0)
            )
        return misp_objects, ids, object_refs, observables

    def _run_observable_from_objects_tests(self, event):
        self._remove_object_ids_flags(event)
        orgc = event['Event']['Orgc']
        misp_objects = deepcopy(event['Event']['Object'])
        self.parser.parse_misp_event(event)
        stix_objects = self.parser.stix_objects
        self._check_spec_versions(stix_objects)
        identity, grouping, observed_data, *observable = stix_objects
        identity_id = self._check_identity_features(
            identity,
            orgc,
            self._datetime_from_timestamp(event['Event']['timestamp'])
        )
        observable_id, *ids = self._check_grouping_features(
            grouping,
            event['Event'],
            identity_id
        )
        self._check_object_observable_features(
            observed_data,
            misp_objects[0],
            identity_id,
            observable_id
        )
        return misp_objects, ids, observed_data['object_refs'], observable

    def _run_observable_from_object_tests(self, event):
        self._remove_object_ids_flags(event)
        orgc = event['Event']['Orgc']
        misp_object = deepcopy(event['Event']['Object'][0])
        self.parser.parse_misp_event(event)
        stix_objects = self.parser.stix_objects
        self._check_spec_versions(stix_objects)
        identity, grouping, observed_data, *observable = stix_objects
        identity_id = self._check_identity_features(
            identity,
            orgc,
            self._datetime_from_timestamp(event['Event']['timestamp'])
        )
        observable_id, *ids = self._check_grouping_features(
            grouping,
            event['Event'],
            identity_id
        )
        self._check_object_observable_features(
            observed_data,
            misp_object,
            identity_id,
            observable_id
        )
        return misp_object['Attribute'], ids, observed_data['object_refs'], observable

    def _run_observable_tests(self, event):
        self._remove_attribute_ids_flag(event)
        orgc = event['Event']['Orgc']
        attribute = event['Event']['Attribute'][0]
        self.parser.parse_misp_event(event)
        stix_objects = self.parser.stix_objects
        self._check_spec_versions(stix_objects)
        identity, grouping, observed_data, *observable = stix_objects
        identity_id = self._check_identity_features(
            identity,
            orgc,
            self._datetime_from_timestamp(event['Event']['timestamp'])
        )
        observable_id, *ids = self._check_grouping_features(
            grouping,
            event['Event'],
            identity_id
        )
        self._check_attribute_observable_features(
            observed_data,
            attribute,
            identity_id,
            observable_id
        )
        return attribute['value'], ids, observed_data['object_refs'], observable

    def _run_observables_tests(self, event, index=2):
        self._remove_attribute_ids_flag(event)
        orgc = event['Event']['Orgc']
        attributes = event['Event']['Attribute']
        self.parser.parse_misp_event(event)
        stix_objects = self.parser.stix_objects
        self._check_spec_versions(stix_objects)
        identity, grouping, *observables = stix_objects
        observed_datas = observables[::index]
        observables = [value for count, value in enumerate(observables) if count % index != 0]
        identity_id = self._check_identity_features(
            identity,
            orgc,
            self._datetime_from_timestamp(event['Event']['timestamp'])
        )
        ids = self._check_grouping_features(
            grouping,
            event['Event'],
            identity_id
        )
        observable_ids = ids[::index]
        object_ids = [value for count, value in enumerate(ids) if count % index != 0]
        for attribute, observed_data, observable_id in zip(attributes, observed_datas, observable_ids):
            self._check_attribute_observable_features(
                observed_data,
                attribute,
                identity_id,
                observable_id
            )
        attribute_values = tuple(attribute['value'] for attribute in attributes)
        object_refs = tuple(observed_data['object_refs'][0] for observed_data in observed_datas)
        return attribute_values, object_ids, object_refs, observables

    ################################################################################
    #                              EVENT FIELDS TESTS                              #
    ################################################################################

    def test_base_event(self):
        event = get_base_event()
        orgc = event['Event']['Orgc']
        self.parser.parse_misp_event(event)
        stix_objects = self._check_bundle_features(3)
        self._check_spec_versions(stix_objects)
        identity, grouping, note = stix_objects
        timestamp = self._datetime_from_timestamp(event['Event']['timestamp'])
        identity_id = self._check_identity_features(identity, orgc, timestamp)
        args = (
            grouping,
            event['Event'],
            identity_id
        )
        object_ref = self._check_grouping_features(*args)[0]
        self.assertEqual(note.type, 'note')
        self.assertEqual(note.id, f"note--{event['Event']['uuid']}")
        self.assertEqual(note.created_by_ref, identity_id)
        self.assertEqual(note.created, timestamp)
        self.assertEqual(note.modified, timestamp)
        self.assertEqual(
            note.content,
            "This MISP Event is empty and contains no attribute, object, galaxy or tag."
        )
        self.assertEqual(note.object_refs, [grouping.id])

    def test_published_event(self):
        event = get_published_event()
        orgc = event['Event']['Orgc']
        self.parser.parse_misp_event(event)
        stix_objects = self._check_bundle_features(3)
        self._check_spec_versions(stix_objects)
        identity, report, _ = stix_objects
        timestamp = self._datetime_from_timestamp(event['Event']['timestamp'])
        identity_id = self._check_identity_features(identity, orgc, timestamp)
        self._check_report_features(report, event['Event'], identity_id, timestamp)
        self.assertEqual(
            report.published,
            self._datetime_from_timestamp(event['Event']['publish_timestamp'])
        )

    def test_event_with_tags(self):
        event = get_event_with_tags()
        orgc = event['Event']['Orgc']
        self.parser.parse_misp_event(event)
        stix_objects = self._check_bundle_features(4)
        self._check_spec_versions(stix_objects)
        _, _, _, marking = stix_objects
        self.assertEqual(marking.definition_type, 'tlp')
        self.assertEqual(marking.definition['tlp'], 'white')

    ################################################################################
    #                        SINGLE ATTRIBUTES EXPORT TESTS                        #
    ################################################################################

    def test_embedded_indicator_attribute_galaxy(self):
        event = get_embedded_indicator_attribute_galaxy()
        orgc = event['Event']['Orgc']
        attribute = event['Event']['Attribute'][0]
        self.parser.parse_misp_event(event)
        stix_objects = self._check_bundle_features(8)
        self._check_spec_versions(stix_objects)
        identity, grouping, attack_pattern, course_of_action, indicator, malware, *relationships = stix_objects
        timestamp = self._datetime_from_timestamp(event['Event']['timestamp'])
        identity_id = self._check_identity_features(identity, orgc, timestamp)
        args = (
            grouping,
            event['Event'],
            identity_id
        )
        object_refs = self._check_grouping_features(*args)
        ap_ref, coa_ref, indicator_ref, malware_ref, apr_ref, coar_ref = object_refs
        ap_relationship, coa_relationship = relationships
        self.assertEqual(attack_pattern.id, ap_ref)
        self.assertEqual(course_of_action.id, coa_ref)
        self.assertEqual(indicator.id, indicator_ref)
        self.assertEqual(malware.id, malware_ref)
        self.assertEqual(ap_relationship.id, apr_ref)
        self.assertEqual(coa_relationship.id, coar_ref)
        timestamp = self._datetime_from_timestamp(attribute['timestamp'])
        self._check_relationship_features(ap_relationship, indicator_ref, ap_ref, 'indicates', timestamp)
        self._check_relationship_features(coa_relationship, indicator_ref, coa_ref, 'has', timestamp)

    def test_embedded_non_indicator_attribute_galaxy(self):
        event = get_embedded_non_indicator_attribute_galaxy()
        orgc = event['Event']['Orgc']
        attribute = event['Event']['Attribute'][0]
        self.parser.parse_misp_event(event)
        stix_objects = self._check_bundle_features(8)
        self._check_spec_versions(stix_objects)
        identity, grouping, attack_pattern, course_of_action, vulnerability, malware, *relationships = stix_objects
        timestamp = self._datetime_from_timestamp(event['Event']['timestamp'])
        identity_id = self._check_identity_features(identity, orgc, timestamp)
        args = (
            grouping,
            event['Event'],
            identity_id
        )
        object_refs = self._check_grouping_features(*args)
        ap_ref, coa_ref, vulnerability_ref, malware_ref, apr_ref, coar_ref = object_refs
        ap_relationship, coa_relationship = relationships
        self.assertEqual(attack_pattern.id, ap_ref)
        self.assertEqual(course_of_action.id, coa_ref)
        self.assertEqual(vulnerability.id, vulnerability_ref)
        self.assertEqual(malware.id, malware_ref)
        self.assertEqual(ap_relationship.id, apr_ref)
        self.assertEqual(coa_relationship.id, coar_ref)
        timestamp = self._datetime_from_timestamp(attribute['timestamp'])
        self._check_relationship_features(ap_relationship, vulnerability_ref, ap_ref, 'has', timestamp)
        self._check_relationship_features(coa_relationship, vulnerability_ref, coa_ref, 'has', timestamp)

    def test_embedded_observable_attribute_galaxy(self):
        event = get_embedded_observable_attribute_galaxy()
        orgc = event['Event']['Orgc']
        attribute = event['Event']['Attribute'][0]
        galaxy = event['Event']['Galaxy'][0]
        cluster = galaxy['GalaxyCluster'][0]
        self.parser.parse_misp_event(event)
        stix_objects = self._check_bundle_features(7)
        self._check_spec_versions(stix_objects)
        identity, grouping, attack_pattern, observed_data, autonomous_system, malware, relationship = stix_objects
        timestamp = self._datetime_from_timestamp(event['Event']['timestamp'])
        identity_id = self._check_identity_features(identity, orgc, timestamp)
        args = (
            grouping,
            event['Event'],
            identity_id
        )
        object_refs = self._check_grouping_features(*args)
        ap_ref, od_ref, as_ref, malware_ref, relationship_ref = object_refs
        self.assertEqual(attack_pattern.id, ap_ref)
        self.assertEqual(observed_data.id, od_ref)
        self.assertEqual(autonomous_system.id, as_ref)
        self.assertEqual(malware.id, malware_ref)
        self.assertEqual(relationship.id, relationship_ref)
        self._check_relationship_features(
            relationship,
            od_ref,
            ap_ref,
            'has',
            self._datetime_from_timestamp(attribute['timestamp'])
        )

    def test_event_with_as_indicator_attribute(self):
        event = get_event_with_as_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        number = self._parse_AS_value(attribute_value)
        self.assertEqual(pattern, f"[autonomous-system:number = '{number}']")

    def test_event_with_as_observable_attribute(self):
        event = get_event_with_as_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        object_ref = object_refs[0]
        AS = observable[0]
        self.assertEqual(object_ref, grouping_refs[0])
        self.assertEqual(AS.id, object_ref)
        self.assertEqual(AS.type, 'autonomous-system')
        number = self._parse_AS_value(attribute_value)
        self.assertEqual(AS.number, number)

    def test_event_with_attachment_indicator_attribute(self):
        event = get_event_with_attachment_attribute()
        data = event['Event']['Attribute'][0]['data']
        attribute_value, pattern = self._run_indicator_tests(event)
        file_pattern = f"file:name = '{attribute_value}'"
        data_pattern = f"file:content_ref.payload_bin = '{data}'"
        self.assertEqual(pattern, f"[{file_pattern} AND {data_pattern}]")

    def test_event_with_attachment_observable_attribute(self):
        event = get_event_with_attachment_attribute()
        data = event['Event']['Attribute'][0]['data']
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        file_id, artifact_id = grouping_refs
        file_ref, artifact_ref = object_refs
        file_object, artifact_object = observable
        self.assertEqual(file_ref, file_id)
        self.assertEqual(file_object.id, file_ref)
        self.assertEqual(file_object.type, 'file')
        self.assertEqual(file_object.name, attribute_value)
        self.assertEqual(file_object.content_ref, artifact_id)
        self.assertEqual(artifact_ref, artifact_id)
        self.assertEqual(artifact_object.id, artifact_ref)
        self.assertEqual(artifact_object.type, 'artifact')
        self.assertEqual(artifact_object.payload_bin, data)

    def test_event_with_campaign_name_attribute(self):
        event = get_event_with_campaign_name_attribute()
        self._remove_attribute_ids_flag(event)
        orgc = event['Event']['Orgc']
        attribute = event['Event']['Attribute'][0]
        self.parser.parse_misp_event(event)
        stix_objects = self.parser.stix_objects
        self._check_spec_versions(stix_objects)
        identity, grouping, campaign = stix_objects
        identity_id = self._check_identity_features(
            identity,
            orgc,
            self._datetime_from_timestamp(event['Event']['timestamp'])
        )
        args = (
            grouping,
            event['Event'],
            identity_id
        )
        object_ref = self._check_grouping_features(*args)[0]
        self._check_attribute_campaign_features(
            campaign,
            attribute,
            identity_id,
            object_ref
        )
        self.assertEqual(campaign.name, attribute['value'])

    def test_event_with_custom_attributes(self):
        event = get_event_with_stix2_custom_attributes()
        orgc = event['Event']['Orgc']
        attributes = event['Event']['Attribute']
        self.parser.parse_misp_event(event)
        stix_objects = self.parser.stix_objects
        self._check_spec_versions(stix_objects)
        identity, grouping, *custom_objects = stix_objects
        identity_id = self._check_identity_features(
            identity,
            orgc,
            self._datetime_from_timestamp(event['Event']['timestamp'])
        )
        args = (
            grouping,
            event['Event'],
            identity_id
        )
        object_refs = self._check_grouping_features(*args)
        for attribute, custom_object, object_ref in zip(attributes, custom_objects, object_refs):
            self._run_custom_attribute_tests(attribute, custom_object, object_ref, identity_id)

    def test_event_with_domain_indicator_attribute(self):
        event = get_event_with_domain_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(pattern, f"[domain-name:value = '{attribute_value}']")

    def test_event_with_domain_observable_attribute(self):
        event = get_event_with_domain_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        object_ref = object_refs[0]
        domain = observable[0]
        self.assertEqual(object_ref, grouping_refs[0])
        self.assertEqual(domain.id, object_ref)
        self.assertEqual(domain.type, 'domain-name')
        self.assertEqual(domain.value, attribute_value)

    def test_event_with_domain_ip_indicator_attribute(self):
        event = get_event_with_domain_ip_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        domain, ip = attribute_value.split('|')
        domain_pattern = f"domain-name:value = '{domain}'"
        ip_pattern = f"domain-name:resolves_to_refs[*].value = '{ip}'"
        self.assertEqual(pattern, f'[{domain_pattern} AND {ip_pattern}]')

    def test_event_with_domain_ip_observable_attribute(self):
        event = get_event_with_domain_ip_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        domain_value, ip_value = attribute_value.split('|')
        domain_id, address_id = grouping_refs
        domain_ref, address_ref = object_refs
        domain, address = observable
        self.assertEqual(domain_ref, domain_id)
        self.assertEqual(domain.id, domain_ref)
        self.assertEqual(domain.type, 'domain-name')
        self.assertEqual(domain.value, domain_value)
        self.assertEqual(domain.resolves_to_refs, [address_id])
        self.assertEqual(address_ref, address_id)
        self.assertEqual(address.id, address_ref)
        self.assertEqual(address.type, 'ipv4-addr')
        self.assertEqual(address.value, ip_value)

    def test_event_with_email_attachment_indicator_attribute(self):
        event = get_event_with_email_attachment_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(pattern, f"[email-message:body_multipart[*].body_raw_ref.name = '{attribute_value}']")

    def test_event_with_email_attachment_observable_attribute(self):
        event = get_event_with_email_attachment_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        email_id, file_id = grouping_refs
        email_ref, file_ref = object_refs
        email, file = observable
        self.assertEqual(email_ref, email_id)
        self.assertEqual(email.id, email_ref)
        self.assertEqual(email.type, 'email-message')
        self.assertEqual(email.is_multipart, True)
        body = email.body_multipart[0]
        self.assertEqual(body.content_disposition, f"attachment; filename='{attribute_value}'")
        self.assertEqual(body.body_raw_ref, file_id)
        self.assertEqual(file_ref, file_id)
        self.assertEqual(file.id, file_ref)
        self.assertEqual(file.name, attribute_value)

    def test_event_with_email_body_indicator_attribute(self):
        event = get_event_with_email_body_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(
            pattern,
            f"[email-message:body = '{attribute_value}']"
        )

    def test_event_with_email_body_observable_attribute(self):
        event = get_event_with_email_body_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        object_ref = object_refs[0]
        message = observable[0]
        self.assertEqual(object_ref, grouping_refs[0])
        self.assertEqual(message.id, object_ref)
        self.assertEqual(message.type, 'email-message')
        self.assertEqual(message.is_multipart, False)
        self.assertEqual(message.body, attribute_value)

    def test_event_with_email_destination_indicator_attribute(self):
        event = get_event_with_email_destination_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(pattern, f"[email-message:to_refs[*].value = '{attribute_value}']")

    def test_event_with_email_destination_observable_attribute(self):
        event = get_event_with_email_destination_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        message_id, address_id = grouping_refs
        message_ref, address_ref = object_refs
        message, address = observable
        self.assertEqual(message_ref, message_id)
        self.assertEqual(message.id, message_ref)
        self.assertEqual(message.type, 'email-message')
        self.assertEqual(message.is_multipart, False)
        self.assertEqual(message.to_refs, [address_id])
        self.assertEqual(address_ref, address_id)
        self.assertEqual(address.id, address_ref)
        self.assertEqual(address.type, 'email-addr')
        self.assertEqual(address.value, attribute_value)

    def test_event_with_email_header_indicator_attribute(self):
        event = get_event_with_email_header_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(pattern, f"[email-message:received_lines = '{attribute_value}']")

    def test_event_with_email_header_observable_attribute(self):
        event = get_event_with_email_header_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        object_ref = object_refs[0]
        message = observable[0]
        self.assertEqual(object_ref, grouping_refs[0])
        self.assertEqual(message.id, object_ref)
        self.assertEqual(message.type, 'email-message')
        self.assertEqual(message.is_multipart, False)
        self.assertEqual(message.received_lines, [attribute_value])

    def test_event_with_email_indicator_attribute(self):
        event = get_event_with_email_address_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(pattern, f"[email-addr:value = '{attribute_value}']")

    def test_event_with_email_message_id_indicator_attribute(self):
        event = get_event_with_email_message_id_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(pattern, f"[email-message:message_id = '{attribute_value}']")

    def test_event_with_email_message_id_observable_attribute(self):
        event = get_event_with_email_message_id_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        object_ref = object_refs[0]
        message = observable[0]
        self.assertEqual(object_ref, grouping_refs[0])
        self.assertEqual(message.id, object_ref)
        self.assertEqual(message.type, 'email-message')
        self.assertEqual(message.is_multipart, False)
        self.assertEqual(message.message_id, attribute_value)

    def test_event_with_email_observable_attribute(self):
        event = get_event_with_email_address_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        object_ref = object_refs[0]
        address = observable[0]
        self.assertEqual(object_ref, grouping_refs[0])
        self.assertEqual(address.id, object_ref)
        self.assertEqual(address.type, 'email-addr')
        self.assertEqual(address.value, attribute_value)

    def test_event_with_email_reply_to_indicator_attribute(self):
        event = get_event_with_email_reply_to_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(
            pattern,
            f"[email-message:additional_header_fields.reply_to = '{attribute_value}']"
        )

    def test_event_with_email_reply_to_observable_attribute(self):
        event = get_event_with_email_reply_to_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        object_ref = object_refs[0]
        message = observable[0]
        self.assertEqual(object_ref, grouping_refs[0])
        self.assertEqual(message.id, object_ref)
        self.assertEqual(message.type, 'email-message')
        self.assertEqual(message.is_multipart, False)
        self.assertEqual(message.additional_header_fields['Reply-To'][0], attribute_value)

    def test_event_with_email_source_indicator_attribute(self):
        event = get_event_with_email_source_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(pattern, f"[email-message:from_ref.value = '{attribute_value}']")

    def test_event_with_email_source_observable_attribute(self):
        event = get_event_with_email_source_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        message_id, address_id = grouping_refs
        message_ref, address_ref = object_refs
        message, address = observable
        self.assertEqual(message_ref, message_id)
        self.assertEqual(message.id, message_ref)
        self.assertEqual(message.type, 'email-message')
        self.assertEqual(message.is_multipart, False)
        self.assertEqual(message.from_ref, address_id)
        self.assertEqual(address_ref, address_id)
        self.assertEqual(address.id, address_ref)
        self.assertEqual(address.type, 'email-addr')
        self.assertEqual(address.value, attribute_value)

    def test_event_with_email_subject_indicator_attribute(self):
        event = get_event_with_email_subject_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(pattern, f"[email-message:subject = '{attribute_value}']")

    def test_event_with_email_subject_observable_attribute(self):
        event = get_event_with_email_subject_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        object_ref = object_refs[0]
        message = observable[0]
        self.assertEqual(object_ref, grouping_refs[0])
        self.assertEqual(message.id, object_ref)
        self.assertEqual(message.type, 'email-message')
        self.assertEqual(message.is_multipart, False)
        self.assertEqual(message.subject, attribute_value)

    def test_event_with_email_x_mailer_indicator_attribute(self):
        event = get_event_with_email_x_mailer_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(
            pattern,
            f"[email-message:additional_header_fields.x_mailer = '{attribute_value}']"
        )

    def test_event_with_email_x_mailer_observable_attribute(self):
        event = get_event_with_email_x_mailer_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        object_ref = object_refs[0]
        message = observable[0]
        self.assertEqual(object_ref, grouping_refs[0])
        self.assertEqual(message.id, object_ref)
        self.assertEqual(message.type, 'email-message')
        self.assertEqual(message.is_multipart, False)
        self.assertEqual(message.additional_header_fields['X-Mailer'], attribute_value)

    def test_event_with_filename_indicator_attribute(self):
        event = get_event_with_filename_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(pattern, f"[file:name = '{attribute_value}']")

    def test_event_with_filename_observable_attribute(self):
        event = get_event_with_filename_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        object_ref = object_refs[0]
        file = observable[0]
        self.assertEqual(object_ref, grouping_refs[0])
        self.assertEqual(file.id, object_ref)
        self.assertEqual(file.type, 'file')
        self.assertEqual(file.name, attribute_value)

    def test_event_with_hash_composite_indicator_attributes(self):
        event = get_event_with_hash_composite_attributes(
            ('md5', 'sha1', 'sha512/256', 'sha3-256'),
            (
                'filename1|b2a5abfeef9e36964281a31e17b57c97',
                'filename2|2920d5e6c579fce772e5506caf03af65579088bd',
                'filename3|82333533f7f7cb4123bceee76358b36d4110e03c2219b80dced5a4d63424cc93',
                'filename4|39725234628358bcce613d1d1c07c2c3d2d106e3a6ac192016b46e5dddcd03f4'
            ),
            (
                '91ae0a21-c7ae-4c7f-b84b-b84a7ce53d1f',
                '518b4bcb-a86b-4783-9457-391d548b605b',
                '34cb1a7c-55ec-412a-8684-ba4a88d83a45',
                '94a2b00f-bec3-4f8a-bea4-e4ccf0de776f'
            )
        )
        attribute_values, patterns = self._run_indicators_tests(event)
        hash_types = ('MD5', 'SHA1', 'SHA256', 'SHA3256')
        for attribute_value, pattern, hash_type in zip(attribute_values, patterns, hash_types):
            filename, hash_value = attribute_value.split('|')
            filename_pattern = f"file:name = '{filename}'"
            hash_pattern = f"file:hashes.{hash_type} = '{hash_value}'"
            self.assertEqual(pattern, f"[{filename_pattern} AND {hash_pattern}]")

    def test_event_with_hash_composite_observable_attributes(self):
        event = get_event_with_hash_composite_attributes(
            ('md5', 'sha1', 'sha512/256', 'sha3-256'),
            (
                'filename1|b2a5abfeef9e36964281a31e17b57c97',
                'filename2|2920d5e6c579fce772e5506caf03af65579088bd',
                'filename3|82333533f7f7cb4123bceee76358b36d4110e03c2219b80dced5a4d63424cc93',
                'filename4|39725234628358bcce613d1d1c07c2c3d2d106e3a6ac192016b46e5dddcd03f4'
            ),
            (
                '91ae0a21-c7ae-4c7f-b84b-b84a7ce53d1f',
                '518b4bcb-a86b-4783-9457-391d548b605b',
                '34cb1a7c-55ec-412a-8684-ba4a88d83a45',
                '94a2b00f-bec3-4f8a-bea4-e4ccf0de776f'
            )
        )
        values, grouping_refs, object_refs, observables = self._run_observables_tests(event)
        for grouping_ref, object_ref, observable in zip(grouping_refs, object_refs, observables):
            self.assertEqual(grouping_ref, object_ref)
            self.assertEqual(observable.id, object_ref)
            self.assertEqual(observable.type, 'file')
        hash_types = ('MD5', 'SHA-1', 'SHA-256', 'SHA3-256')
        for value, observable, hash_type in zip(values, observables, hash_types):
            filename, hash_value = value.split('|')
            self.assertEqual(observable.name, filename)
            self.assertEqual(observable.hashes[hash_type], hash_value)

    def test_event_with_hash_indicator_attributes(self):
        event = get_event_with_hash_attributes(
            ('md5', 'sha1', 'sha512/256', 'sha3-256'),
            (
                'b2a5abfeef9e36964281a31e17b57c97',
                '2920d5e6c579fce772e5506caf03af65579088bd',
                '82333533f7f7cb4123bceee76358b36d4110e03c2219b80dced5a4d63424cc93',
                '39725234628358bcce613d1d1c07c2c3d2d106e3a6ac192016b46e5dddcd03f4'
            ),
            (
                '91ae0a21-c7ae-4c7f-b84b-b84a7ce53d1f',
                '518b4bcb-a86b-4783-9457-391d548b605b',
                '34cb1a7c-55ec-412a-8684-ba4a88d83a45',
                '94a2b00f-bec3-4f8a-bea4-e4ccf0de776f'
            )
        )
        attribute_values, patterns = self._run_indicators_tests(event)
        md5, sha1, sha2, sha3 = attribute_values
        md5_pattern, sha1_pattern, sha2_pattern, sha3_pattern = patterns
        self.assertEqual(md5_pattern, f"[file:hashes.MD5 = '{md5}']")
        self.assertEqual(sha1_pattern, f"[file:hashes.SHA1 = '{sha1}']")
        self.assertEqual(sha2_pattern, f"[file:hashes.SHA256 = '{sha2}']")
        self.assertEqual(sha3_pattern, f"[file:hashes.SHA3256 = '{sha3}']")

    def test_event_with_hash_observable_attributes(self):
        event = get_event_with_hash_attributes(
            ('md5', 'sha1', 'sha512/256', 'sha3-256'),
            (
                'b2a5abfeef9e36964281a31e17b57c97',
                '2920d5e6c579fce772e5506caf03af65579088bd',
                '82333533f7f7cb4123bceee76358b36d4110e03c2219b80dced5a4d63424cc93',
                '39725234628358bcce613d1d1c07c2c3d2d106e3a6ac192016b46e5dddcd03f4'
            ),
            (
                '91ae0a21-c7ae-4c7f-b84b-b84a7ce53d1f',
                '518b4bcb-a86b-4783-9457-391d548b605b',
                '34cb1a7c-55ec-412a-8684-ba4a88d83a45',
                '94a2b00f-bec3-4f8a-bea4-e4ccf0de776f'
            )
        )
        values, grouping_refs, object_refs, observables = self._run_observables_tests(event)
        for grouping_ref, object_ref, observable in zip(grouping_refs, object_refs, observables):
            self.assertEqual(grouping_ref, object_ref)
            self.assertEqual(observable.id, object_ref)
            self.assertEqual(observable.type, 'file')
        md5, sha1, sha2, sha3 = values
        md5_object, sha1_object, sha2_object, sha3_object = observables
        self.assertEqual(md5_object.hashes['MD5'], md5)
        self.assertEqual(sha1_object.hashes['SHA-1'], sha1)
        self.assertEqual(sha2_object.hashes['SHA-256'], sha2)
        self.assertEqual(sha3_object.hashes['SHA3-256'], sha3)

    def test_event_with_hostname_indicator_attribute(self):
        event = get_event_with_hostname_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(pattern, f"[domain-name:value = '{attribute_value}']")

    def test_event_with_hostname_observable_attribute(self):
        event = get_event_with_hostname_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        object_ref = object_refs[0]
        domain = observable[0]
        self.assertEqual(object_ref, grouping_refs[0])
        self.assertEqual(domain.id, object_ref)
        self.assertEqual(domain.type, 'domain-name')
        self.assertEqual(domain.value, attribute_value)

    def test_event_with_hostname_port_indicator_attribute(self):
        event = get_event_with_hostname_port_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        hostname, port = attribute_value.split('|')
        hostname_pattern = f"domain-name:value = '{hostname}'"
        port_pattern = f"network-traffic:dst_port = '{port}'"
        self.assertEqual(pattern, f"[{hostname_pattern} AND {port_pattern}]")

    def test_event_with_hostname_port_observable_attribute(self):
        event = get_event_with_hostname_port_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        hostname, port = attribute_value.split('|')
        domain_id, network_traffic_id = grouping_refs
        hostname_ref, network_traffic_ref = object_refs
        domain, network_traffic = observable
        self.assertEqual(hostname_ref, domain_id)
        self.assertEqual(domain.id, hostname_ref)
        self.assertEqual(domain.type, 'domain-name')
        self.assertEqual(domain.value, hostname)
        self.assertEqual(network_traffic.id, network_traffic_id)
        self.assertEqual(network_traffic.type, 'network-traffic')
        self.assertEqual(network_traffic.dst_port, int(port))
        self.assertEqual(network_traffic.dst_ref, domain_id)

    def test_event_with_http_indicator_attributes(self):
        event = get_event_with_http_attributes()
        attribute_values, patterns = self._run_indicators_tests(event)
        http_method, user_agent = attribute_values
        http_method_pattern, user_agent_pattern = patterns
        prefix = f"network-traffic:extensions.'http-request-ext'"
        self.assertEqual(
            http_method_pattern,
            f"[{prefix}.request_method = '{http_method}']"
        )
        self.assertEqual(
            user_agent_pattern,
            f"[{prefix}.request_header.'User-Agent' = '{user_agent}']"
        )

    def test_event_with_ip_indicator_attributes(self):
        event = get_event_with_ip_attributes()
        attribute_values, patterns = self._run_indicators_tests(event)
        src, dst = attribute_values
        src_pattern, dst_pattern = patterns
        src_type_pattern = "network-traffic:src_ref.type = 'ipv4-addr'"
        src_value_pattern = f"network-traffic:src_ref.value = '{src}'"
        self.assertEqual(src_pattern, f"[{src_type_pattern} AND {src_value_pattern}]")
        dst_type_pattern = "network-traffic:dst_ref.type = 'ipv4-addr'"
        dst_value_pattern = f"network-traffic:dst_ref.value = '{dst}'"
        self.assertEqual(dst_pattern, f"[{dst_type_pattern} AND {dst_value_pattern}]")

    def test_event_with_ip_observable_attributes(self):
        event = get_event_with_ip_attributes()
        values, grouping_refs, object_refs, observables = self._run_observables_tests(
            event,
            index=3
        )
        for grouping_ref, observable in zip(grouping_refs, observables):
            self.assertEqual(grouping_ref, observable.id)
        src, dst = values
        src_network_id, src_address_id, dst_network_id, dst_address_id = grouping_refs
        src_observable_id, dst_observable_id = object_refs
        src_network, src_address, dst_network, dst_address = observables
        self.assertEqual(src_network_id, src_observable_id)
        self.assertEqual(src_network.id, src_network_id)
        self.assertEqual(src_network.type, 'network-traffic')
        self.assertEqual(src_network.src_ref, src_address_id)
        self.assertEqual(src_address.id, src_address_id)
        self.assertEqual(src_address.value, src)
        self.assertEqual(dst_network_id, dst_observable_id)
        self.assertEqual(dst_network.id, dst_network_id)
        self.assertEqual(dst_network.type, 'network-traffic')
        self.assertEqual(dst_network.dst_ref, dst_address_id)
        self.assertEqual(dst_address.id, dst_address_id)
        self.assertEqual(dst_address.value, dst)

    def test_event_with_ip_port_indicator_attributes(self):
        event = get_event_with_ip_port_attributes()
        attribute_values, patterns = self._run_indicators_tests(event)
        src, dst = attribute_values
        src_ip_value, src_port_value = src.split('|')
        dst_ip_value, dst_port_value = dst.split('|')
        src_pattern, dst_pattern = patterns
        src_type_pattern = "network-traffic:src_ref.type = 'ipv4-addr'"
        src_value_pattern = f"network-traffic:src_ref.value = '{src_ip_value}'"
        src_port_pattern = f"network-traffic:src_port = '{src_port_value}'"
        self.assertEqual(
            src_pattern,
            f"[{src_type_pattern} AND {src_value_pattern} AND {src_port_pattern}]"
        )
        dst_type_pattern = "network-traffic:dst_ref.type = 'ipv4-addr'"
        dst_value_pattern = f"network-traffic:dst_ref.value = '{dst_ip_value}'"
        dst_port_pattern = f"network-traffic:dst_port = '{dst_port_value}'"
        self.assertEqual(
            dst_pattern,
            f"[{dst_type_pattern} AND {dst_value_pattern} AND {dst_port_pattern}]"
        )

    def test_event_with_ip_port_observable_attributes(self):
        event = get_event_with_ip_port_attributes()
        values, grouping_refs, object_refs, observables = self._run_observables_tests(
            event,
            index=3
        )
        for grouping_ref, observable in zip(grouping_refs, observables):
            self.assertEqual(grouping_ref, observable.id)
        src, dst = values
        src_network_id, src_address_id, dst_network_id, dst_address_id = grouping_refs
        src_observable_id, dst_observable_id = object_refs
        src_network, src_address, dst_network, dst_address = observables
        src_ip_value, src_port_value = src.split('|')
        self.assertEqual(src_network_id, src_observable_id)
        self.assertEqual(src_network.id, src_network_id)
        self.assertEqual(src_network.type, 'network-traffic')
        self.assertEqual(src_network.src_port, int(src_port_value))
        self.assertEqual(src_network.src_ref, src_address_id)
        self.assertEqual(src_address.id, src_address_id)
        self.assertEqual(src_address.value, src_ip_value)
        dst_ip_value, dst_port_value = dst.split('|')
        self.assertEqual(dst_network_id, dst_observable_id)
        self.assertEqual(dst_network.id, dst_network_id)
        self.assertEqual(dst_network.type, 'network-traffic')
        self.assertEqual(dst_network.dst_port, int(dst_port_value))
        self.assertEqual(dst_network.dst_ref, dst_address_id)
        self.assertEqual(dst_address.id, dst_address_id)
        self.assertEqual(dst_address.value, dst_ip_value)

    def test_event_with_mac_address_indicator_attribute(self):
        event = get_event_with_mac_address_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(pattern, f"[mac-addr:value = '{attribute_value}']")

    def test_event_with_mac_address_observable_attribute(self):
        event = get_event_with_mac_address_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        object_ref = object_refs[0]
        mac_address = observable[0]
        self.assertEqual(object_ref, grouping_refs[0])
        self.assertEqual(mac_address.id, object_ref)
        self.assertEqual(mac_address.type, 'mac-addr')
        self.assertEqual(mac_address.value, attribute_value)

    def test_event_with_malware_sample_indicator_attribute(self):
        event = get_event_with_malware_sample_attribute()
        data = event['Event']['Attribute'][0]['data']
        attribute_value, pattern = self._run_indicator_tests(event)
        filename, hash_value = attribute_value.split('|')
        file_pattern = f"file:name = '{filename}'"
        hash_pattern = f"file:hashes.MD5 = '{hash_value}'"
        data_pattern = f"file:content_ref.payload_bin = '{data}'"
        self.assertEqual(pattern, f"[{file_pattern} AND {hash_pattern} AND {data_pattern}]")

    def test_event_with_malware_sample_observable_attribute(self):
        event = get_event_with_malware_sample_attribute()
        data = event['Event']['Attribute'][0]['data']
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        file_id, artifact_id = grouping_refs
        file_ref, artifact_ref = object_refs
        file_object, artifact_object = observable
        filename, hash_value = attribute_value.split('|')
        self.assertEqual(file_ref, file_id)
        self.assertEqual(file_object.id, file_ref)
        self.assertEqual(file_object.type, 'file')
        self.assertEqual(file_object.name, filename)
        self.assertEqual(file_object.hashes['MD5'], hash_value)
        self.assertEqual(file_object.content_ref, artifact_id)
        self.assertEqual(artifact_ref, artifact_id)
        self.assertEqual(artifact_object.id, artifact_ref)
        self.assertEqual(artifact_object.type, 'artifact')
        self.assertEqual(artifact_object.payload_bin, data)

    def test_event_with_mutex_indicator_attribute(self):
        event = get_event_with_mutex_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(pattern, f"[mutex:name = '{attribute_value}']")

    def test_event_with_mutex_observable_attribute(self):
        event = get_event_with_mutex_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        object_ref = object_refs[0]
        mutex = observable[0]
        self.assertEqual(object_ref, grouping_refs[0])
        self.assertEqual(mutex.id, object_ref)
        self.assertEqual(mutex.type, 'mutex')
        self.assertEqual(mutex.name, attribute_value)

    def test_event_with_port_indicator_attribute(self):
        event = get_event_with_port_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(pattern, f"[network-traffic:dst_port = '{attribute_value}']")

    def test_event_with_regkey_indicator_attribute(self):
        event = get_event_with_regkey_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(
            pattern.replace('\\\\', '\\'),
            f"[windows-registry-key:key = '{attribute_value.strip()}']"
        )

    def test_event_with_regkey_observable_attribute(self):
        event = get_event_with_regkey_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        object_ref = object_refs[0]
        registry_key = observable[0]
        self.assertEqual(object_ref, grouping_refs[0])
        self.assertEqual(registry_key.id, object_ref)
        self.assertEqual(registry_key.type, 'windows-registry-key')
        self.assertEqual(registry_key.key, attribute_value.strip())

    def test_event_with_regkey_value_indicator_attribute(self):
        event = get_event_with_regkey_value_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        key, value = attribute_value.split('|')
        key_pattern = f"windows-registry-key:key = '{key.strip()}'"
        value_pattern = f"windows-registry-key:values.data = '{value.strip()}'"
        self.assertEqual(
            pattern.replace('\\\\', '\\'),
            f"[{key_pattern} AND {value_pattern}]"
        )

    def test_event_with_regkey_value_observable_attribute(self):
        event = get_event_with_regkey_value_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        key, value = attribute_value.split('|')
        object_ref = object_refs[0]
        registry_key = observable[0]
        self.assertEqual(object_ref, grouping_refs[0])
        self.assertEqual(registry_key.id, object_ref)
        self.assertEqual(registry_key.type, 'windows-registry-key')
        self.assertEqual(registry_key.key, key.strip())
        self.assertEqual(registry_key['values'][0].data, value.strip())

    def test_event_with_size_in_bytes_indicator_attribute(self):
        event = get_event_with_size_in_bytes_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(pattern, f"[file:size = '{attribute_value}']")

    def test_event_with_url_indicator_attribute(self):
        event = get_event_with_url_attribute()
        attribute_value, pattern = self._run_indicator_tests(event)
        self.assertEqual(pattern, f"[url:value = '{attribute_value}']")

    def test_event_with_url_observable_attribute(self):
        event = get_event_with_url_attribute()
        attribute_value, grouping_refs, object_refs, observable = self._run_observable_tests(event)
        object_ref = object_refs[0]
        url = observable[0]
        self.assertEqual(object_ref, grouping_refs[0])
        self.assertEqual(url.id, object_ref)
        self.assertEqual(url.type, 'url')
        self.assertEqual(url.value, attribute_value)

    def test_event_with_vulnerability_attribute(self):
        event = get_event_with_vulnerability_attribute()
        self._add_attribute_ids_flag(event)
        orgc = event['Event']['Orgc']
        attribute = event['Event']['Attribute'][0]
        self.parser.parse_misp_event(event)
        stix_objects = self.parser.stix_objects
        self._check_spec_versions(stix_objects)
        identity, grouping, vulnerability = stix_objects
        identity_id = self._check_identity_features(
            identity,
            orgc,
            self._datetime_from_timestamp(event['Event']['timestamp'])
        )
        args = (
            grouping,
            event['Event'],
            identity_id
        )
        object_ref = self._check_grouping_features(*args)[0]
        self._check_attribute_vulnerability_features(
            vulnerability,
            attribute,
            identity_id,
            object_ref
        )
        self.assertEqual(vulnerability.name, attribute['value'])
        self._check_external_reference(
            vulnerability.external_references[0],
            'cve',
            attribute['value']
        )

    def test_event_with_x509_fingerprint_indicator_attributes(self):
        event = get_event_with_x509_fingerprint_attributes()
        attribute_values, patterns = self._run_indicators_tests(event)
        md5, sha1, sha256 = attribute_values
        md5_pattern, sha1_pattern, sha256_pattern = patterns
        self.assertEqual(md5_pattern, f"[x509-certificate:hashes.MD5 = '{md5}']")
        self.assertEqual(sha1_pattern, f"[x509-certificate:hashes.SHA1 = '{sha1}']")
        self.assertEqual(sha256_pattern, f"[x509-certificate:hashes.SHA256 = '{sha256}']")

    def test_event_with_x509_fingerprint_observable_attributes(self):
        event = get_event_with_x509_fingerprint_attributes()
        values, grouping_refs, object_refs, observables = self._run_observables_tests(event)
        for grouping_ref, object_ref, observable in zip(grouping_refs, object_refs, observables):
            self.assertEqual(grouping_ref, object_ref)
            self.assertEqual(observable.id, object_ref)
            self.assertEqual(observable.type, 'x509-certificate')
        md5, sha1, sha256 = values
        md5_object, sha1_object, sha256_object = observables
        self.assertEqual(md5_object.hashes['MD5'], md5)
        self.assertEqual(sha1_object.hashes['SHA-1'], sha1)
        self.assertEqual(sha256_object.hashes['SHA-256'], sha256)

    ################################################################################
    #                          MISP OBJECTS EXPORT TESTS.                          #
    ################################################################################

    def test_event_with_account_indicator_objects(self):
        event = get_event_with_account_objects()
        misp_objects, patterns = self._run_indicators_from_objects_tests(event)
        facebook_object, twitter_object = misp_objects
        facebook_pattern, twitter_pattern = patterns
        account_id, account_name, link = (attribute['value'] for attribute in facebook_object['Attribute'])
        account_type, user_id, account_login, _link = facebook_pattern[1:-1].split(' AND ')
        self.assertEqual(account_type, f"user-account:account_type = 'facebook'")
        self.assertEqual(user_id, f"user-account:user_id = '{account_id}'")
        self.assertEqual(account_login, f"user-account:account_login = '{account_name}'")
        self.assertEqual(_link, f"user-account:x_misp_link = '{link}'")
        _id, name, displayed_name, followers = (attribute['value'] for attribute in twitter_object['Attribute'])
        account_type, display_name, user_id, account_login, _followers = twitter_pattern[1:-1].split(' AND ')
        self.assertEqual(account_type, f"user-account:account_type = 'twitter'")
        self.assertEqual(display_name, f"user-account:display_name = '{displayed_name}'")
        self.assertEqual(user_id, f"user-account:user_id = '{_id}'")
        self.assertEqual(account_login, f"user-account:account_login = '{name}'")
        self.assertEqual(_followers, f"user-account:x_misp_followers = '{followers}'")

    def test_event_with_account_observable_objects(self):
        event = get_event_with_account_objects()
        misp_objects, grouping_refs, object_refs, observables = self._run_observables_from_objects_tests(event)
        for grouping_ref, object_ref, observable in zip(grouping_refs, object_refs, observables):
            for grp_ref, obj_ref, obs in zip(grouping_ref, object_ref, observable):
                self.assertTrue(grp_ref == obj_ref == obs.id)
        facebook_object, twitter_object = misp_objects
        facebook, twitter = observables
        account_id, account_name, link = (attribute['value'] for attribute in facebook_object['Attribute'])
        facebook = facebook[0]
        self.assertEqual(facebook.type, 'user-account')
        self.assertEqual(facebook.account_type, 'facebook')
        self.assertEqual(facebook.user_id, account_id)
        self.assertEqual(facebook.account_login, account_name)
        self.assertEqual(facebook.x_misp_link, link)
        _id, name, displayed_name, followers = (attribute['value'] for attribute in twitter_object['Attribute'])
        twitter = twitter[0]
        self.assertEqual(twitter.type, 'user-account')
        self.assertEqual(twitter.account_type, 'twitter')
        self.assertEqual(twitter.user_id, _id)
        self.assertEqual(twitter.account_login, name)
        self.assertEqual(twitter.display_name, displayed_name)
        self.assertEqual(twitter.x_misp_followers, followers)

    def test_event_with_asn_indicator_object(self):
        event = get_event_with_asn_object()
        attributes, pattern = self._run_indicator_from_object_tests(event)
        asn, description, subnet1, subnet2 = (attribute['value'] for attribute in attributes)
        asn_pattern, description_pattern, subnet1_pattern, subnet2_pattern = pattern[1:-1].split(' AND ')
        self.assertEqual(asn_pattern, f"autonomous-system:number = '{int(asn[2:])}'")
        self.assertEqual(description_pattern, f"autonomous-system:name = '{description}'")
        self.assertEqual(
            subnet1_pattern,
            f"autonomous-system:x_misp_subnet_announced = '{subnet1}'"
        )
        self.assertEqual(
            subnet2_pattern,
            f"autonomous-system:x_misp_subnet_announced = '{subnet2}'"
        )

    def test_event_with_asn_observable_object(self):
        event = get_event_with_asn_object()
        attributes, grouping_refs, object_refs, observable = self._run_observable_from_object_tests(event)
        asn, description, subnet1, subnet2 = (attribute['value'] for attribute in attributes)
        object_ref = object_refs[0]
        autonomous_system = observable[0]
        self.assertEqual(object_ref, grouping_refs[0])
        self.assertEqual(autonomous_system.id, object_ref)
        self.assertEqual(autonomous_system.type, 'autonomous-system')
        self.assertEqual(autonomous_system.number, int(asn[2:]))
        self.assertEqual(autonomous_system.name, description)
        self.assertEqual(
            autonomous_system.x_misp_subnet_announced,
            [subnet1, subnet2]
        )

    def test_event_with_attack_pattern_object(self):
        event = get_event_with_attack_pattern_object()
        orgc = event['Event']['Orgc']
        misp_object = deepcopy(event['Event']['Object'][0])
        self.parser.parse_misp_event(event)
        stix_objects = self.parser.stix_objects
        self._check_spec_versions(stix_objects)
        identity, grouping, attack_pattern = stix_objects
        identity_id = self._check_identity_features(
            identity,
            orgc,
            self._datetime_from_timestamp(event['Event']['timestamp'])
        )
        args = (grouping, event['Event'], identity_id)
        object_ref = self._check_grouping_features(*args)[0]
        self.assertEqual(attack_pattern.type, 'attack-pattern')
        self.assertEqual(attack_pattern.id, object_ref)
        self.assertEqual(attack_pattern.created_by_ref, identity_id)
        self._check_killchain(attack_pattern.kill_chain_phases[0], misp_object['meta-category'])
        self._check_object_labels(misp_object, attack_pattern.labels)
        timestamp = self._datetime_from_timestamp(misp_object['timestamp'])
        self.assertEqual(attack_pattern.created, timestamp)
        self.assertEqual(attack_pattern.modified, timestamp)
        id, name, summary = (attribute['value'] for attribute in misp_object['Attribute'])
        self.assertEqual(attack_pattern.name, name)
        self.assertEqual(attack_pattern.description, summary)
        self._check_external_reference(
            attack_pattern.external_references[0],
            'capec',
            f'CAPEC-{id}'
        )

    def test_event_with_course_of_action_object(self):
        event = get_event_with_course_of_action_object()
        orgc = event['Event']['Orgc']
        misp_object = deepcopy(event['Event']['Object'][0])
        self.parser.parse_misp_event(event)
        stix_objects = self.parser.stix_objects
        self._check_spec_versions(stix_objects)
        identity, grouping, course_of_action = stix_objects
        identity_id = self._check_identity_features(
            identity,
            orgc,
            self._datetime_from_timestamp(event['Event']['timestamp'])
        )
        args = (grouping, event['Event'], identity_id)
        object_ref = self._check_grouping_features(*args)[0]
        self.assertEqual(course_of_action.type, 'course-of-action')
        self.assertEqual(course_of_action.id, object_ref)
        self.assertEqual(course_of_action.created_by_ref, identity_id)
        self._check_object_labels(misp_object, course_of_action.labels)
        timestamp = self._datetime_from_timestamp(misp_object['timestamp'])
        self.assertEqual(course_of_action.created, timestamp)
        self.assertEqual(course_of_action.modified, timestamp)
        self.assertEqual(course_of_action.name, misp_object['Attribute'][0]['value'])
        for attribute in misp_object['Attribute'][1:]:
            self.assertEqual(
                getattr(
                    course_of_action,
                    f"x_misp_{attribute['object_relation']}"
                ),
                attribute['value']
            )

    def test_event_with_credential_indicator_object(self):
        event = get_event_with_credential_object()
        attributes, pattern = self._run_indicator_from_object_tests(event)
        text, username, password, *attributes = ((attribute['object_relation'], attribute['value']) for attribute in attributes)
        attributes.insert(0, text)
        username_pattern, password_pattern, *pattern = pattern[1:-1].split(' AND ')
        self.assertEqual(username_pattern, f"user-account:user_id = '{username[1]}'")
        self.assertEqual(password_pattern, f"user-account:credential = '{password[1]}'")
        for pattern_part, attribute in zip(pattern, attributes):
            feature, value = attribute
            self.assertEqual(pattern_part, f"user-account:x_misp_{feature} = '{value}'")

    def test_event_with_credential_observable_object(self):
        event = get_event_with_credential_object()
        attributes, grouping_refs, object_refs, observable = self._run_observable_from_object_tests(event)
        text, username, password, *attributes = ((attribute['object_relation'], attribute['value']) for attribute in attributes)
        attributes.insert(0, text)
        object_ref = object_refs[0]
        user_account = observable[0]
        self.assertEqual(object_ref, grouping_refs[0])
        self.assertEqual(user_account.id, object_ref)
        self.assertEqual(user_account.type, 'user-account')
        self.assertEqual(user_account.user_id, username[1])
        self.assertEqual(user_account.credential, password[1])
        for feature, value in attributes:
            self.assertEqual(getattr(user_account, f'x_misp_{feature}'), value)

    def test_event_with_custom_objects(self):
        event = get_event_with_custom_objects()
        orgc = event['Event']['Orgc']
        misp_objects = deepcopy(event['Event']['Object'])
        self.parser.parse_misp_event(event)
        stix_objects = self.parser.stix_objects
        self._check_spec_versions(stix_objects)
        identity, grouping, *custom_objects = stix_objects
        identity_id = self._check_identity_features(
            identity,
            orgc,
            self._datetime_from_timestamp(event['Event']['timestamp'])
        )
        args = (
            grouping,
            event['Event'],
            identity_id
        )
        object_refs = self._check_grouping_features(*args)
        for misp_object, custom_object, object_ref in zip(misp_objects, custom_objects, object_refs):
            self._run_custom_object_tests(misp_object, custom_object, object_ref, identity_id)

    def test_event_with_domain_ip_indicator_object(self):
        event = get_event_with_domain_ip_object()
        attributes, pattern = self._run_indicator_from_object_tests(event)
        domain, ip = (attribute['value'] for attribute in attributes)
        domain_pattern, ip_pattern = pattern[1:-1].split(' AND ')
        self.assertEqual(domain_pattern, f"domain-name:value = '{domain}'")
        self.assertEqual(ip_pattern, f"domain-name:resolves_to_refs[*].value = '{ip}'")

    def test_event_with_domain_ip_observable_object(self):
        event = get_event_with_domain_ip_object()
        attributes, grouping_refs, object_refs, observable = self._run_observable_from_object_tests(event)
        domain, ip = (attribute['value'] for attribute in attributes)
        domain_ref, address_ref = object_refs
        domain_object, address_object = observable
        self.assertEqual(domain_ref, grouping_refs[0])
        self.assertEqual(address_ref, grouping_refs[1])
        self.assertEqual(domain_object.id, domain_ref)
        self.assertEqual(domain_object.type, 'domain-name')
        self.assertEqual(domain_object.value, domain)
        self.assertEqual(domain_object.resolves_to_refs, [address_ref])
        self.assertEqual(address_object.id, address_ref)
        self.assertEqual(address_object.value, ip)

    def test_event_with_email_indicator_object(self):
        event = get_event_with_email_object()
        attributes, pattern = self._run_indicator_from_object_tests(event)
        _from, _to, _cc1, _cc2, _reply_to, _subject, _attachment1, _attachment2, _x_mailer, _user_agent, _boundary = (attribute['value'] for attribute in attributes)
        cc1_, cc2_, from_, reply_to_, subject_, to_, x_mailer_, attachment1_, attachment2_, user_agent_, boundary_ = pattern[1:-1].split(' AND ')
        self.assertEqual(from_, f"email-message:from_ref.value = '{_from}'")
        self.assertEqual(to_, f"email-message:to_refs.value = '{_to}'")
        self.assertEqual(cc1_, f"email-message:cc_refs.value = '{_cc1}'")
        self.assertEqual(cc2_, f"email-message:cc_refs.value = '{_cc2}'")
        self.assertEqual(
            reply_to_,
            f"email-message:additional_header_fields.reply_to = '{_reply_to}'"
        )
        self.assertEqual(subject_, f"email-message:subject = '{_subject}'")
        self.assertEqual(
            attachment1_,
            f"email-message:body_multipart[0].body_raw_ref.name = '{_attachment1}'"
        )
        self.assertEqual(
            attachment2_,
            f"email-message:body_multipart[1].body_raw_ref.name = '{_attachment2}'"
        )
        self.assertEqual(
            x_mailer_,
            f"email-message:additional_header_fields.x_mailer = '{_x_mailer}'"
        )
        self.assertEqual(user_agent_, f"email-message:x_misp_user_agent = '{_user_agent}'")
        self.assertEqual(boundary_, f"email-message:x_misp_mime_boundary = '{_boundary}'")

    def test_event_with_email_observable_object(self):
        event = get_event_with_email_object()
        attributes, grouping_refs, object_refs, observables = self._run_observable_from_object_tests(event)
        _from, _to, _cc1, _cc2, _reply_to, _subject, _attachment1, _attachment2, _x_mailer, _user_agent, _boundary = (attribute['value'] for attribute in attributes)
        message, address1, address2, address3, address4, file1, file2 = observables
        for grouping_ref, object_ref in zip(grouping_refs, object_refs):
            self.assertEqual(grouping_ref, object_ref)
        message_ref, address1_ref, address2_ref, address3_ref, address4_ref, file1_ref, file2_ref = grouping_refs
        self.assertEqual(message.id, message_ref)
        self.assertEqual(message.type, 'email-message')
        self.assertEqual(message.is_multipart, True)
        self.assertEqual(message.subject, _subject)
        additional_header = message.additional_header_fields
        self.assertEqual(additional_header['Reply-To'], _reply_to)
        self.assertEqual(additional_header['X-Mailer'], _x_mailer)
        self.assertEqual(message.x_misp_mime_boundary, _boundary)
        self.assertEqual(message.x_misp_user_agent, _user_agent)
        self.assertEqual(message.from_ref, address1_ref)
        self.assertEqual(message.to_refs, [address2_ref])
        self.assertEqual(message.cc_refs, [address3_ref, address4_ref])
        body1, body2 = message.body_multipart
        self.assertEqual(body1['body_raw_ref'], file1_ref)
        self.assertEqual(body1['content_disposition'], f"attachment; filename='{_attachment1}'")
        self.assertEqual(body2['body_raw_ref'], file2_ref)
        self.assertEqual(body2['content_disposition'], f"attachment; filename='{_attachment2}'")
        self.assertEqual(address1.id, address1_ref)
        self.assertEqual(address1.type, 'email-addr')
        self.assertEqual(address1.value, _from)
        self.assertEqual(address2.id, address2_ref)
        self.assertEqual(address2.type, 'email-addr')
        self.assertEqual(address2.value, _to)
        self.assertEqual(address3.id, address3_ref)
        self.assertEqual(address3.type, 'email-addr')
        self.assertEqual(address3.value, _cc1)
        self.assertEqual(address4.id, address4_ref)
        self.assertEqual(address4.type, 'email-addr')
        self.assertEqual(address4.value, _cc2)
        self.assertEqual(file1.id, file1_ref)
        self.assertEqual(file1.type, 'file')
        self.assertEqual(file1.name, _attachment1)
        self.assertEqual(file2.id, file2_ref)
        self.assertEqual(file2.type, 'file')
        self.assertEqual(file2.name, _attachment2)

    def test_event_with_file_and_pe_indicator_objects(self):
        event = get_event_with_file_and_pe_objects()
        misp_objects, pattern = self._run_indicator_from_objects_tests(event)
        file, pe, section = misp_objects
        _filename, _md5, _sha1, _sha256, _size, _entropy = (attribute['value'] for attribute in file['Attribute'])
        pattern = pattern[1:-1].split(' AND ')
        md5_, sha1_, sha256_, name_, size_, entropy_ = pattern[:6]
        self.assertEqual(md5_, f"file:hashes.MD5 = '{_md5}'")
        self.assertEqual(sha1_, f"file:hashes.SHA1 = '{_sha1}'")
        self.assertEqual(sha256_, f"file:hashes.SHA256 = '{_sha256}'")
        self.assertEqual(name_, f"file:name = '{_filename}'")
        self.assertEqual(size_, f"file:size = '{_size}'")
        self.assertEqual(entropy_, f"file:x_misp_entropy = '{_entropy}'")
        _type, _compilation, _entrypoint, _original, _internal, _desc, _version, _lang, _prod_name, _prod_version, _company, _copyright, _sections, _imphash, _impfuzzy = (attribute['value'] for attribute in pe['Attribute'])
        imphash_, sections_, type_, entrypoint_, compilation_, original_, internal_, desc_, version_, lang_, prod_name_, prod_version_, company_, copyright_, impfuzzy_ = pattern[6:21]
        prefix = "file:extensions.'windows-pebinary-ext'"
        self.assertEqual(imphash_, f"{prefix}.imphash = '{_imphash}'")
        self.assertEqual(sections_, f"{prefix}.number_of_sections = '{_sections}'")
        self.assertEqual(type_, f"{prefix}.pe_type = '{_type}'")
        self.assertEqual(entrypoint_, f"{prefix}.optional_header.address_of_entry_point = '{_entrypoint}'")
        self.assertEqual(compilation_, f"{prefix}.x_misp_compilation_timestamp = '{_compilation}'")
        self.assertEqual(original_, f"{prefix}.x_misp_original_filename = '{_original}'")
        self.assertEqual(internal_, f"{prefix}.x_misp_internal_filename = '{_internal}'")
        self.assertEqual(desc_, f"{prefix}.x_misp_file_description = '{_desc}'")
        self.assertEqual(version_, f"{prefix}.x_misp_file_version = '{_version}'")
        self.assertEqual(lang_, f"{prefix}.x_misp_lang_id = '{_lang}'")
        self.assertEqual(prod_name_, f"{prefix}.x_misp_product_name = '{_prod_name}'")
        self.assertEqual(prod_version_, f"{prefix}.x_misp_product_version = '{_prod_version}'")
        self.assertEqual(company_, f"{prefix}.x_misp_company_name = '{_company}'")
        self.assertEqual(copyright_, f"{prefix}.x_misp_legal_copyright = '{_copyright}'")
        self.assertEqual(impfuzzy_, f"{prefix}.x_misp_impfuzzy = '{_impfuzzy}'")
        _name, _size, _entropy, _md5, _sha1, _sha256, _sha512, _ssdeep = (attribute['value'] for attribute in section['Attribute'])
        entropy_, name_, size_, md5_, sha1_, sha256_, sha512_, ssdeep_ = pattern[21:]
        prefix = f"{prefix}.sections[0]"
        self.assertEqual(entropy_, f"{prefix}.entropy = '{_entropy}'")
        self.assertEqual(name_, f"{prefix}.name = '{_name}'")
        self.assertEqual(size_, f"{prefix}.size = '{_size}'")
        self.assertEqual(md5_, f"{prefix}.hashes.MD5 = '{_md5}'")
        self.assertEqual(sha1_, f"{prefix}.hashes.SHA1 = '{_sha1}'")
        self.assertEqual(sha256_, f"{prefix}.hashes.SHA256 = '{_sha256}'")
        self.assertEqual(sha512_, f"{prefix}.hashes.SHA512 = '{_sha512}'")
        self.assertEqual(ssdeep_, f"{prefix}.hashes.SSDEEP = '{_ssdeep}'")

    def test_event_with_file_and_pe_observable_objects(self):
        event = get_event_with_file_and_pe_objects()
        misp_objects, grouping_refs, object_refs, observables = self._run_observable_from_objects_tests(event)
        _file, pe, section = misp_objects
        self.assertEqual(grouping_refs[0], object_refs[0])
        filename, md5, sha1, sha256, size, entropy = (attribute['value'] for attribute in _file['Attribute'])
        file_object = observables[0]
        self.assertEqual(file_object.id, object_refs[0])
        self.assertEqual(file_object.type, 'file')
        self.assertEqual(file_object.name, filename)
        hashes = file_object.hashes
        self.assertEqual(hashes['MD5'], md5)
        self.assertEqual(hashes['SHA-1'], sha1)
        self.assertEqual(hashes['SHA-256'], sha256)
        self.assertEqual(file_object.size, int(size))
        self.assertEqual(file_object.x_misp_entropy, entropy)
        _type, compilation, entrypoint, original, internal, desc, version, lang, prod_name, prod_version, company, copyright, sections, imphash, impfuzzy = (attribute['value'] for attribute in pe['Attribute'])
        pe_extension = file_object.extensions['windows-pebinary-ext']
        self.assertEqual(pe_extension.pe_type, _type)
        self.assertEqual(pe_extension.imphash, imphash)
        self.assertEqual(pe_extension.number_of_sections, int(sections))
        self.assertEqual(pe_extension.optional_header['address_of_entry_point'], int(entrypoint))
        self.assertEqual(pe_extension.x_misp_company_name, company)
        self.assertEqual(pe_extension.x_misp_compilation_timestamp, compilation)
        self.assertEqual(pe_extension.x_misp_file_description, desc)
        self.assertEqual(pe_extension.x_misp_file_version, version)
        self.assertEqual(pe_extension.x_misp_impfuzzy, impfuzzy)
        self.assertEqual(pe_extension.x_misp_internal_filename, internal)
        self.assertEqual(pe_extension.x_misp_lang_id, lang)
        self.assertEqual(pe_extension.x_misp_legal_copyright, copyright)
        self.assertEqual(pe_extension.x_misp_original_filename, original)
        self.assertEqual(pe_extension.x_misp_product_name, prod_name)
        self.assertEqual(pe_extension.x_misp_product_version, prod_version)
        name, size, entropy, md5, sha1, sha256, sha512, ssdeep = (attribute['value'] for attribute in section['Attribute'])
        section = pe_extension.sections[0]
        self.assertEqual(section.name, name)
        self.assertEqual(section.size, int(size))
        self.assertEqual(section.entropy, float(entropy))
        hashes = section.hashes
        self.assertEqual(hashes['MD5'], md5)
        self.assertEqual(hashes['SHA-1'], sha1)
        self.assertEqual(hashes['SHA-256'], sha256)
        self.assertEqual(hashes['SHA-512'], sha512)
        self.assertEqual(hashes['SSDEEP'], ssdeep)

    def test_event_with_file_indicator_object(self):
        event = get_event_with_file_object_with_artifact()
        attributes, pattern = self._run_indicator_from_object_tests(event)
        _malware_sample, _filename, _md5, _sha1, _sha256, _size, _attachment, _path, _encoding = (attribute['value'] for attribute in attributes)
        md5_, sha1_, sha256_, filename_, encoding_, size_, path_, malware_sample_, attachment_ = self._reassemble_pattern(pattern[1:-1])
        self.assertEqual(md5_, f"file:hashes.MD5 = '{_md5}'")
        self.assertEqual(sha1_, f"file:hashes.SHA1 = '{_sha1}'")
        self.assertEqual(sha256_, f"file:hashes.SHA256 = '{_sha256}'")
        self.assertEqual(filename_, f"file:name = '{_filename}'")
        self.assertEqual(encoding_, f"file:name_enc = '{_encoding}'")
        self.assertEqual(path_, f"file:parent_directory_ref.path = '{_path}'")
        self.assertEqual(size_, f"file:size = '{_size}'")
        ms_data, ms_filename, ms_md5 = malware_sample_.split(' AND ')
        self.assertEqual(ms_data, f"(file:content_ref.payload_bin = '{attributes[0]['data']}'")
        filename, md5 = _malware_sample.split('|')
        self.assertEqual(ms_filename, f"file:content_ref.x_misp_filename = '{filename}'")
        self.assertEqual(ms_md5, f"file:content_ref.hashes.MD5 = '{md5}')")
        a_data, a_filename = attachment_.split(' AND ')
        self.assertEqual(a_data, f"(file:content_ref.payload_bin = '{attributes[6]['data']}'")
        self.assertEqual(a_filename, f"file:content_ref.x_misp_filename = '{_attachment}')")

    def test_event_with_file_observable_object(self):
        event = get_event_with_file_object_with_artifact()
        attributes, grouping_refs, object_refs, observables = self._run_observable_from_object_tests(event)
        _malware_sample, _filename, _md5, _sha1, _sha256, _size, _attachment, _path, _encoding = (attribute['value'] for attribute in attributes)
        file, directory, artifact1, artifact2 = observables
        for grouping_ref, object_ref in zip(grouping_refs, object_refs):
            self.assertEqual(grouping_ref, object_ref)
        file_ref, directory_ref, artifact1_ref, artifact2_ref = grouping_refs
        self.assertEqual(file.id, file_ref)
        self.assertEqual(file.type, 'file')
        self.assertEqual(file.size, int(_size))
        self.assertEqual(file.name, _filename)
        self.assertEqual(file.name_enc, _encoding)
        hashes = file.hashes
        self.assertEqual(hashes['MD5'], _md5)
        self.assertEqual(hashes['SHA-1'], _sha1)
        self.assertEqual(hashes['SHA-256'], _sha256)
        self.assertEqual(file.parent_directory_ref, directory_ref)
        self.assertEqual(file.content_ref, artifact1_ref)
        self.assertEqual(directory.id, directory_ref)
        self.assertEqual(directory.type, 'directory')
        self.assertEqual(directory.path, _path)
        self.assertEqual(artifact1.id, artifact1_ref)
        self.assertEqual(artifact1.type, 'artifact')
        self.assertEqual(artifact1.payload_bin, attributes[0]['data'])
        filename, md5 = _malware_sample.split('|')
        self.assertEqual(artifact1.hashes['MD5'], md5)
        self.assertEqual(artifact1.x_misp_filename, filename)
        self.assertEqual(artifact2.id, artifact2_ref)
        self.assertEqual(artifact2.type, 'artifact')
        self.assertEqual(artifact2.payload_bin, attributes[6]['data'])
        self.assertEqual(artifact2.x_misp_filename, _attachment)

    def test_event_with_ip_port_indicator_object(self):
        prefix = 'network-traffic'
        event = get_event_with_ip_port_object()
        attributes, pattern = self._run_indicator_from_object_tests(event)
        ip, port, domain, first_seen = (attribute['value'] for attribute in attributes)
        pattern = pattern[1:-1].split(' AND ')
        self.assertEqual(
            ' AND '.join(pattern[:2]),
            f"({prefix}:dst_ref.type = 'ipv4-addr' AND {prefix}:dst_ref.value = '{ip}')"
        )
        self.assertEqual(
            ' AND '.join(pattern[2:4]),
            f"({prefix}:dst_ref.type = 'domain-name' AND {prefix}:dst_ref.value = '{domain}')"
        )
        self.assertEqual(pattern[4], f"{prefix}:dst_port = '{port}'")
        self.assertEqual(pattern[5], f"{prefix}:start = '{first_seen}'")

    def test_event_with_ip_port_observable_object(self):
        event = get_event_with_ip_port_object()
        attributes, grouping_refs, object_refs, observables = self._run_observable_from_object_tests(event)
        ip, port, domain, first_seen = (attribute['value'] for attribute in attributes)
        network_traffic_ref, address_ref = object_refs
        network_traffic, address_object = observables
        self.assertEqual(network_traffic_ref, grouping_refs[0])
        self.assertEqual(address_ref, grouping_refs[1])
        self.assertEqual(network_traffic.id, network_traffic_ref)
        self.assertEqual(network_traffic.type, 'network-traffic')
        self.assertEqual(network_traffic.dst_port, int(port))
        self.assertEqual(
            network_traffic.start.strftime('%Y-%m-%dT%H:%M:%SZ'),
            first_seen
        )
        self.assertIn('ipv4', network_traffic.protocols)
        self.assertEqual(network_traffic.dst_ref, address_ref)
        self.assertEqual(network_traffic.x_misp_domain, domain)
        self.assertEqual(address_object.id, address_ref)
        self.assertEqual(address_object.type, 'ipv4-addr')
        self.assertEqual(address_object.value, ip)

    def test_event_with_network_connection_indicator_object(self):
        event = get_event_with_network_connection_object()
        attributes, pattern = self._run_indicator_from_object_tests(event)
        _ip_src, _ip_dst, _src_port, _dst_port, _hostname, _layer3, _layer4, _layer7 = (attribute['value'] for attribute in attributes)
        ip_src_, ip_dst_, hostname_, dst_port_, src_port_, layer3_, layer4_, layer7_ = self._reassemble_pattern(pattern[1:-1])
        ip_src_type, ip_src_value = ip_src_.split(' AND ')
        self.assertEqual(ip_src_type, "(network-traffic:src_ref.type = 'ipv4-addr'")
        self.assertEqual(ip_src_value, f"network-traffic:src_ref.value = '{_ip_src}')")
        ip_dst_type, ip_dst_value = ip_dst_.split(' AND ')
        self.assertEqual(ip_dst_type, "(network-traffic:dst_ref.type = 'ipv4-addr'")
        self.assertEqual(ip_dst_value, f"network-traffic:dst_ref.value = '{_ip_dst}')")
        hostname_type, hostname_value = hostname_.split(' AND ')
        self.assertEqual(hostname_type, "(network-traffic:dst_ref.type = 'domain-name'")
        self.assertEqual(hostname_value, f"network-traffic:dst_ref.value = '{_hostname}')")
        self.assertEqual(dst_port_, f"network-traffic:dst_port = '{_dst_port}'")
        self.assertEqual(src_port_, f"network-traffic:src_port = '{_src_port}'")
        self.assertEqual(layer3_, f"network-traffic:protocols[0] = '{_layer3}'")
        self.assertEqual(layer4_, f"network-traffic:protocols[1] = '{_layer4}'")
        self.assertEqual(layer7_, f"network-traffic:protocols[2] = '{_layer7}'")

    def test_event_with_network_connection_observable_object(self):
        event = get_event_with_network_connection_object()
        attributes, grouping_refs, object_refs, observables = self._run_observable_from_object_tests(event)
        ip_src, ip_dst, src_port, dst_port, hostname, layer3, layer4, layer7 = (attribute['value'] for attribute in attributes)
        for grouping_ref, object_ref in zip(grouping_refs, object_refs):
            self.assertEqual(grouping_ref, object_ref)
        network_traffic, address1, address2 = observables
        network_traffic_ref, address1_ref, address2_ref = grouping_refs
        self.assertEqual(network_traffic.id, network_traffic_ref)
        self.assertEqual(network_traffic.type, 'network-traffic')
        self.assertEqual(network_traffic.src_port, int(src_port))
        self.assertEqual(network_traffic.dst_port, int(dst_port))
        self.assertEqual(network_traffic.protocols, [layer3, layer4, layer7])
        self.assertEqual(network_traffic.src_ref, address1_ref)
        self.assertEqual(network_traffic.dst_ref, address2_ref)
        self.assertEqual(network_traffic.x_misp_hostname_dst, hostname)
        self.assertEqual(address1.id, address1_ref)
        self.assertEqual(address1.type, 'ipv4-addr')
        self.assertEqual(address1.value, ip_src)
        self.assertEqual(address2.id, address2_ref)
        self.assertEqual(address2.type, 'ipv4-addr')
        self.assertEqual(address2.value, ip_dst)

    def test_event_with_network_socket_indicator_object(self):
        event = get_event_with_network_socket_object()
        attributes, pattern = self._run_indicator_from_object_tests(event)
        _ip_src, _ip_dst, _src_port, _dst_port, _hostname, _address_family, _domain_family, _socket_type, _state, _protocol = (attribute['value'] for attribute in attributes)
        ip_src_, ip_dst_, hostname_, dst_port_, src_port_, protocol_, address_family_, socket_type_, state_, domain_family_ = self._reassemble_pattern(pattern[1:-1])
        ip_src_type, ip_src_value = ip_src_.split(' AND ')
        self.assertEqual(ip_src_type, "(network-traffic:src_ref.type = 'ipv4-addr'")
        self.assertEqual(ip_src_value, f"network-traffic:src_ref.value = '{_ip_src}')")
        ip_dst_type, ip_dst_value = ip_dst_.split(' AND ')
        self.assertEqual(ip_dst_type, "(network-traffic:dst_ref.type = 'ipv4-addr'")
        self.assertEqual(ip_dst_value, f"network-traffic:dst_ref.value = '{_ip_dst}')")
        hostname_type, hostname_value = hostname_.split(' AND ')
        self.assertEqual(hostname_type, "(network-traffic:dst_ref.type = 'domain-name'")
        self.assertEqual(hostname_value, f"network-traffic:dst_ref.value = '{_hostname}')")
        self.assertEqual(dst_port_, f"network-traffic:dst_port = '{_dst_port}'")
        self.assertEqual(src_port_, f"network-traffic:src_port = '{_src_port}'")
        self.assertEqual(protocol_, f"network-traffic:protocols[0] = '{_protocol}'")
        self.assertEqual(address_family_, f"network-traffic:extensions.'socket-ext'.address_family = '{_address_family}'")
        self.assertEqual(socket_type_, f"network-traffic:extensions.'socket-ext'.socket_type = '{_socket_type}'")
        self.assertEqual(state_, f"network-traffic:extensions.'socket-ext'.is_{_state} = true")
        self.assertEqual(domain_family_, f"network-traffic:x_misp_domain_family = '{_domain_family}'")

    def test_event_with_network_socket_observable_object(self):
        event = get_event_with_network_socket_object()
        attributes, grouping_refs, object_refs, observables = self._run_observable_from_object_tests(event)
        ip_src, ip_dst, src_port, dst_port, hostname, address_family, domain_family, socket_type, state, protocol = (attribute['value'] for attribute in attributes)
        for grouping_ref, object_ref in zip(grouping_refs, object_refs):
            self.assertEqual(grouping_ref, object_ref)
        network_traffic, address1, address2 = observables
        network_traffic_ref, address1_ref, address2_ref = grouping_refs
        self.assertEqual(network_traffic.id, network_traffic_ref)
        self.assertEqual(network_traffic.type, 'network-traffic')
        self.assertEqual(network_traffic.src_port, int(src_port))
        self.assertEqual(network_traffic.dst_port, int(dst_port))
        self.assertEqual(network_traffic.protocols, [protocol])
        self.assertEqual(network_traffic.src_ref, address1_ref)
        self.assertEqual(network_traffic.dst_ref, address2_ref)
        socket_ext = network_traffic.extensions['socket-ext']
        self.assertEqual(socket_ext.address_family, address_family)
        self.assertEqual(socket_ext.socket_type, socket_type)
        self.assertEqual(getattr(socket_ext, f'is_{state}'), True)
        self.assertEqual(network_traffic.x_misp_domain_family, domain_family)
        self.assertEqual(network_traffic.x_misp_hostname_dst, hostname)
        self.assertEqual(address1.id, address1_ref)
        self.assertEqual(address1.type, 'ipv4-addr')
        self.assertEqual(address1.value, ip_src)
        self.assertEqual(address2.id, address2_ref)
        self.assertEqual(address2.type, 'ipv4-addr')
        self.assertEqual(address2.value, ip_dst)

    def test_event_with_process_indicator_object(self):
        event = get_event_with_process_object()
        attributes, pattern = self._run_indicator_from_object_tests(event)
        _pid, _child_pid, _parent_pid, _name, _image, _port = (attribute['value'] for attribute in attributes)
        pid_, image_, parent_pid_, child_pid_, name_, port_ = pattern[1:-1].split(' AND ')
        self.assertEqual(pid_, f"process:pid = '{_pid}'")
        self.assertEqual(image_, f"process:image_ref.name = '{_image}'")
        self.assertEqual(parent_pid_, f"process:parent_ref.pid = '{_parent_pid}'")
        self.assertEqual(child_pid_, f"process:child_refs[0].pid = '{_child_pid}'")
        self.assertEqual(name_, f"process:x_misp_name = '{_name}'")
        self.assertEqual(port_, f"process:x_misp_port = '{_port}'")

    def test_event_with_process_observable_object(self):
        event = get_event_with_process_object()
        attributes, grouping_refs, object_refs, observables = self._run_observable_from_object_tests(event)
        pid, child_pid, parent_pid, name, image, port = (attribute['value'] for attribute in attributes)
        for grouping_ref, object_ref in zip(grouping_refs, object_refs):
            self.assertEqual(grouping_ref, object_ref)
        process, parent_process, child_process, image_object = observables
        process_ref, parent_ref, child_ref, image_ref = grouping_refs
        self.assertEqual(process.id, process_ref)
        self.assertEqual(process.type, 'process')
        self.assertEqual(process.pid, int(pid))
        self.assertEqual(process.x_misp_name, name)
        self.assertEqual(process.x_misp_port, port)
        self.assertEqual(process.parent_ref, parent_ref)
        self.assertEqual(process.child_refs, [child_ref])
        self.assertEqual(process.image_ref, image_ref)
        self.assertEqual(parent_process.id, parent_ref)
        self.assertEqual(parent_process.type, 'process')
        self.assertEqual(parent_process.pid, int(parent_pid))
        self.assertEqual(child_process.id, child_ref)
        self.assertEqual(child_process.type, 'process')
        self.assertEqual(child_process.pid, int(child_pid))
        self.assertEqual(image_object.id, image_ref)
        self.assertEqual(image_object.type, 'file')
        self.assertEqual(image_object.name, image)

    def test_event_with_registry_key_indicator_object(self):
        event = get_event_with_registry_key_object()
        attributes, pattern = self._run_indicator_from_object_tests(event)
        _key, _hive, _name, _data, _data_type, _modified = (attribute['value'] for attribute in attributes)
        key_, modified_, data_, data_type_, name_, hive_ = pattern[1:-1].split(' AND ')
        key = _key.replace('\\', '\\\\')
        self.assertEqual(key_, f"windows-registry-key:key = '{key}'")
        self.assertEqual(modified_, f"windows-registry-key:modified = '{_modified}'")
        self.assertEqual(data_, f"windows-registry-key:values[0].data = '{_data}'")
        self.assertEqual(data_type_, f"windows-registry-key:values[0].data_type = '{_data_type}'")
        self.assertEqual(name_, f"windows-registry-key:values[0].name = '{_name}'")
        self.assertEqual(hive_, f"windows-registry-key:x_misp_hive = '{_hive}'")

    def test_event_with_registry_key_observable_object(self):
        event = get_event_with_registry_key_object()
        attributes, grouping_refs, object_refs, observables = self._run_observable_from_object_tests(event)
        key, hive, name, data, data_type, modified = (attribute['value'] for attribute in attributes)
        self.assertEqual(grouping_refs[0], object_refs[0])
        registry_key = observables[0]
        self.assertEqual(registry_key.id, object_refs[0])
        self.assertEqual(registry_key.type, 'windows-registry-key')
        self.assertEqual(registry_key.key, key)
        self.assertEqual(registry_key.modified, f'{modified}Z')
        self.assertEqual(registry_key.x_misp_hive, hive)
        registry_value = registry_key['values'][0]
        self.assertEqual(registry_value.data, data)
        self.assertEqual(registry_value.data_type, data_type)
        self.assertEqual(registry_value.name, name)

    def test_event_with_url_indicator_object(self):
        event = get_event_with_url_object()
        attributes, pattern = self._run_indicator_from_object_tests(event)
        _url, _domain, _host, _ip, _port = (attribute['value'] for attribute in attributes)
        url_, domain_, host_, ip_, port_ = pattern[1:-1].split(' AND ')
        self.assertEqual(url_, f"url:value = '{_url}'")
        self.assertEqual(domain_, f"url:x_misp_domain = '{_domain}'")
        self.assertEqual(host_, f"url:x_misp_host = '{_host}'")
        self.assertEqual(ip_, f"url:x_misp_ip = '{_ip}'")
        self.assertEqual(port_, f"url:x_misp_port = '{_port}'")

    def test_event_with_url_observable_object(self):
        event = get_event_with_url_object()
        attributes, grouping_refs, object_refs, observables = self._run_observable_from_object_tests(event)
        url, domain, host, ip, port = (attribute['value'] for attribute in attributes)
        self.assertEqual(grouping_refs[0], object_refs[0])
        url_object = observables[0]
        self.assertEqual(url_object.id, object_refs[0])
        self.assertEqual(url_object.type, 'url')
        self.assertEqual(url_object.value, url)
        self.assertEqual(url_object.x_misp_domain, domain)
        self.assertEqual(url_object.x_misp_host, host)
        self.assertEqual(url_object.x_misp_ip, ip)
        self.assertEqual(url_object.x_misp_port, port)

    def test_event_with_user_account_indicator_object(self):
        event = get_event_with_user_account_object()
        attributes, pattern = self._run_indicator_from_object_tests(event)
        _username, _userid, _display_name, _passwd, _group1, _group2, _groupid, _home, _account_type, _plc = (attribute['value'] for attribute in attributes)
        account_type_, display_name_, userid_, username_, passwd_, plc_, group1_, group2_, groupid_, home_ = pattern[1:-1].split(' AND ')
        self.assertEqual(account_type_, f"user-account:account_type = '{_account_type}'")
        self.assertEqual(display_name_, f"user-account:display_name = '{_display_name}'")
        self.assertEqual(userid_, f"user-account:user_id = '{_userid}'")
        self.assertEqual(username_, f"user-account:account_login = '{_username}'")
        self.assertEqual(passwd_, f"user-account:credential = '{_passwd}'")
        self.assertEqual(plc_, f"user-account:credential_last_changed = '{_plc}'")
        self.assertEqual(group1_, f"user-account:extensions.'unix-account-ext'.groups = '{_group1}'")
        self.assertEqual(group2_, f"user-account:extensions.'unix-account-ext'.groups = '{_group2}'")
        self.assertEqual(groupid_, f"user-account:extensions.'unix-account-ext'.gid = '{_groupid}'")
        self.assertEqual(home_, f"user-account:extensions.'unix-account-ext'.home_dir = '{_home}'")

    def test_event_with_user_account_observable_object(self):
        event = get_event_with_user_account_object()
        attributes, grouping_refs, object_refs, observables = self._run_observable_from_object_tests(event)
        username, userid, display_name, passwd, group1, group2, groupid, home, account_type, plc = (attribute['value'] for attribute in attributes)
        self.assertEqual(grouping_refs[0], object_refs[0])
        user_account = observables[0]
        self.assertEqual(user_account.id, object_refs[0])
        self.assertEqual(user_account.type, 'user-account')
        self.assertEqual(user_account.user_id, userid)
        self.assertEqual(user_account.credential, passwd)
        self.assertEqual(user_account.account_login, username)
        self.assertEqual(user_account.account_type, account_type)
        self.assertEqual(user_account.display_name, display_name)
        extension = user_account.extensions['unix-account-ext']
        self.assertEqual(extension.gid, int(groupid))
        self.assertEqual(extension.groups, [group1, group2])
        self.assertEqual(extension.home_dir, home)
        self.assertEqual(
            datetime.strftime(user_account.credential_last_changed, '%Y-%m-%dT%H:%M:%S'),
            plc
        )

    def test_event_with_vulnerability_object(self):
        event = get_event_with_vulnerability_object()
        orgc = event['Event']['Orgc']
        misp_object = deepcopy(event['Event']['Object'][0])
        self.parser.parse_misp_event(event)
        stix_objects = self.parser.stix_objects
        self._check_spec_versions(stix_objects)
        identity, grouping, vulnerability = stix_objects
        identity_id = self._check_identity_features(
            identity,
            orgc,
            self._datetime_from_timestamp(event['Event']['timestamp'])
        )
        args = (grouping, event['Event'], identity_id)
        object_ref = self._check_grouping_features(*args)[0]
        self._check_object_vulnerability_features(vulnerability, misp_object, identity_id, object_ref)

    def test_event_with_x509_indicator_object(self):
        event = get_event_with_x509_object()
        attributes, pattern = self._run_indicator_from_object_tests(event)
        _issuer, _pem, _pia, _pie, _pim, _srlnmbr, _signalg, _subject, _vnb, _vna, _version, _md5, _sha1 = (attribute['value'] for attribute in attributes)
        md5_, sha1_, issuer_, pia_, pie_, pim_, srlnmbr_, signalg_, subject_, version_, vna_, vnb_, pem_ = pattern[1:-1].split(' AND ')
        self.assertEqual(md5_, f"x509-certificate:hashes.MD5 = '{_md5}'")
        self.assertEqual(sha1_, f"x509-certificate:hashes.SHA1 = '{_sha1}'")
        self.assertEqual(issuer_, f"x509-certificate:issuer = '{_issuer}'")
        self.assertEqual(pia_, f"x509-certificate:subject_public_key_algorithm = '{_pia}'")
        self.assertEqual(pie_, f"x509-certificate:subject_public_key_exponent = '{_pie}'")
        self.assertEqual(pim_, f"x509-certificate:subject_public_key_modulus = '{_pim}'")
        self.assertEqual(srlnmbr_, f"x509-certificate:serial_number = '{_srlnmbr}'")
        self.assertEqual(signalg_, f"x509-certificate:signature_algorithm = '{_signalg}'")
        self.assertEqual(subject_, f"x509-certificate:subject = '{_subject}'")
        self.assertEqual(version_, f"x509-certificate:version = '{_version}'")
        self.assertEqual(vna_, f"x509-certificate:validity_not_after = '{_vna}'")
        self.assertEqual(vnb_, f"x509-certificate:validity_not_before = '{_vnb}'")
        self.assertEqual(pem_, f"x509-certificate:x_misp_pem = '{_pem}'")

    def test_event_with_x509_observable_object(self):
        event = get_event_with_x509_object()
        attributes, grouping_refs, object_refs, observables = self._run_observable_from_object_tests(event)
        issuer, pem, pia, pie, pim, srlnmbr, signalg, subject, vnb, vna, version, md5, sha1 = (attribute['value'] for attribute in attributes)
        self.assertEqual(grouping_refs[0], object_refs[0])
        x509 = observables[0]
        self.assertEqual(x509.id, object_refs[0])
        self.assertEqual(x509.type, 'x509-certificate')
        hashes = x509.hashes
        self.assertEqual(hashes['MD5'], md5)
        self.assertEqual(hashes['SHA-1'], sha1)
        self.assertEqual(x509.version, version)
        self.assertEqual(x509.serial_number, srlnmbr)
        self.assertEqual(x509.signature_algorithm, signalg)
        self.assertEqual(x509.issuer, issuer)
        self.assertEqual(
            datetime.strftime(x509.validity_not_before, '%Y-%m-%dT%H:%M:%S'),
            vnb
        )
        self.assertEqual(
            datetime.strftime(x509.validity_not_after, '%Y-%m-%dT%H:%M:%S'),
            vna
        )
        self.assertEqual(x509.subject, subject)
        self.assertEqual(x509.subject_public_key_algorithm, pia)
        self.assertEqual(x509.subject_public_key_modulus, pim)
        self.assertEqual(x509.subject_public_key_exponent, int(pie))
        self.assertEqual(x509.x_misp_pem, pem)

    ################################################################################
    #                            GALAXIES EXPORT TESTS.                            #
    ################################################################################

    def test_event_with_attack_pattern_galaxy(self):
        event = get_event_with_attack_pattern_galaxy()
        galaxy = event['Event']['Galaxy'][0]
        timestamp = self._datetime_from_timestamp(event['Event']['timestamp'])
        attack_pattern = self._run_galaxy_tests(event, timestamp)
        self.assertEqual(attack_pattern.type, 'attack-pattern')
        self._check_galaxy_features(attack_pattern, galaxy, timestamp, True, False)

    def test_event_with_course_of_action_galaxy(self):
        event = get_event_with_course_of_action_galaxy()
        galaxy = event['Event']['Galaxy'][0]
        timestamp = self._datetime_from_timestamp(event['Event']['timestamp'])
        course_of_action = self._run_galaxy_tests(event, timestamp)
        self.assertEqual(course_of_action.type, 'course-of-action')
        self._check_galaxy_features(course_of_action, galaxy, timestamp, False, False)

    def test_event_with_malware_galaxy(self):
        event = get_event_with_malware_galaxy()
        galaxy = event['Event']['Galaxy'][0]
        timestamp = self._datetime_from_timestamp(event['Event']['timestamp'])
        malware = self._run_galaxy_tests(event, timestamp)
        self.assertEqual(malware.type, 'malware')
        self._check_galaxy_features(malware, galaxy, timestamp, True, True)

    def test_event_with_threat_actor_galaxy(self):
        event = get_event_with_threat_actor_galaxy()
        galaxy = event['Event']['Galaxy'][0]
        timestamp = self._datetime_from_timestamp(event['Event']['timestamp'])
        threat_actor = self._run_galaxy_tests(event, timestamp)
        self.assertEqual(threat_actor.type, 'threat-actor')
        self._check_galaxy_features(threat_actor, galaxy, timestamp, False, True)

    def test_event_with_tool_galaxy(self):
        event = get_event_with_tool_galaxy()
        galaxy = event['Event']['Galaxy'][0]
        timestamp = self._datetime_from_timestamp(event['Event']['timestamp'])
        tool = self._run_galaxy_tests(event, timestamp)
        self.assertEqual(tool.type, 'tool')
        self._check_galaxy_features(tool, galaxy, timestamp, True, True)

    def test_event_with_vulnerability_galaxy(self):
        event = get_event_with_vulnerability_galaxy()
        galaxy = event['Event']['Galaxy'][0]
        timestamp = self._datetime_from_timestamp(event['Event']['timestamp'])
        vulnerability = self._run_galaxy_tests(event, timestamp)
        self.assertEqual(vulnerability.type, 'vulnerability')
        self._check_galaxy_features(vulnerability, galaxy, timestamp, False, False)
