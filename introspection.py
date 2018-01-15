from django.db import models, connection
from django.core.management.commands import inspectdb
import re
from collections import OrderedDict
from django.db.models.options import Options
import timeit

class ModelFactory:

    def __init__(self, app_name, table_name):
        self.app_name = app_name
        self.table_name = table_name

    @property
    def models(self):
        app_name = self.app_name
        table_name = self.table_name
        def strip_prefix(s):
            return s[1:] if s.startswith("u'") else s

        def table2model(table_name):
            return re.sub(r'[^a-zA-Z0-9]', '', table_name.title())
        cursor = connection.cursor()
        try:
            relations = connection.introspection.get_relations(cursor, table_name)
        except NotImplementedError:
            relations = {}
        try:
            constraints = connection.introspection.get_constraints(
                cursor, table_name)
        except NotImplementedError:
            constraints = {}
        primary_key_column = connection.introspection.get_primary_key_column(
            cursor, table_name)
        unique_columns = [
            c['columns'][0] for c in constraints.values()
            if c['unique'] and len(c['columns']) == 1
        ]
        table_description = connection.introspection.get_table_description(
            cursor, table_name)


        used_column_names = []
        column_to_field_name = {}
        class_name = table2model(table_name)
        field_list = []
        for row in table_description:
            # Holds Field notes, to be displayed in a Python comment.
            comment_notes = []
            # Holds Field parameters such as 'db_column'.
            extra_params = OrderedDict()
            column_name = row[0]
            is_relation = column_name in relations
            att_name, params, notes = inspectdb.Command().normalize_col_name(
                column_name, used_column_names, is_relation)
            extra_params.update(params)
            comment_notes.extend(notes)
            used_column_names.append(att_name)
            column_to_field_name[column_name] = att_name
            if column_name == primary_key_column:
                extra_params['primary_key'] = True
            elif column_name in unique_columns:
                extra_params['unique'] = True
            field_type, field_params, field_notes = inspectdb.Command(
            ).get_field_type(connection, table_name, row)
            extra_params.update(field_params)
            comment_notes.extend(field_notes)

            field_type += '('
            if att_name == 'id' and extra_params == {'primary_key': True}:
                if field_type == 'AutoField(':
                    continue
                elif field_type == 'IntegerField(' and not connection.features.can_introspect_autofield:
                    comment_notes.append('AutoField?')
            if row[6]:  # If it's NULL...
                if field_type == 'BooleanField(':
                    field_type = 'NullBooleanField('
                else:
                    extra_params['blank'] = True
                    extra_params['null'] = True

            field_desc = '%s = %s%s' % (
                att_name,
                # Custom fields will have a dotted path
                '' if '.' in field_type else 'models.',
                field_type,
            )
            if field_type.startswith('ForeignKey('):
                field_desc += ', models.DO_NOTHING'

            if extra_params:
                if not field_desc.endswith('('):
                    field_desc += ', '
                field_desc += ', '.join(
                    '%s=%s' % (k, strip_prefix(repr(v)))
                    for k, v in extra_params.items())
            field_desc += ')'
            if comment_notes:
                field_desc += '  # ' + ' '.join(comment_notes)
            result = '    %s' % field_desc
            field_list.append(result + '\n')
        class_header = 'class ' + class_name + '(models.Model):\n'
        class_meta = "    class Meta:\n        db_table='{}'".format(table_name)
        executable_statement = class_header + "".join(field_list) + class_meta
        exec(executable_statement)
        return eval(class_name)

# from http import server
