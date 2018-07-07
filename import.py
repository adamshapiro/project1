import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():

    # create a csv reader for the zips file
    f = open("zips.csv")
    reader = csv.reader(f)

    # skip the header row in the file
    next(reader, None)

    for zip, city, state, lat, long, pop in reader:
        # check if zip lost leading zero, and re-add if necessary
        if len(zip) == 4:
            zip = "0" + zip

        # latitude and longitude are both floats in the database
        lat = float(lat)
        long = float(long)

        # add each row into the database
        db.execute("INSERT INTO locations (zip, city, state, latitude, longitude, population) VALUES (:z, :c, :s, :lat, :long, :p)",
            {"z": zip, "c": city, "s": state, "lat": lat, "long": long, "p": pop})

    # and commit the insertions!
    db.commit()

if __name__ == "__main__":
    main()
