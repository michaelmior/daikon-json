# Daikon JSON

This repository implements a JSON front end for the [Daikon](https://plse.cs.washington.edu/daikon/) invariant detector.
It allows the detection of invariants across a collection of JSON documents in [JSON Lines](https://jsonlines.org/) format.

From an input JSON file, it will generate both a declarations file and a trace file that can be used as input to Daikon.
It can be run as in the following example:

    python daikon_json.py input.json input.decls input.dtrace
    java -cp daikon.jar daikon.Daikon input.decls input.dtrace
