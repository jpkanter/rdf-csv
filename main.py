 #!/usr/bin/env python
# coding: utf-8

# Copyright 2021 by Leipzig University Library, http://ub.uni-leipzig.de
#                   JP Kanter, <kanter@ub.uni-leipzig.de>
#
# This file is part of RDF+CSV.
#
# This program is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RDF+CSV. If not, see <http://www.gnu.org/licenses/>.
#
# @license GPL-3.0-only <https://www.gnu.org/licenses/gpl-3.0.en.html>

import copy
import logging
import os
import json
import codecs
import csv
from rdflib import Graph
from rdflib.term import URIRef

__rdffile__ = "./gm306.ttl"
__csvfile__ = "jgames.csv"
__relevant_csv_fields__ = ['GPIr', 'QId', 'ASIN', 'Leipzig ID']
__export_joined_file__ = "joined.json"
__rdf_json__ = "rdf.json"
__csv_json__ = "csv.json"

__ma_prefix = "https://mediaarts-db.bunka.go.jp/data/property/"
__toi__ = {  # triples of interest
    f"{__ma_prefix}source": "source",
    f"{__ma_prefix}freebase": "freebase",
    f"{__ma_prefix}imdb": "imdb",
    f"{__ma_prefix}mobyGames": "moby",
    f"{__ma_prefix}metacritic": "metacritic",
    f"{__ma_prefix}twitch": "twitch",
    "https://schema.org/identifier": "jident"
}

if __name__ == "__main__":
    print("Starting main")
    turtle = Graph()
    turtle.load(__rdffile__, format="turtle")
    all_of_it = {}
    for _, subject in enumerate(turtle.subjects()):
        data = {}
        for bla in turtle.predicate_objects(subject):
            if bla[0].toPython() in __toi__:
                if bla[0].toPython() == f"{__ma_prefix}source":
                    source_url = bla[1].toPython().split(" ")[0]
                    url_parts = source_url.split("/")
                    data[__toi__[bla[0].toPython()]] = url_parts[len(url_parts)-1]
                elif bla[0].toPython() == f"{__ma_prefix}mobyGames":
                    data[__toi__[bla[0].toPython()]] = bla[1].toPython().split(",") # it seems like moby games are comma separated
                else:
                    data[__toi__[bla[0].toPython()]] = bla[1].toPython()
        if 'jident' in data:
            all_of_it[data['jident']] = data
        else:
            all_of_it[subject] = data
    csv_info = {}
    with codecs.open(__csvfile__, "r", encoding="utf-8", errors="ignore") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        lines = csv_reader.__iter__()
        header = lines.__next__()
        row_map = {key:_ for _, key in enumerate(header)}
        main_data = {}
        for _, row in enumerate(lines):
            if row[0] == "" and row[1] == "" and row[2] == "":
                continue
            data = {}
            terms = set(__relevant_csv_fields__)
            for i, value in enumerate(row):
                if header[i] in terms:
                    if value.strip() != "":
                        data[header[i]] = value
                    terms.remove(header[i])
                if len(terms) <= 0:
                    break
            if 'Leipzig ID' not in data:
                logging.warning(f"Leipzig ID was empty for {str(data)}")
            if 'QId' in data:  # same filter as above for source
                #main_data[data['Leipzig ID']] = data
                main_data[data['QId']] = data
    all_shared = []
    for key, value in all_of_it.items():
        if 'source' in value:
            if value['source'] in main_data:
                    similar = copy.deepcopy(all_of_it[key])
                    similar.update(main_data[value['source']])
                    all_shared.append(similar)
    print(f"Shared Entries: {len(all_shared)}")
    print(f"J Entries: {len(all_of_it)}")
    print(f"CSV Entries: {len(main_data)}")
    with codecs.open(__export_joined_file__, "w", encoding="utf-8") as export_file:
        json.dump(all_shared, export_file, indent=3, ensure_ascii=False)
    with codecs.open(__rdf_json__ , "w", encoding="utf-8") as export_file:
        json.dump(all_of_it, export_file, indent=3, ensure_ascii=False)
    with codecs.open(__csv_json__, "w", encoding="utf-8") as export_file:
        json.dump(main_data, export_file, indent=3, ensure_ascii=False)
