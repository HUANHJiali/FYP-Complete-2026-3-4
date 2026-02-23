from locust import HttpUser, task, between

class ExamSystemUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        self.token = None
        self.login()
    
    def login(self):
        response = self.client.post("/api/sys/login/", {
            "userName": "student",
            "passWord": "123456"
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                self.token = data.get("data", {}).get("token")
    
    @task(5)
    def get_user_info(self):
        if self.token:
            self.client.get(f"/api/sys/info/?token={self.token}", name="/api/sys/info/")
    
    @task(3)
    def get_exams(self):
        if self.token:
            self.client.get(f"/api/exams/page/?token={self.token}&pageIndex=1&pageSize=10", name="/api/exams/page/")
    
    @task(2)
    def get_practises(self):
        if self.token:
            self.client.get(f"/api/practises/page/?token={self.token}&pageIndex=1&pageSize=10", name="/api/practises/page/")
    
    @task(1)
    def get_health(self):
        self.client.get("/api/health/", name="/api/health/")

class AdminUser(HttpUser):
    wait_time = between(2, 5)
    
    def on_start(self):
        self.token = None
        self.login()
    
    def login(self):
        response = self.client.post("/api/sys/login/", {
            "userName": "admin",
            "passWord": "123456"
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                self.token = data.get("data", {}).get("token")
    
    @task(3)
    def get_students(self):
        if self.token:
            self.client.get(f"/api/students/getPageInfos/?token={self.token}&pageIndex=1&pageSize=20", name="/api/students/page/")
    
    @task(2)
    def get_teachers(self):
        if self.token:
            self.client.get(f"/api/teachers/getPageInfos/?token={self.token}&pageIndex=1&pageSize=20", name="/api/teachers/page/")
    
    @task(1)
    def get_logs(self):
        if self.token:
            self.client.get(f"/api/logs/page/?token={self.token}&pageIndex=1&pageSize=50", name="/api/logs/page/")
