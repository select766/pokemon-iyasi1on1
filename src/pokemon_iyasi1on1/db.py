import csv
from pathlib import Path

from pokemon_iyasi1on1.model import PokeSpecies


def load_species_from_csv() -> list[PokeSpecies]:
    csv_path = Path(__file__).parent / "base_stats.csv"
    species_list = []
    seen_numbers = set()

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            original_no = int(row["No."])
            no = original_no

            while no in seen_numbers:
                no = no + 10000
            seen_numbers.add(no)

            name = row["ポケモン"].replace("\n", "")

            species = PokeSpecies(
                no=no,
                name=name,
                base_hp=int(row["HP"]),
                base_a=int(row["攻撃"]),
                base_b=int(row["防御"]),
                base_s=int(row["素早さ"]),
            )
            species_list.append(species)

    return species_list


_all_species = load_species_from_csv()
_species_by_name = {species.name: species for species in _all_species}
_species_by_no = {species.no: species for species in _all_species}


def get_species(no: int) -> PokeSpecies:
    if no in _species_by_no:
        return _species_by_no[no]
    raise ValueError(f"Species with no {no} not found.")


def get_species_by_name(name: str) -> PokeSpecies:
    if name in _species_by_name:
        return _species_by_name[name]
    raise ValueError(f"Species with name {name} not found.")


if __name__ == "__main__":
    for species in _all_species:
        print(species)
