#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2026 Rufat Nuriyev, https://rufat.top/, https://dev256.com/

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__author__ = "Rufat Nuriyev"
__copyright__ = "Copyright (c) 2026 Rufat Nuriyev"
__credits__ = ["Rufat Nuriyev"]
__maintainer__ = "Rufat Nuriyev"
__email__ = "info@dev256.com"
__uri__ = "https://rufat.top/"
__urls__ = ["https://rufat.top/", "https://dev256.com/"]
__license__ = "MIT"
__version__ = "1.2"


import datetime
import os
from os import listdir
from typing import List

import yaml


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

    def save(self, path="results"):
        if not os.path.exists(path):
            os.makedirs(path)

        with open(
            os.path.join(path, f"{self.name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"),
            "w",
            encoding="utf-8",
        ) as f:
            for search, res in zip(self.search_words, self.data_res):
                f.write("----" + "\n" + f"{search}" + "\n")
                for line in res:
                    f.write(line + "\n")


def load_words_set(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    words_set = config.get("words_set")
    if not isinstance(words_set, dict):
        raise ValueError("Invalid config.yaml: `words_set` must be a mapping")
    print(f"words_set: {words_set}")
    return words_set


def main():
    words_set = load_words_set()
    for name, words in words_set.items():
        a = Analyze(name, words)
        path = r"results"  # path/to
        files = [f for f in listdir(path) if os.path.isfile(os.path.join(path, f))]
        files = filter(lambda f: f.endswith(".csv"), files)
        for filename in files:
            a.load_file(path, filename)

        a.search()
        a.save()


if __name__ == "__main__":
    main()
