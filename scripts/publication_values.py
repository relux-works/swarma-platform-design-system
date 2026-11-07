"""Batch publication decoding through real CommonMark and HTML engines."""

import json
import os
from pathlib import Path
import subprocess
from xml.etree import ElementTree

ENGINE = Path(__file__).with_name("publication-engine.mjs")
MARKUP = {".md", ".html", ".htm", ".svg", ".css", ".yaml", ".yml"}


def documents(records, *, rendered=False, root=None):
    payload, locations, output = [], [], {}
    for path, source in records:
        suffix = path.suffix.lower()
        item = {"suffix": suffix, "source": source, "path": str(path.resolve())}
        if suffix == ".svg":
            try:
                xml_root = ElementTree.fromstring(source)
                item["xml"] = {
                    "text": "".join(xml_root.itertext()),
                    "attributes": [(name.rsplit("}", 1)[-1], value) for node in xml_root.iter() for name, value in node.attrib.items()],
                    "styles": ["".join(node.itertext()) for node in xml_root.iter() if node.tag.rsplit("}", 1)[-1] == "style"],
                }
            except ElementTree.ParseError:
                output[path] = {"error": "publication-decode"}
                continue
        payload.append(item)
        locations.append(path)
    if payload:
        environment = {key: value for key, value in os.environ.items() if key != "IDENT_DENY_TOKENS"}
        # Bound browser work so repository size cannot exhaust one engine deadline.
        batch_size = 8 if rendered else len(payload)
        for start in range(0, len(payload), batch_size):
            batch = payload[start:start + batch_size]
            result = subprocess.run(["node", str(ENGINE)], input=json.dumps({"documents": batch, "rendered": rendered,
                                    "root": str(root.resolve()) if root else None}), text=True,
                                    capture_output=True, timeout=60, env=environment)
            # Never forward child stderr, JSON errors or exception payloads into a diagnostic.
            if result.returncode:
                raise ValueError("publication engine failed")
            values = json.loads(result.stdout)
            if not isinstance(values, list) or len(values) != len(batch):
                raise ValueError("invalid publication result")
            output.update(zip(locations[start:start + batch_size], values))
    return output


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from strings(item)
