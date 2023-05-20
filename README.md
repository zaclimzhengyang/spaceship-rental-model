# Spaceship Rental Model

This repository contains a flask API which takes in a list of contracts.

Each contract has a start time, an end time, and a profit.

We only have one spaceship to rent.

This is a practice on a knapsack problem, where we want to maximize the profits we get by choosing the most optimal contracts.

## Creating a virtual environment

Create a virtual environment with python3.9

```commandline
virtualenv venv -p $(which python3.9)
```

## Activate the virtual environment

```commandline
source venv/bin/activate
```

## Installing requirements into virtual environment

```commandline
pip3 install -r requirements.txt
```

## Spinning up the API service locally

```
export PYTHONPATH=. && python3 main.py
```
