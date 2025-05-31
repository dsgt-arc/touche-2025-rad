import json


def generate_tsv_from_jsonl(jsonl_file_path):
    """
    Extracts distinct topics from a JSONL file and generates TSV output.

    Args:
        jsonl_file_path (str): The path to the input JSONL file.

    Returns:
        str: A string containing the TSV data.
    """
    distinct_topics = set()

    try:
        with open(jsonl_file_path, "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, 1):
                try:
                    data = json.loads(line)
                    if "debate" in data and isinstance(data["debate"], list):
                        for turn in data["debate"]:
                            if "arguments" in turn and isinstance(
                                turn["arguments"], list
                            ):
                                for argument in turn["arguments"]:
                                    if "topic" in argument and argument["topic"]:
                                        distinct_topics.add(argument["topic"])
                except json.JSONDecodeError:
                    print(
                        f"Warning: Could not decode JSON on line {line_number}: {line.strip()}"
                    )
                except KeyError as e:
                    print(
                        f"Warning: Missing key {e} on line {line_number}: {line.strip()}"
                    )
                except TypeError as e:
                    print(
                        f"Warning: Type error {e} on line {line_number} (likely unexpected data structure): {line.strip()}"
                    )

    except FileNotFoundError:
        return "Error: File not found."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

    if not distinct_topics:
        return "TOPIC_DESCRIPTION\tUSER\n# No topics found"

    tsv_output_lines = ["TOPIC_DESCRIPTION\tUSER"]
    for topic in sorted(list(distinct_topics)):
        tsv_output_lines.append(f"{topic}\tbase-user")

    return "\n".join(tsv_output_lines)


if __name__ == "__main__":
    file_path = "/Users/conorjohnston/Downloads/touche25-rad-cmv-debates.jsonl"
    tsv_data = generate_tsv_from_jsonl(file_path)

    print(tsv_data)

    output_file_path = "data/debate_topics.tsv"
    try:
        with open(output_file_path, "w", encoding="utf-8") as outfile:
            outfile.write(tsv_data)
        print(f"\nTSV data successfully written to {output_file_path}")
    except IOError:
        print(f"Error: Could not write to file {output_file_path}")
