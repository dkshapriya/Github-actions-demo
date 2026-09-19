import argparse
import subprocess
import re
from collections import defaultdict


def get_changed_files(base, head):
    result = subprocess.run(
        ["git", "diff", "--name-status", base, head, "--", "force-app/main/default"],
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip().splitlines()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    changed_files = get_changed_files(args.base, args.head)

    metadata = defaultdict(set)

    for line in changed_files:
        if not line:
            continue

        parts = line.split("\t")
        status = parts[0]

        # Handle normal changes: A, M, D
        file_path = parts[-1]

        # LWC
        lwc_match = re.match(
            r"force-app/main/default/lwc/([^/]+)/",
            file_path,
        )

        if lwc_match:
            component_name = lwc_match.group(1)

            if status == "D":
                raise SystemExit(
                    f"Deletion detected for LWC '{component_name}'. "
                    "Destructive changes are not handled by this demo yet."
                )

            metadata["LightningComponentBundle"].add(component_name)
            continue

        # Apex Classes
        apex_match = re.match(
            r"force-app/main/default/classes/([^/]+)\.(cls|cls-meta\.xml)$",
            file_path,
        )

        if apex_match:
            class_name = apex_match.group(1)

            if status == "D":
                raise SystemExit(
                    f"Deletion detected for Apex class '{class_name}'. "
                    "Destructive changes are not handled by this demo yet."
                )

            metadata["ApexClass"].add(class_name)
            continue

        raise SystemExit(
            f"Unsupported Salesforce metadata path detected: {file_path}"
        )

    if not metadata:
        raise SystemExit("No Salesforce metadata changes found.")

    package_xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<Package xmlns="http://soap.sforce.com/2006/04/metadata">',
    ]

    for metadata_type in sorted(metadata):
        package_xml.append("    <types>")

        for member in sorted(metadata[metadata_type]):
            package_xml.append(f"        <members>{member}</members>")

        package_xml.append(f"        <name>{metadata_type}</name>")
        package_xml.append("    </types>")

    package_xml.append("    <version>65.0</version>")
    package_xml.append("</Package>")

    with open(args.output, "w", encoding="utf-8") as file:
        file.write("\n".join(package_xml) + "\n")

    print("Generated package.xml:")
    print()
    print("\n".join(package_xml))


if __name__ == "__main__":
    main()