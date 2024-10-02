import numpy as np

def calculate(list):
 """Calcule la moyenne, la variance, l'écart type, le maximum, le minimum et la somme des lignes, des colonnes et des éléments dans une matrice 3 x 3.

 Args:
  list: Une liste contenant 9 chiffres.

 Returns:
  Un dictionnaire contenant les résultats.
 """

 # Vérifiez si la liste contient 9 chiffres
 if len(list) != 9:
  raise ValueError("La liste doit contenir 9 chiffres.")

 # Convertir la liste en tableau NumPy 3x3
 matrix = np.array(list).reshape((3, 3))

 # Calculer les statistiques
 mean = np.mean(matrix, axis=0)
 variance = np.var(matrix, axis=0)
 standard_deviation = np.std(matrix, axis=0)
 max = np.max(matrix, axis=0)
 min = np.min(matrix, axis=0)
 sum = np.sum(matrix, axis=0)

 # Calculer les statistiques le long des colonnes
 mean_column = np.mean(matrix, axis=1)
 variance_column = np.var(matrix, axis=1)
 standard_deviation_column = np.std(matrix, axis=1)
 max_column = np.max(matrix, axis=1)
 min_column = np.min(matrix, axis=1)
 sum_column = np.sum(matrix, axis=1)

 # Calculer les statistiques pour la matrice aplatie
 mean_flat = np.mean(matrix)
 variance_flat = np.var(matrix)
 standard_deviation_flat = np.std(matrix)
 max_flat = np.max(matrix)
 min_flat = np.min(matrix)
 sum_flat = np.sum(matrix)

 # Créer le dictionnaire des résultats
 calculations = {
  'mean': [mean.tolist(), mean_column.tolist(), mean_flat],
  'variance': [variance.tolist(), variance_column.tolist(), variance_flat],
  'standard deviation': [standard_deviation.tolist(), standard_deviation_column.tolist(), standard_deviation_flat],
  'max': [max.tolist(), max_column.tolist(), max_flat],
  'min': [min.tolist(), min_column.tolist(), min_flat],
  'sum': [sum.tolist(), sum_column.tolist(), sum_flat]
 }

 return calculations

 


liste_nombres = [1, 2, 3, 4, 5, 6, 7, 8, 9]
calculs = calculate(liste_nombres)
print(calculs)
