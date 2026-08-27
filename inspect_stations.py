"""
Quick terminal inspector for the station_codes table in Supabase.

Usage:
    export DATABASE_URL="postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres"
    python3 inspect_stations.py

Get DATABASE_URL from Supabase dashboard -> Project Settings -> Database
-> Connection string (URI). Use the "Session pooler" or direct connection
string depending on what your app already uses elsewhere.
"""

import os
import sys

import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    sys.exit("Set DATABASE_URL env var first (see docstring above).")


def main():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("SELECT COUNT(*) AS total FROM station_codes;")
    total = cur.fetchone()["total"]
    print(f"Total stations: {total}\n")

    cur.execute("""
        SELECT COUNT(*) FILTER (WHERE crs_code IS NULL) AS missing_crs,
               COUNT(*) FILTER (WHERE route_description IS NULL) AS missing_route
        FROM station_codes;
    """)
    row = cur.fetchone()
    print(f"Missing CRS code: {row['missing_crs']}")
    print(f"Missing route:    {row['missing_route']}\n")

    cur.execute("""
        SELECT route_description, COUNT(*) AS station_count
        FROM station_codes
        GROUP BY route_description
        ORDER BY station_count DESC;
    """)
    print("Stations per route:")
    for row in cur.fetchall():
        route = row["route_description"] or "(none)"
        print(f"  {route:<30} {row['station_count']}")

    print("\nSample rows with a CRS code:")
    cur.execute("""
        SELECT stanox_no, full_name, crs_code, route_description
        FROM station_codes
        WHERE crs_code IS NOT NULL
        ORDER BY full_name
        LIMIT 10;
    """)
    for row in cur.fetchall():
        print(f"  [{row['crs_code']}] {row['full_name']} ({row['route_description']})")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
