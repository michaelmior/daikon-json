import argparse
import collections
import json
import sys

TYPES = ["java.lang.String", "int", "double", "Map", "None", "boolean"]
ESCAPE = str.maketrans({'"': r"\"", "\n": r"\n", "\r": r"\r"})


def var_type(value):
    if isinstance(value, str):
        return "java.lang.String"
    elif isinstance(value, bool):
        return "boolean"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "double"
    elif isinstance(value, dict):
        return "Map"
    elif isinstance(value, list):
        return var_type(value[0]) + "[]"
    elif value is None:
        return "None"


def value_str(value):
    if isinstance(value, dict):
        return "nonsensical"
    elif isinstance(value, str):
        return '"' + value.translate(ESCAPE) + '"'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif value is None:
        return "null"
    else:
        return str(value)


def process_obj(obj, path="__ROOT__", key=None):
    values = []
    if isinstance(obj, dict):
        values.append((path, key, {}))
        for k in sorted(obj.keys()):
            if key is not None:
                path += "." + key
            values.extend(process_obj(obj[k], path, k))
    elif isinstance(obj, list):
        values.append((path + "." + key + "[]", None, obj))
    else:
        values.append((path, key, obj))

    return values


def run_daikon(infile, dtrace_file):
    dtrace_file.write("decl-version 2.0\n")
    dtrace_file.write("input-language json\n")

    values = []
    for line in infile:
        obj = json.loads(line)
        values.append(process_obj(obj))

    dtrace_file.write("ppt program.point:::POINT\n")
    dtrace_file.write("ppt-type point\n")

    for path, key, value in values[0]:
        if key is None:
            if path.endswith("[]"):
                dtrace_file.write("variable " + path + "\n")
                dtrace_file.write("  var-kind array\n")
                enclosing_path = ".".join(path[:-2].split(".")[:-1])
                dtrace_file.write("  enclosing-var " + enclosing_path + "\n")
            else:
                dtrace_file.write("variable " + path + "\n")
                dtrace_file.write("  var-kind variable\n")
        else:
            dtrace_file.write("variable " + path + "." + key + "\n")
            dtrace_file.write("  var-kind field " + key + "\n")
            dtrace_file.write("  enclosing-var " + path + "\n")

        value_type = var_type(value)
        if value_type.endswith("[]"):
            comp_index = len(TYPES) + TYPES.index(value_type[:-2])
        else:
            comp_index = TYPES.index(value_type)
        dtrace_file.write("  comparability " + str(comp_index) + "\n")
        dtrace_file.write("  dec-type " + value_type + "\n")
        if value_type in ["Map", "None"]:
            dtrace_file.write("  rep-type hashcode\n")
        else:
            dtrace_file.write("  rep-type " + value_type + "\n")

    dtrace_file.write("\n")
    for value_group in values:
        dtrace_file.write("program.point:::POINT\n")
        for path, key, value in value_group:
            if key is None:
                dtrace_file.write(path + "\n")
            else:
                dtrace_file.write(path + "." + key + "\n")
            dtrace_file.write(value_str(value) + "\n")
            dtrace_file.write("1\n")

        dtrace_file.write("\n")
    dtrace_file.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("dtrace_out")
    args = parser.parse_args()

    if args.input == "-":
        infile = sys.stdin
    else:
        infile = open(args.input)

    dtrace_file = open(dtrace_out, "w")

    run_daikon(infile, dtrace_file)

    dtrace_file.close()

    infile.close()


if __name__ == "__main__":
    main()
