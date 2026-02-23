from locust import HttpUser, task, between

class AuthenticatedUser(HttpUser):
    wait_time = between(0.5, 2)
    
    def on_start(self):
        self.token = None
        response = self.client.post("/api/sys/login/", {
            "userName": "student",
            "passWord": "123456"
        }, name="login_once")
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                self.token = data.get("data", {}).get("token")
    
    @task(10)
    def get_user_info(self):
        if self.token:
            self.client.get(f"/api/sys/info/?token={self.token}", name="/api/sys/info/")
    
    @task(5)
    def get_exams(self):
        if self.token:
            self.client.get(f"/api/exams/page/?token={self.token}&pageIndex=1&pageSize=10", name="/api/exams/page/")
    
    @task(5)
    def get_practises(self):
        if self.token:
            self.client.get(f"/api/practises/page/?token={self.token}&pageIndex=1&pageSize=10", name="/api/practises/page/")
    
    @task(3)
    def get_health(self):
        self.client.get("/api/health/", name="/api/health/")
    
    @task(2)
    def get_colleges(self):
        if self.token:
            self.client.get(f"/api/colleges/all/?token={self.token}", name="/api/colleges/all/")
    
    @task(2)
    def get_grades(self):
        if self.token:
            self.client.get(f"/api/grades/all/?token={self.token}", name="/api/grades/all/")
