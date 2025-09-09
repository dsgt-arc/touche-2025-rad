import csv
import random
import argparse


def extract_random_topics(input_tsv_path, output_tsv_path, num_topics):
    """
    Extracts a specified number of random debate topics from an input TSV file
    and writes them to an output TSV file.

    Args:
        input_tsv_path (str): Path to the input TSV file.
        output_tsv_path (str): Path to the output TSV file.
        num_topics (int): The number of random topics to extract.
    """
    try:
        with open(input_tsv_path, "r", newline="", encoding="utf-8") as infile:
            reader = csv.reader(infile, delimiter="\t")
            header = next(reader)
            all_topics = list(reader)

        if not all_topics:
            print("Input TSV file is empty (aside from header) or header is missing.")
            return

        if num_topics <= 0:
            print("Number of topics to extract must be a positive integer.")
            with open(output_tsv_path, "w", newline="", encoding="utf-8") as outfile:
                writer = csv.writer(outfile, delimiter="\t")
                writer.writerow(header)
            return

        if num_topics >= len(all_topics):
            selected_topics = all_topics
            print(
                f"Requested {num_topics} topics, but only {len(all_topics)} are available. Selecting all."
            )
        else:
            selected_topics = random.sample(all_topics, num_topics)

        with open(output_tsv_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.writer(outfile, delimiter="\t")
            writer.writerow(header)
            writer.writerows(selected_topics)

        print(
            f"Successfully extracted {len(selected_topics)} random topics to {output_tsv_path}"
        )

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_tsv_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract N random debate topics from a TSV file."
    )
    parser.add_argument(
        "num_topics", type=int, help="Number of random topics to extract."
    )
    parser.add_argument("output_file", type=str, help="Path to the output TSV file.")
    parser.add_argument(
        "--input_file",
        type=str,
        default="data/debate_topics.tsv",
        help="Path to the input TSV file (default: data/debate_topics.tsv)",
    )

    args = parser.parse_args()

    extract_random_topics(args.input_file, args.output_file, args.num_topics)
