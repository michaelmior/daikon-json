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
            values.extend(process_obj(obj[k], path, k))
    else:
        values.append((path, key, obj))

    return values


def run_daikon(infile, decls_file, dtrace_file):
    decls_file.write("decl-version 2.0\n")
    decls_file.write("input-language json\n")

    values = []
    for line in infile:
        obj = json.loads(line)
        values.append(process_obj(obj))

    decls_file.write("ppt program.point:::POINT\n")
    decls_file.write("ppt-type point\n")

    for path, key, value in values[0]:
        if key is None:
            decls_file.write("variable " + path + "\n")
            decls_file.write("  var-kind variable\n")
        else:
            decls_file.write("variable " + path + "." + key + "\n")
            decls_file.write("  var-kind field " + key + "\n")
            decls_file.write("  enclosing-var " + path + "\n")

        value_type = var_type(value)
        decls_file.write("  comparability " + str(TYPES.index(value_type)) + "\n")
        decls_file.write("  dec-type " + value_type + "\n")
        if value_type in ["Map", "None"]:
            decls_file.write("  rep-type hashcode\n")
        else:
            decls_file.write("  rep-type " + value_type + "\n")
    decls_file.close()

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
    parser.add_argument("decls_out")
    parser.add_argument("dtrace_out")
    args = parser.parse_args()

    if args.input == "-":
        infile = sys.stdin
    else:
        infile = open(args.input)

    decls_file = open(decls_out, "w")
    dtrace_file = open(dtrace_out, "w")

    run_daikon(infile, decls_file, dtrace_file)

    decls_file.close()
    dtrace_file.close()

    infile.close()


if __name__ == "__main__":
    main()
