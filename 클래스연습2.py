# Developer클래스를 정의하면서
# id, name, skill 변수가 있고,
# printInfo() 메서드가 있다.

class Developer:    
    def __init__(self, id, name, skill):
        self.id = id
        self.name = name
        self.skill = skill

    def printInfo(self):
        print(f"ID: {self.id}, Name: {self.name}, Skill: {self.skill}")

