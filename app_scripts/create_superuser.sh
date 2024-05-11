#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

create_superuser() {
python << END
import sys
import asyncio
import uuid

import asyncpg

async def run():
    try:
        connection = await asyncpg.connect(
            database="${TEST_POSTGRES_DB}" if "$1" == "test_db" else "${POSTGRES_DB}",
            user="${POSTGRES_USER}",
            password="${POSTGRES_PASSWORD}",
            host="${POSTGRES_HOST}",
            port="${POSTGRES_PORT}"
        )

        user_id = uuid.uuid4()

        # Inserting user data
        user_insert_query = """INSERT INTO "user"
            (ID, FIRST_NAME, LAST_NAME, EMAIL, USERNAME, PASSWORD, BIRTH_DATE, IS_SUPERUSER, IS_STAFF, IS_ACTIVE)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)"""
        await connection.execute(user_insert_query, user_id, "${SUPERUSER_FIRST_NAME}",
                                 "${SUPERUSER_LAST_NAME}", "${SUPERUSER_EMAIL}",
                                 "${SUPERUSER_USERNAME}", "${SUPERUSER_PASSWORD}",
                                 "${SUPERUSER_BIRTHDATE}", True, True, True)

        # Inserting user address data
        address_id = uuid.uuid4()
        address_insert_query = """INSERT INTO "user_address"
            (ID, COUNTRY, STATE, CITY, POSTAL_CODE, STREET, HOUSE_NUMBER, APARTMENT_NUMBER, USER_ID)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)"""
        await connection.execute(address_insert_query, address_id, 'USA', 'Texas', 'Houston',
                                 '34567', 'Walker Avenue', '35', '2', user_id)

        print("successfully created superuser")

    except asyncpg.exceptions.UniqueViolationError:
        print("Couldn't create a superuser. Check if the superuser account is already created.")
        sys.exit(-1)
    finally:
        await connection.close()

asyncio.run(run())

END
}

create_superuser $1

exec "$@"
