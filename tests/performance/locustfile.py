from locust import HttpUser, between, task


class EnterpriseAIUser(HttpUser):
    wait_time = between(1, 3)

    @task(4)
    def health(self):
        self.client.get("/system/health")

    @task(2)
    def root(self):
        self.client.get("/")

    @task(2)
    def cache_health(self):
        self.client.get("/api/cache/health")

    @task(1)
    def docs_schema(self):
        self.client.get("/openapi.json")
