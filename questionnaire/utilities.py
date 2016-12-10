import random
from datetime import datetime
from django.db.models import F


def pick_random_clients(clients):
    if clients.filter(randomised=False):
        selected_clients = random.sample(clients, len(clients) / 2)
        for client in clients:
            client.randomised = True
            client.save()
        for client in selected_clients:
            client.random_selection = True
            client.save()
    else:
        selected_clients = clients.filter(randomised=True).filter(random_selection=True)
    return selected_clients
