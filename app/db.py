import json
import logging
import os
from operator import itemgetter

from app import prepare

logger = logging.getLogger(__name__)

class JSONDatabase:

    def __init__(self, dir="all"):
        self.path = None
        self.database = {
            "sprite_data": {}
        }
        self.load(dir)

    def load(self, directory="all"):
        """Loads all data from JSON files located under our data path.
        :param directory: The directory under resources/db/ to load. Defaults
            to "all".
        :type directory: String
        :returns: None
        """

        self.path = prepare.fetch("db")
        if directory == "all":
            self.load_json("sprite_data")
        else:
            self.load_json(directory)

    def load_json(self, directory):
        """Loads all JSON items under a specified path.
        :param directory: The directory under resources/db/ to look in.
        :type directory: String
        :returns: None
        """

        for json_item in os.listdir(os.path.join(self.path, directory)):

            # Only load .json files.
            if not json_item.endswith(".json"):
                continue

            # Load our json as a dictionary.
            with open(os.path.join(self.path, directory, json_item)) as fp:
                try:
                    item = json.load(fp)
                except ValueError:
                    logger.error("invalid JSON " + json_item)
                    raise

            if type(item) is list:
                for sub in item:
                    self.load_dict(sub, directory)
            else:
                self.load_dict(item, directory)

    def load_dict(self, item, table):
        """Loads a single json object as a dictionary and adds it to the appropriate db table
        :param item: The json object to load in
        :type item: dict
        :param table: The db table to load the object into
        :type table: String
        :returns None
        """

        if item['slug'] not in self.database[table]:
            self.database[table][item['slug']] = item
        else:
            logger.warning("Error: Item with slug %s was already loaded.", item)

    def lookup(self, slug, table="monster"):
        """Looks up a monster, technique, item, or npc based on slug.
        :param slug: The slug of the monster, technique, item, or npc.  A short English identifier.
        :param table: Which index to do the search in. Can be: "monster",
            "item", "npc", or "technique".
        :type slug: String
        :type table: String
        :rtype: Dict
        :returns: A dictionary from the resulting lookup.
        """
        return set_defaults(
            self.database[table][slug],
            table
        )

    def lookup_file(self, table, slug):
        """Does a lookup with the given slug in the given table, expecting a dictionary with two keys, 'slug' and 'file'
        :param slug: The slug of the file record.
        :param table: The table to do the lookup in, such as "sounds" or "music"
        :type slug: String
        :type table: String
        :rtype: String
        :returns: The 'file' property of the resulting dictionary OR the slug if it doesn't exist.
        """
        try:
            filename = self.database[table][slug]["file"]
        except:
            filename = slug
            logger.debug(
                "Could not find a file record for slug {}, did you remember to create a database record?".format(slug))
        return filename


def set_defaults(results, table):
    if table == "monster":
        name = results['slug']

        sprites = results.setdefault(
            "sprites",
            {}
        )

        for key, view in (
                ('battle1', 'front'),
                ('battle2', 'back'),
                ('menu1', 'menu01'),
                ('menu2', 'menu02'),
        ):
            if not results.get(key):
                sprites[key] = "gfx/sprites/battle/{}-{}".format(
                    name,
                    view
                )

    return results


# Global database container
db = JSONDatabase()
