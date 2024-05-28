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

        user_insert_query = """INSERT INTO "user"
            (ID, FIRST_NAME, LAST_NAME, EMAIL, PASSWORD, BIRTH_DATE, EMPLOYMENT_DATE,
            IS_SUPERUSER, IS_STAFF, IS_ACTIVE, CAN_MOVE_STOCKS, CAN_RECEPT_STOCKS, CAN_ISSUE_STOCKS,
            HAS_PASSWORD_SET)
            VALUES ('{user_id}', '${SUPERUSER_FIRST_NAME}', '${SUPERUSER_LAST_NAME}', '${SUPERUSER_EMAIL}',
        '${SUPERUSER_PASSWORD}', '${SUPERUSER_BIRTHDATE}', '${SUPERUSER_EMPLOYMENT_DATE}', 
        TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE)""".format(user_id=user_id)
        await connection.execute(user_insert_query)

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
