from sqlalchemy import inspect, text


V3_COLUMNS = {
    "cages": {
        "user_id": "INTEGER",
    },
    "mice": {
        "user_id": "INTEGER",
        "external_id": "VARCHAR",
        "retag": "VARCHAR",
        "color": "VARCHAR",
        "purpose": "VARCHAR",
        "sacrificed": "VARCHAR",
    },
    "matings": {
        "user_id": "INTEGER",
        "genotyping_reference": "VARCHAR",
        "keep_litter": "INTEGER",
        "euthanise_litter": "INTEGER",
        "kept_male_pups": "INTEGER",
        "kept_female_pups": "INTEGER",
        "kept_pup_genotype": "VARCHAR",
        "kept_mouse_ids": "TEXT",
    },
}

CREATE_V311_TABLES = [
    """
    CREATE TABLE IF NOT EXISTS litter_pups (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        mating_id INTEGER NOT NULL,
        mouse_id INTEGER,
        pup_label VARCHAR,
        assigned_external_id VARCHAR,
        sex VARCHAR NOT NULL,
        dob DATE,
        wean_date DATE,
        genotype VARCHAR,
        genotype_reference_1 VARCHAR,
        genotype_reference_2 VARCHAR,
        decision VARCHAR NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(mating_id) REFERENCES matings(id),
        FOREIGN KEY(mouse_id) REFERENCES mice(id)
    )
    """
]


def apply_v3_schema_upgrades(engine):
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as connection:
        for statement in CREATE_V311_TABLES:
            connection.execute(text(statement))

        for table_name, columns in V3_COLUMNS.items():
            if table_name not in existing_tables:
                continue

            existing_columns = {
                column["name"] for column in inspector.get_columns(table_name)
            }
            for column_name, column_type in columns.items():
                if column_name in existing_columns:
                    continue
                connection.execute(
                    text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
                )
