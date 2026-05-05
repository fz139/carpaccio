import datetime
import os
from os import listdir
from typing import List


class Analyze:
    def __init__(self, name: str, search_words: List):
        self.name: str = name
        self.search_words: List = search_words
        self.data_src = []
        self.data_res = []

    def load_file(self, path, filename):
        filename_full = os.path.join(path, filename)
        self.data_src += [line.strip() for line in open(filename_full, encoding="utf-8")]

    def search(self):
        # print(self.data_src)
        self.data_res = [[] for _ in range(len(self.search_words))]
        for l in self.data_src:
            for i, group in enumerate(self.search_words):
                if sum([1 for w in group if w in l]) > 0:
                    self.data_res[i].append(l)

    def save(self):
        with open(f"{self.name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w", encoding="utf-8") as f:
            for search, res in zip(self.search_words, self.data_res):
                f.write("----" + "\n")
                f.write(f"{search}" + "\n")
                for line in res:
                    f.write(line + "\n")


words_set = {
    "trackers": [
        ["rutracker.org"],
        ["nnm-club", "nnmclub"],
    ],
    "vpn": [
        ["vpn"],
    ],
    "hosting": [
        ["hosting"],
    ],
    "vps": [
        ["vps"],
    ],
}


def main():
    for name, words in words_set.items():
        a = Analyze(name, words)
        path = r".\\"  # path/to
        files = [f for f in listdir(path) if os.path.isfile(os.path.join(path, f))]
        files = filter(lambda f: f.endswith(".csv"), files)
        for filename in files:
            a.load_file(path, filename)

        a.search()
        a.save()


main()
