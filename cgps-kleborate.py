import csv
import dataclasses
import json
import subprocess
import sys
from dataclasses import field
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

"""Script runs Kleborate and reformats the results for use by Pathogenwatch"""


class Profile(str, Enum):
    kpsc = "kpsc"
    kosc = "kosc"
    eco = "eco"
    other = "other"


@dataclasses.dataclass
class Config:
    profile: Profile
    output_filename: str
    flag: list[str] = field(default_factory=list)


modules = {
    "top_level_modules": {
        "enterobacterales__species",
        "general__contig_stats",
        "klebsiella_oxytoca_complex__mlst",
        "klebsiella_pneumo_complex__mlst",
        "escherichia__mlst_achtman",
        "escherichia__mlst_pasteur",
        "klebsiella_pneumo_complex__kaptive",
        "klebsiella_pneumo_complex__wzi",
    },
    "virulence_modules": {
        "klebsiella__abst",
        "klebsiella__cbst",
        "klebsiella__rmst",
        "klebsiella__rmpa2",
        "klebsiella__smst",
        "klebsiella__ybst",
        "klebsiella_pneumo_complex__virulence_score",
    },
    "amr_modules": {
        "klebsiella_pneumo_complex__amr",
        "klebsiella_pneumo_complex__resistance_score",
        "klebsiella_pneumo_complex__resistance_class_count",
        "klebsiella_pneumo_complex__resistance_gene_count",
    },
}
configs = {
    Profile.kpsc: Config(
        Profile.kpsc,
        "klebsiella_pneumo_complex_output.txt",
        ["-p", "kpsc"],
    ),
    Profile.kosc: Config(
        Profile.kosc,
        "klebsiella_oxytoca_complex_output.txt",
        ["-p", "kosc"],
    ),
    Profile.eco: Config(
        Profile.eco,
        "Escherichia_coli_output.txt",
        ["-p", "eco"],
    ),
    Profile.other: Config(
        Profile.other,
        "enterobacterales__species_output.txt",
        ["-m", "enterobacterales__species"],
    ),
}


def parse_kleborate(raw: dict[str, str], amr_dict: dict[str, dict[str, str]]) -> dict[str, any]:
    result: dict[str, any] = {
        "modules": [],
        "amr": {
            "profile": {},
            "classes": {},
        },
        "virulence": {
            "profile": {},
            "markers": {},
        },
    }

    for key, value in raw.items():
        if key == "strain":
            continue
        field_name = key.split("__")[-1]
        module_name = "__".join(key.split("__")[0:-1])
        for group in modules.keys():
            if module_name in modules[group]:
                # Code here
                if module_name not in result["modules"]:
                    result["modules"].append(module_name)
                if group == "amr_modules":
                    if field_name in ["truncated_resistance_hits", "spurious_resistance_hits", "resistance_score",
                                      "num_resistance_genes", "num_resistance_classes"]:
                        result["amr"][field_name] = value
                        break
                    result["amr"]["classes"][field_name] = value
                    phenotype = amr_dict[field_name]
                    tag = phenotype["key"]
                    if tag not in result["amr"]['profile'].keys():
                        result["amr"]['profile'][tag] = phenotype
                        result["amr"]['profile'][tag]['resistant'] = False
                        result["amr"]['profile'][tag]['matches'] = '-'
                    if value != '-':
                        result["amr"]['profile'][tag]['resistant'] = True
                        if result["amr"]['profile'][tag]['matches'] == '-':
                            result["amr"]['profile'][tag]['matches'] = value
                        else:
                            result["amr"]['profile'][tag][
                                'matches'] = f'{result["amr"]["profile"][tag]["matches"]};{value}'
                elif group == "virulence_modules":
                    if field_name in ["Yersiniabactin", "YbST", "Colibactin", "CbST", "Aerobactin", "AbST",
                                      "Salmochelin", "SmST", "RmpADC", "RmST", "rmpA2"]:
                        result["virulence"]["profile"][field_name] = value
                    elif field_name.startswith("virulence") or field_name.startswith("spurious"):
                        result["virulence"][field_name] = value
                    else:
                        result["virulence"]["markers"][field_name] = value
                else:
                    result[field_name] = value
                break
        else:
            print(f"Key: {key}, Module: {module_name}, Field: {field_name}, Value: {value}", file=sys.stderr)
            print(f"Unrecognized field {key} in Kleborate output", file=sys.stderr)

    # Clean up the result dictionary
    if not result["amr"]["classes"]:
        del result["amr"]
    if not result["virulence"]["markers"] and not result["virulence"]["profile"]:
        del result["virulence"]

    return result


