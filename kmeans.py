from sklearn.cluster import KMeans
import numpy as np

import matplotlib
matplotlib.use('Agg')

import word_analyzer
import matplotlib.pyplot as plt

def fitKMeans(list_words):
    vectors = []
    for word in list_words:
        avg_syllable_len=0
        word_len = len(word);
        syllables = word_analyzer.syllables(word)
        for syllable in syllables:
             avg_syllable_len+=len(syllable)
        avg_syllable_len+=1
        syllab_count = len(syllables)+1;
        vectors.append([word_len/avg_syllable_len, avg_syllable_len/syllab_count])
        if(word_len/avg_syllable_len>0.8)and(avg_syllable_len/syllab_count>3):
              print(word)
    array = np.array(vectors)

    kmeans = KMeans(n_clusters=3, random_state=0).fit(array)
    print(kmeans.labels_)
    print(kmeans.predict([[0, 0], [4, 4]]))
    print(kmeans.cluster_centers_)

    # Step size of the mesh. Decrease to increase the quality of the VQ.
    h = .02  # point in the mesh [x_min, x_max]x[y_min, y_max].

    # Plot the decision boundary. For that, we will assign a color to each
    x_min, x_max = array[:, 0].min() - 1, array[:, 0].max() + 1
    y_min, y_max = array[:, 1].min() - 1, array[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

    # Obtain labels for each point in mesh. Use last trained model.
    Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    plt.figure(1)
    plt.clf()
    plt.imshow(Z, interpolation='nearest',
               extent=(xx.min(), xx.max(), yy.min(), yy.max()),
               cmap=plt.cm.Paired,
               aspect='auto', origin='lower')

    plt.plot(array[:, 0], array[:, 1], 'k.', markersize=2)

    # Plot the centroids as a white X
    centroids = kmeans.cluster_centers_
    plt.scatter(centroids[:, 0], centroids[:, 1],
                marker='x', s=169, linewidths=3,
                color='w', zorder=10)
    plt.title('K-means clustering on candidate words data (Word lengt, number of syllables)\n'
              'Centroids are marked with white cross')
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.xticks(())
    plt.yticks(())
    plt.savefig('plot.png')
#   plt.show()
