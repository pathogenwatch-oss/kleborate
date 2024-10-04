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
        "Klebsiella_pneumo_complex__mlst",
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
        field_name = key.split("__")[-1]
        module_name = key.replace(f"__{field_name}", "")
        for group in modules.keys():
            if module_name in modules[group]:
                # Code here
                if module_name not in result["modules"]:
                    result["modules"].append(module_name)
                if group == "amr_modules":
                    if field_name in ["truncated_resistance_hits", "spurious_resistance_hits", "resistance_score",
                                      "num_resistance_genes", "num_resistance_classes"]:
                        result["amr"][field_name] = value
                        continue
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

    # Read result file and write as json blob
    with (open(f'/tmp/{config.output_filename}', 'r') as result_fh,
          open(amr_json, 'r') as js_fh,
          open(kleborate_version_file, 'r') as v_fh,
          open(code_version_file, 'r') as c_fh):
        kleborate_version = v_fh.readline().strip()
        code_version = c_fh.readline().strip()
        amr_dict = {f"{record['kleborateCode']}_{extension}": record for record in json.load(js_fh) for extension in
                    record['classes']}
        reader = csv.DictReader(result_fh, delimiter='\t')
        result = parse_kleborate(next(reader), amr_dict) | {
            "versions": {"kleborate": kleborate_version, "wrapper": code_version}}
        print(json.dumps(result), file=sys.stdout)

    # amr_profile = dict()
    # amr_profile['profile'] = dict()
    # amr_profile['classes'] = dict()
    #
    # output = dict()
    # output['Kleborate version'] = version
    # output['virulence'] = dict()
    # output['typing'] = dict()
    # output['other'] = dict()
    # output['csv'] = list()
    #
    # for i in range(0, len(top_level_fields)):
    #     output[top_level_fields[i]] = result[i]
    #     output['csv'].append({'set': '', 'field': top_level_fields[i], 'name': top_level_fields[i]})
    #
    # column_counter = len(top_level_fields)
    #
    # for i in range(0, len(virulence_fields)):
    #     output['virulence'][virulence_fields[i]] = result[column_counter]
    #     output['csv'].append({'set': 'virulence', 'field': virulence_fields[i], 'name': virulence_fields[i]})
    #     column_counter += 1
    #
    # for i in range(0, len(typing_fields)):
    #     output['typing'][typing_fields[i]] = result[column_counter]
    #     output['csv'].append({'set': 'typing', 'field': typing_fields[i], 'name': typing_fields[i]})
    #     column_counter += 1
    #
    # amr_cache = set()
    #
    # for i in range(0, len(classes_fields)):
    #     amr_profile['classes'][classes_fields[i]] = result[column_counter]
    #     phenotype = amr_dict[classes_fields[i]]
    #     tag = phenotype['key']
    #     if tag not in amr_profile['profile'].keys():
    #         amr_cache.add(tag)
    #         amr_profile['profile'][tag] = phenotype
    #         amr_profile['profile'][tag]['resistant'] = False
    #         amr_profile['profile'][tag]['matches'] = '-'
    #     if result[column_counter] != '-':
    #         amr_profile['profile'][tag]['resistant'] = True
    #         if amr_profile['profile'][tag]['matches'] == '-':
    #             amr_profile['profile'][tag]['matches'] = result[column_counter]
    #         else:
    #             amr_profile['profile'][tag]['matches'] = amr_profile['profile'][tag]['matches'] + ';' + result[
    #                 column_counter]
    #     output['csv'].append({'set': 'amr', 'field': classes_fields[i], 'name': classes_fields[i]})
    #     column_counter += 1
    #
    # output['amr'] = amr_profile
    # output['amr']['classes']['truncated_resistance_hits'] = result[column_counter]
    # output['csv'].append({'set': 'amr', 'field': 'truncated_resistance_hits', 'name': 'truncated_resistance_hits'})
    #
    # output['amr']['classes']['spurious_resistance_hits'] = result[column_counter + 1]
    # output['csv'].append({'set': 'amr', 'field': 'spurious_resistance_hits', 'name': 'spurious_resistance_hits'})
    # column_counter += 2
    #
    # for i in range(0, len(other_fields)):
    #     output['other'][other_fields[i]] = result[column_counter]
    #     output['csv'].append({'set': 'other', 'field': other_fields[i], 'name': other_fields[i]})
    #     column_counter += 1
    #
    # del output['strain']
    # print(json.dumps(output, separators=(',', ':')), file=sys.stdout)


if __name__ == "__main__":
    typer.run(main)
