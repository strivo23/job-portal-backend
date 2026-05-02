from django.db import migrations


def add_description_if_missing(apps, schema_editor):
    Job = apps.get_model("Jobs", "Job")
    table_name = Job._meta.db_table

    with schema_editor.connection.cursor() as cursor:
        table_description = schema_editor.connection.introspection.get_table_description(
            cursor, table_name
        )

    existing_columns = {col.name for col in table_description}
    if "description" in existing_columns:
        return

    field = Job._meta.get_field("description")
    schema_editor.add_field(Job, field)


class Migration(migrations.Migration):
    dependencies = [
        ("Jobs", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_description_if_missing, migrations.RunPython.noop),
    ]
