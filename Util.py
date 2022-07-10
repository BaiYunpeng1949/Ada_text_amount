def read_from_file(path_text):
    # Read materials from a text file. While the texts are all stacked up in one line.
    with open(path_text) as f:
        texts = f.read()
    return texts