def main(
        assembly_file: Annotated[
            Path, typer.Argument(
                help="Assembly file in fasta format"
            )],
        species: Annotated[
            Profile, typer.Argument(
                case_sensitive=False,
                help="Specify the Kleborate module set."
            )],
        amr_json: Annotated[
            Path, typer.Option(
                "-a",
                "--amr-map",
                help="JSON format AMR map",
                file_okay=True,
                exists=True,
                dir_okay=False
            )] = "amrMap.json",
        kleborate_version_file: Annotated[
            Path, typer.Option(
                "-k",
                "--kleborate-version",
                help="Kleborate version file",
                file_okay=True,
                exists=True,
                dir_okay=False
            )] = "kleborate_version",
        code_version_file: Annotated[
            Path, typer.Option(
                "-c",
                "--code-version",
                help="Code version file",
                file_okay=True,
                exists=True,
                dir_okay=False
            )] = "code_version",
) -> None:
    config = configs[species]
    # Run kleborate
    run_kleborate(assembly_file, config)

    if not Path(kleborate_version_file).is_file() or not Path(code_version_file).is_file():
        print("Error: Kleborate version and code version files not found", file=sys.stderr)
        sys.exit(1)

    with open(kleborate_version_file, 'r') as v_fh, open(code_version_file, 'r') as c_fh:
        kleborate_version = v_fh.readline().strip()
        code_version = c_fh.readline().strip()

    versions = {"versions": {"kleborate": kleborate_version, "wrapper": code_version}}

    output_filename = f'/tmp/{config.output_filename}'

    # Deal with missing result file.
    if not Path(output_filename).is_file():
        other_filenames = [f'/tmp/{config.output_filename}' for config in configs.values()]
        result = {}
        for other_filename in other_filenames:
            if Path(other_filename).is_file():
                with open(other_filename, 'r') as other_fh:
                    reader = csv.DictReader(other_fh, delimiter='\t')
                    row = next(reader)
                    result["modules"] = ["enterobacterales__species"]
                    result["species"] = row["enterobacterales__species__species"]
                    result["species_match"] = row["enterobacterales__species__species_match"]
                    break
        else:  # If the species is not kosc or kpsc the output file is not created so it needs rerunning.
            run_kleborate(assembly_file, configs.get(Profile.other))
            rerun_output_filename = f"/tmp/{configs.get(Profile.other).output_filename}"
            if not Path(rerun_output_filename).is_file():
                result = {"modules": []} | versions
            else:
                with open(rerun_output_filename, 'r') as result_fh:
                    reader = csv.DictReader(result_fh, delimiter='\t')
                    result = parse_kleborate(next(reader), {}) | versions
        print(json.dumps(result), file=sys.stdout)
        sys.exit(0)

    # Read result file and write as json blob
    with open(output_filename, 'r') as result_fh, open(amr_json, 'r') as js_fh:
        amr_dict = {f"{record['kleborateCode']}_{extension}": record for record in json.load(js_fh) for extension in
                    record['classes']}
        reader = csv.DictReader(result_fh, delimiter='\t')
        result = parse_kleborate(next(reader), amr_dict) | versions

        print(json.dumps(result), file=sys.stdout)


def run_kleborate(assembly_file, config):
    try:
        command = ['kleborate', '-a', str(assembly_file), '-o', '/tmp/', ] + config.flag
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print("Error: Kleborate failed to run", file=sys.stderr)
        print("Command:", e.cmd, file=sys.stderr)
        print("Return code:", e.returncode, file=sys.stderr)
        print("Standard output:", e.stdout, file=sys.stderr)
        print("Standard error:", e.stderr, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    typer.run(main)
