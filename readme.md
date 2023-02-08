Première utilisation:

-Lancer le script BD.py afin de créer le fichier sqlite.
-Modifier le fichier bot-devoir.py, la ligne "await client.start('TOKEN')" et mettre le token du bot.
-Installer les modules qui ne seraient pas installé, ex: discord.py.
-Modifier la fonction "def is_authorized(ctx)" afin d'autoriser certaines personnes ou rôles à executer les commandes "admins", spécifié avec les IDs.

Notes: 
-S'assurer que le bot dans le dev portal a les bon "intents", cocher tout pour être sûr.
-Donner les bonnes perms au bot (Il doit pouvoir lire les channels, créer des embed, fetch des anciens messages etc..).