- Première utilisation:

  - Modifier dans le fichier bot-devoir.py les variables "role_ids", "list_users" et TOKEN.
    - role_ids est une liste d'identifiant de role qui ont l'autorisation de modifier la base de données.
    - list_users est la même chose mais avec l'identifiant d'un utilisateur.
    - TOKEN est le token du bot.
    - interval peut aussi être modifié, mais pas en dessous de ~5 secondes
  - Installer les modules qui ne seraient pas installé, ex: discord.py.

- Notes:

  - S'assurer que le bot dans le dev portal a les bon "intents", cocher tout pour être sûr.
  - Donner les bonnes perms au bot (Il doit pouvoir lire les channels, créer des embed, fetch des anciens messages etc..).
  - Commandes : $help (modifiable dans le code) - $help bd - $help agenda
  - Garantis de fonctionner sur Linux, sur la version 3.9.2 de python et avec le module discord.py en version 2.0.0 (Versions précédentes discord non compatibles)
  - Pour la commande "$agenda [channel] [link]", il faut utiliser un lien e-learn appartenant à un élève dans la bonne section.

- Export calendrier e-learn :

Se rendre ici : https://learn-technique.helmo.be/calendar/export.php

Avec ces paramètres : (version e-learn début 2023, à voir si ça va changer avec l'update prévue)
![image](https://github.com/ThowZzy/Bot-Devoirs/assets/61882536/d1e3bc6a-ad7b-49f0-a858-785cf8503905)
