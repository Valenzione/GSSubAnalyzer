# from sklearn.cluster import KMeans
import numpy as np

import word_analyzer


def fitKMeans(list_words):
    vectors = []
    for word in list_words:
        word_len = len(word);
        syllables = word_analyzer.syllables(word)
        syllab_count = len(syllables);
        vectors.append([word_len, syllab_count])
    array = np.array(vectors)
    print(array)

# kmeans = KMeans(n_clusters=2, random_state=0).fit(X)
# print(kmeans.labels_)
# print(kmeans.predict([[0, 0], [4, 4]]))
# print(kmeans.cluster_centers_)
