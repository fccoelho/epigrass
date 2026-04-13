#!/usr/bin/env python3
"""
Build Epigrass model files from ANTT2002 transportation data.
"""

import pandas as pd
import geobr
from shapely.geometry import Point
import re
import unicodedata

WORKDIR = "/home/fccoelho/Documentos/Projects_software/epigrass/demos/ANTT2002"


def load_data():
    """Load all required data files."""
    print("Loading data files...")

    edges = pd.read_csv(f"{WORKDIR}/edges.csv")
    pop = pd.read_csv(f"{WORKDIR}/POPTBR02.csv")
    sites_orig = pd.read_csv(f"{WORKDIR}/sites.csv")

    print(f"  edges.csv: {len(edges)} rows")
    print(f"  POPTBR02.csv: {len(pop)} rows")
    print(f"  sites.csv (original): {len(sites_orig)} rows")

    return edges, pop, sites_orig


def get_unique_cities(edges):
    """Extract unique cities from edges file."""
    cities1 = edges[["municipio1", "uf1"]].rename(
        columns={"municipio1": "name", "uf1": "state"}
    )
    cities2 = edges[["municipio2", "uf2"]].rename(
        columns={"municipio2": "name", "uf2": "state"}
    )
    cities = pd.concat([cities1, cities2]).drop_duplicates()
    cities["name_upper"] = cities["name"].str.upper().str.strip()
    print(f"\nUnique cities in edges: {len(cities)}")
    return cities


def state_abbrev_to_name(abbrev):
    """Convert state abbreviation to full name."""
    state_map = {
        "AC": "Acre",
        "AL": "Alagoas",
        "AP": "Amapá",
        "AM": "Amazonas",
        "BA": "Bahia",
        "CE": "Ceará",
        "DF": "Distrito Federal",
        "ES": "Espírito Santo",
        "GO": "Goiás",
        "MA": "Maranhão",
        "MT": "Mato Grosso",
        "MS": "Mato Grosso do Sul",
        "MG": "Minas Gerais",
        "PA": "Pará",
        "PB": "Paraíba",
        "PR": "Paraná",
        "PE": "Pernambuco",
        "PI": "Piauí",
        "RJ": "Rio de Janeiro",
        "RN": "Rio Grande do Norte",
        "RS": "Rio Grande do Sul",
        "RO": "Rondônia",
        "RR": "Roraima",
        "SC": "Santa Catarina",
        "SP": "São Paulo",
        "SE": "Sergipe",
        "TO": "Tocantins",
    }
    return state_map.get(abbrev.upper().strip(), abbrev)


def load_geobr_municipalities():
    """Load Brazilian municipalities from geobr."""
    print("\nLoading geobr municipality data...")
    try:
        mun = geobr.read_municipality(year=2020)
        print(f"  geobr loaded: {len(mun)} municipalities")
        return mun
    except Exception as e:
        print(f"  Error loading geobr: {e}")
        return None


def normalize_name(name):
    """Normalize city name for matching (remove accents, uppercase)."""
    if pd.isna(name):
        return ""
    name = str(name).strip()
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    name = name.upper().strip()
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name


MANUAL_NAME_CORRECTIONS = {
    ("CACHOEIRO DO ITAPEMIRIM", "ES"): "Cachoeiro De Itapemirim",
    ("GOV VALADARES", "MG"): "Governador Valadares",
    ("PRES PRUDENTE", "SP"): "Presidente Prudente",
    ("MOGI-GUACU", "SP"): "Mogi Guacu",
}


def find_city_in_geobr(city_name, state_abbrev, geobr_df):
    """Find a city in geobr data using name and state."""
    state_upper = state_abbrev.upper().strip()
    lookup_key = (city_name.upper().strip(), state_upper)

    if lookup_key in MANUAL_NAME_CORRECTIONS:
        city_name = MANUAL_NAME_CORRECTIONS[lookup_key]

    name_norm = normalize_name(city_name)

    matches = geobr_df[
        (geobr_df["name_upper"] == name_norm)
        | (geobr_df["name_normalized"] == name_norm)
    ]

    if len(matches) == 0:
        return None, None

    if len(matches) == 1:
        return matches.iloc[0]["geometry"], int(matches.iloc[0]["code_muni"])

    matches_state = matches[matches["abbrev_state"] == state_upper]
    if len(matches_state) == 1:
        return matches_state.iloc[0]["geometry"], int(
            matches_state.iloc[0]["code_muni"]
        )

    if len(matches_state) > 1:
        return matches_state.iloc[0]["geometry"], int(
            matches_state.iloc[0]["code_muni"]
        )

    return matches.iloc[0]["geometry"], int(matches.iloc[0]["code_muni"])


def get_centroid(geom):
    """Get centroid of geometry."""
    if geom is None:
        return None, None
    try:
        centroid = geom.centroid
        return centroid.y, centroid.x
    except:
        return None, None


