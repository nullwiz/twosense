import argparse
from api.adapters.orm import create_tables, drop_tables
from api.config import get_sync_postgres_uri
from sqlalchemy import create_engine


def main(drop):
    # Get the connection string
    connection_string = get_sync_postgres_uri()

    # Create the SQLAlchemy engine
    engine = create_engine(connection_string)

    if drop:
        drop_tables(engine)
        print("Tables dropped.")
    create_tables(engine)
    print("Tables created.")

    # Close the engine
    engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage database tables.")
    parser.add_argument('--drop', action='store_true',
                        help='Drop tables if given')
    args = parser.parse_args()

    main(drop=args.drop)
