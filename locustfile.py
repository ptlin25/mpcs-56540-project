import os
import random
from locust import HttpUser, LoadTestShape, between, task, stats

stats.PERCENTILES_TO_CHART = [0.50, 0.95, 0.99]

# seeded with seed_test() in seeder.py
NUM_USERS = 200                      # user1 … user200, password = PASSWORD
PASSWORD = "password"
POLL_IDS = list(range(1, 30))       # polls 1–29 are active
CLOSED_POLL_ID = 30                 # poll 30 is inactive (to check results page)


LOAD_TEST = [
    {"duration": 30, "users": 30, "spawn_rate": 1},     # ramp up to 30 VUs
    {"duration": 90, "users": 30, "spawn_rate": 1},     # hold at peak load
    {"duration": 120, "users": 0, "spawn_rate": 1},     # ramp down
]

SPIKE_TEST = [
    {"duration": 30, "users": 30, "spawn_rate": 1},     # baseline
    {"duration": 40, "users": 100, "spawn_rate": 50},   # spike
    {"duration": 60, "users": 100, "spawn_rate": 50},   # hold spike briefly
    {"duration": 70, "users": 30, "spawn_rate": 50},    # back to baseline
    {"duration": 120, "users": 30, "spawn_rate": 1},    # observe recovery
    {"duration": 150, "users": 0, "spawn_rate": 1},
]


class PollsUser(HttpUser):
    host = "http://127.0.0.1:8000"
    wait_time = between(1, 3)

    def on_start(self):
        idx = random.randint(1, NUM_USERS)
        resp = self.client.get("/accounts/login/", name="GET login")
        csrf = resp.cookies.get("csrftoken", "")
        self.client.post(
            "/accounts/login/",
            data={
                "username": f"user{idx}",
                "password": PASSWORD,
                "csrfmiddlewaretoken": csrf,
            },
            name="POST login",
            allow_redirects=True,
        )

    @task(40)
    def poll_list(self):
        self.client.get("/polls/list/", name="GET /polls/list/")

    @task(30)
    def poll_detail(self):
        poll_id = random.choice(POLL_IDS)
        self.client.get(f"/polls/{poll_id}/", name="GET /polls/{id}/")

    @task(20)
    def poll_vote(self):
        poll_id = random.choice(POLL_IDS)
        csrf = self.client.cookies.get("csrftoken", "")
        # poll n (1-indexed) has choices at IDs (n-1)*2+1 and (n-1)*2+2
        base = (poll_id - 1) * 2 + 1
        choice_id = random.choice([base, base + 1])
        self.client.post(
            f"/polls/{poll_id}/vote/",
            data={"choice": choice_id, "csrfmiddlewaretoken": csrf},
            name="POST /polls/{id}/vote/",
        )

    @task(10)
    def poll_results(self):
        self.client.get(
            f"/polls/{CLOSED_POLL_ID}/",
            name="GET /polls/{closed}/ [results]",
        )


class StagesShape(LoadTestShape):
    stages = SPIKE_TEST if os.environ.get("LOCUST_TEST_PROFILE") == "spike" else LOAD_TEST

    def tick(self):
        t = self.get_run_time()
        for stage in self.stages:
            if t <= stage["duration"]:
                return stage["users"], stage["spawn_rate"]
        return None
