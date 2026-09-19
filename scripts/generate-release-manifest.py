import argparse
import subprocess
import re
from collections import defaultdict


def get_changed_files(base, head):
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-status",
            base,
            head,
            "--",
            "force-app/main/default",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip().splitlines()


def add_metadata(metadata, metadata_type, member):
    metadata[metadata_type].add(member)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    changed_files = get_changed_files(args.base, args.head)

    metadata = defaultdict(set)
    excluded = []

    for line in changed_files:
        if not line:
            continue

        parts = line.split("\t")
        status = parts[0]
        file_path = parts[-1]

        relative_path = file_path.replace(
            "force-app/main/default/",
            "",
            1,
        )

        # ---------------------------------------------------------
        # Lightning Web Components
        # ---------------------------------------------------------
        lwc_match = re.match(
            r"lwc/([^/]+)/",
            relative_path,
        )

        if lwc_match:
            component_name = lwc_match.group(1)

            if status == "D":
                raise SystemExit(
                    f"Deletion detected for LWC '{component_name}'. "
                    "Destructive changes are not handled by this demo yet."
                )

            add_metadata(
                metadata,
                "LightningComponentBundle",
                component_name,
            )
            continue

        # ---------------------------------------------------------
        # Apex Classes
        # ---------------------------------------------------------
        apex_match = re.match(
            r"classes/([^/]+)\.(cls|cls-meta\.xml)$",
            relative_path,
        )

        if apex_match:
            class_name = apex_match.group(1)

            if status == "D":
                raise SystemExit(
                    f"Deletion detected for Apex class '{class_name}'. "
                    "Destructive changes are not handled by this demo yet."
                )

            add_metadata(
                metadata,
                "ApexClass",
                class_name,
            )
            continue

        # ---------------------------------------------------------
        # Apex Triggers
        # ---------------------------------------------------------
        trigger_match = re.match(
            r"triggers/([^/]+)\.(trigger|trigger-meta\.xml)$",
            relative_path,
        )

        if trigger_match:
            trigger_name = trigger_match.group(1)

            if status == "D":
                raise SystemExit(
                    f"Deletion detected for Apex trigger '{trigger_name}'. "
                    "Destructive changes are not handled by this demo yet."
                )

            add_metadata(
                metadata,
                "ApexTrigger",
                trigger_name,
            )
            continue

        # ---------------------------------------------------------
        # Flows
        # ---------------------------------------------------------
        flow_match = re.match(
            r"flows/([^/]+)\.flow-meta\.xml$",
            relative_path,
        )

        if flow_match:
            flow_name = flow_match.group(1)

            if status == "D":
                raise SystemExit(
                    f"Deletion detected for Flow '{flow_name}'. "
                    "Destructive changes are not handled by this demo yet."
                )

            add_metadata(
                metadata,
                "Flow",
                flow_name,
            )
            continue

        # ---------------------------------------------------------
        # Permission Sets
        # ---------------------------------------------------------
        permission_set_match = re.match(
            r"permissionsets/([^/]+)\.permissionset-meta\.xml$",
            relative_path,
        )

        if permission_set_match:
            permission_set_name = permission_set_match.group(1)

            if status == "D":
                raise SystemExit(
                    f"Deletion detected for Permission Set "
                    f"'{permission_set_name}'. "
                    "Destructive changes are not handled by this demo yet."
                )

            add_metadata(
                metadata,
                "PermissionSet",
                permission_set_name,
            )
            continue

        # ---------------------------------------------------------
        # Page Layouts
        # ---------------------------------------------------------
        layout_match = re.match(
            r"layouts/([^/]+)\.layout-meta\.xml$",
            relative_path,
        )

        if layout_match:
            layout_name = layout_match.group(1)

            if status == "D":
                raise SystemExit(
                    f"Deletion detected for Layout '{layout_name}'. "
                    "Destructive changes are not handled by this demo yet."
                )

            add_metadata(
                metadata,
                "Layout",
                layout_name,
            )
            continue

        # ---------------------------------------------------------
        # FlexiPages
        # ---------------------------------------------------------
        flexipage_match = re.match(
            r"flexipages/([^/]+)\.flexipage-meta\.xml$",
            relative_path,
        )

        if flexipage_match:
            flexipage_name = flexipage_match.group(1)

            if status == "D":
                raise SystemExit(
                    f"Deletion detected for FlexiPage "
                    f"'{flexipage_name}'. "
                    "Destructive changes are not handled by this demo yet."
                )

            add_metadata(
                metadata,
                "FlexiPage",
                flexipage_name,
            )
            continue

        # ---------------------------------------------------------
        # Custom Objects / Fields
        # ---------------------------------------------------------
        object_match = re.match(
            r"objects/([^/]+)/",
            relative_path,
        )

        if object_match:
            object_name = object_match.group(1)

            excluded.append(
                f"{file_path} "
                f"(CustomObject/CustomField: {object_name})"
            )
            continue

        # ---------------------------------------------------------
        # Unsupported metadata
        # ---------------------------------------------------------
        excluded.append(
            f"{file_path} (unsupported metadata type)"
        )

    if not metadata:
        raise SystemExit(
            "No automatically deployable Salesforce metadata changes found."
        )

    package_xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<Package xmlns="http://soap.sforce.com/2006/04/metadata">',
    ]

    for metadata_type in sorted(metadata):
        package_xml.append("    <types>")

        for member in sorted(metadata[metadata_type]):
            package_xml.append(
                f"        <members>{member}</members>"
            )

        package_xml.append(f"        <name>{metadata_type}</name>")
        package_xml.append("    </types>")

    package_xml.append("    <version>65.0</version>")
    package_xml.append("</Package>")

    with open(args.output, "w", encoding="utf-8") as file:
        file.write("\n".join(package_xml) + "\n")

    print("Generated package.xml:")
    print()
    print("\n".join(package_xml))

    if excluded:
        print()
        print("===== Excluded from automated deployment =====")

        for item in excluded:
            print(f"- {item}")

        print("==============================================")


if __name__ == "__main__":
    main()