def build_sites_and_edges(edges, pop, geobr_df):
    """Build sites.csv and edges.csv dataframes."""
    cities = get_unique_cities(edges)

    print("\nMatching cities to geobr...")
    site_records = []
    city_to_geocode = {}
    not_found = []

    for _, row in cities.iterrows():
        name = row["name"]
        state = row["state"]
        name_norm = normalize_name(name)

        geom, code_muni = find_city_in_geobr(name, state, geobr_df)

        if geom is not None:
            lat, lon = get_centroid(geom)
            code_muni_6 = int(str(code_muni)[:6])

            pop_match = pop[pop["MUNIC_RES"] == code_muni_6]
            population = (
                pop_match["POPULACAO"].values[0] if len(pop_match) > 0 else 100000
            )

            site_records.append(
                {
                    "lat": lat,
                    "long": lon,
                    "name": name,
                    "pop": population,
                    "geocode": code_muni,
                }
            )
            city_to_geocode[(name.upper().strip(), state.upper().strip())] = code_muni
            print(f"  ✓ {name} ({state}) -> {code_muni}")
        else:
            not_found.append((name, state))
            print(f"  ✗ NOT FOUND: {name} ({state})")

    print(f"\nSites found: {len(site_records)}")
    print(f"Cities not found: {len(not_found)}")

    sites_df = pd.DataFrame(site_records)

    print("\nBuilding edges with geocodes...")
    edge_records = []
    edges_not_found = 0

    for _, row in edges.iterrows():
        key1 = (row["municipio1"].upper().strip(), row["uf1"].upper().strip())
        key2 = (row["municipio2"].upper().strip(), row["uf2"].upper().strip())

        code1 = city_to_geocode.get(key1)
        code2 = city_to_geocode.get(key2)

        if code1 and code2:
            edge_records.append(
                {
                    "Source": code1,
                    "Dest": code2,
                    "flowSD": row["pass ida"],
                    "flowDS": row["pass volta"],
                    "Distance": 0,
                    "geoSource": row["municipio1"],
                    "geoDest": row["municipio2"],
                }
            )
        else:
            edges_not_found += 1

    print(f"Edges created: {len(edge_records)}")
    print(f"Edges skipped (city not found): {edges_not_found}")

    edges_df = pd.DataFrame(edge_records)

    return sites_df, edges_df


def create_model_epg(sites_df, edges_df, output_dir):
    """Create the model.epg file."""

    n_sites = len(sites_df)
    n_edges = len(edges_df)

    model_content = f"""################################################################
#
#  EPIGRASS - Model Definition
#  Dengue model using ANTT2002 transportation network
#
################################################################
################################################################

#==============================================================#
[THE WORLD]
#==============================================================#

sites = sites.csv
edges = edges.csv
encoding = utf8

#==============================================================#
[EPIDEMIOLOGICAL MODEL]
#==============================================================#
modtype = SEIR

#==============================================================#
[MODEL PARAMETERS]
#==============================================================#

# Dengue typical parameters
beta = 0.4          # transmission coefficient
alpha = 1           # clumping parameter (1 = mass action)
e = 0.2              # incubation rate (5 days = 1/5)
r = 0.143            # recovery rate (7 days = 1/7)
delta = 0            # probability of acquiring full immunity
tau = 0              # delay in start of control measures
k = 0                # reduction in transmission due to controls
B = 0                # birth rate
w = 0                # immunity waning rate
p = 0                # probability of recovered becoming infected

#==============================================================#
[INITIAL CONDITIONS]
#==============================================================#
S = N
E = 0
I = 0

#==============================================================#
[EPIDEMIC EVENTS]
#==============================================================#
# Initial infection in a few major cities
seed = [({sites_df.iloc[0]["geocode"]}, 'I', 10)]
Vaccinate = []
Quarantine = []

#==============================================================#
[TRANSPORTATION MODEL]
#==============================================================#
doTransp = 1
stochastic = 0
speed = 0

#==============================================================#
[SIMULATION AND OUTPUT]
#==============================================================#
steps = 365
outdir =
sqlout = 1
report = 0
Replicas = 0
RandSeed = 0
Batch = []

################################################################
################################################################
"""

    model_path = f"{output_dir}/model.epg"
    with open(model_path, "w") as f:
        f.write(model_content)

    print(f"\nCreated model.epg: {model_path}")


def main():
    """Main function to build all model files."""
    output_dir = WORKDIR

    edges, pop, sites_orig = load_data()
    geobr_df = load_geobr_municipalities()

    if geobr_df is None:
        print("Failed to load geobr. Exiting.")
        return

    geobr_df["name_upper"] = geobr_df["name_muni"].str.upper().str.strip()
    geobr_df["name_normalized"] = geobr_df["name_upper"].apply(normalize_name)

    sites_df, edges_df = build_sites_and_edges(edges, pop, geobr_df)

    sites_df.to_csv(f"{output_dir}/sites.csv", index=False)
    print(f"\nSaved sites.csv: {len(sites_df)} sites")

    edges_df.to_csv(f"{output_dir}/edges.csv", index=False)
    print(f"Saved edges.csv: {len(edges_df)} edges")

    create_model_epg(sites_df, edges_df, output_dir)

    print("\n" + "=" * 60)
    print("MODEL CREATION COMPLETE")
    print("=" * 60)
    print(f"Sites: {len(sites_df)}")
    print(f"Edges: {len(edges_df)}")
    print(f"\nFiles created in {output_dir}:")
    print("  - sites.csv")
    print("  - edges.csv")
    print("  - model.epg")


if __name__ == "__main__":
    main()
