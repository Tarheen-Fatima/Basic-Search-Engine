import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import re
import math

class SearchEngine:
    def __init__(self):
        self.index = defaultdict(list)
        self.doc_lengths = defaultdict(float)

    def index_page(self, url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            text = soup.get_text()
            words = re.findall(r'\w+', text.lower())
            word_freq = defaultdict(int)
            for word in words:
                self.index[word].append(url)
                word_freq[word] += 1
            doc_length = sum(word_freq.values())
            for word, freq in word_freq.items():
                tf = freq / doc_length
                self.doc_lengths[url] += tf ** 2
        except Exception as e:
            print("Error indexing page:", e)

    def search(self, query):
        query_words = re.findall(r'\w+', query.lower())
        query_vector = defaultdict(float)
        for word in query_words:
            query_vector[word] += 1
        query_length = math.sqrt(sum(value ** 2 for value in query_vector.values()))

        doc_scores = defaultdict(float)
        for word, query_tf in query_vector.items():
            if word in self.index:
                idf = math.log(len(self.doc_lengths) / len(self.index[word]))
                for doc_url in set(self.index[word]):  # Using set to avoid counting duplicate documents
                    tf = 1 + math.log(self.index[word].count(doc_url))
                    tf_idf = tf * idf
                    doc_scores[doc_url] += tf_idf * query_tf

        for doc_url, score in doc_scores.items():
          doc_scores[doc_url] = abs(doc_scores[doc_url])
          doc_scores[doc_url] /= math.sqrt(self.doc_lengths[doc_url]) * query_length


        sorted_results = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results

# Example usage:
search_engine = SearchEngine()
search_engine.index_page("https://en.wikipedia.org/wiki/Web_scraping")
search_engine.index_page("https://en.wikipedia.org/wiki/Computer_vision")
search_engine.index_page("https://en.wikipedia.org/wiki/Text_processing")

query = "Python for scraping"
results = search_engine.search(query)
print("Search results for query:", query)
for i, (result, relevance) in enumerate(results, start=1):
    print(f"{i}. {result} - Relevance: {relevance:.4f}")