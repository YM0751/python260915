# Person은 사람 한 명을 표현하기 위한 기본 설계도입니다.
# 설계도에는 사람의 번호(id)와 이름(name)을 적어 둡니다.
class Person:
    # __init__은 새 사람을 만들 때 한 번 자동으로 실행됩니다.
    # id와 name은 새 사람을 만들 때 바깥에서 받아 옵니다.
    def __init__(self, id, name):
        # self는 지금 만들고 있는 바로 그 사람을 가리킵니다.
        self.id = id
        self.name = name

    # printInfo는 사람의 정보를 화면에 보여 주는 기능입니다.
    def printInfo(self):
        print(f"ID: {self.id}, Name: {self.name}")


# Manager는 Person을 물려받은 관리자 설계도입니다.
# Person의 id와 name을 그대로 사용하면서 title도 하나 더 가집니다.
class Manager(Person):
    # 관리자를 만들 때 번호, 이름, 직책을 받습니다.
    def __init__(self, id, name, title):
        # super()는 부모인 Person의 __init__을 불러옵니다.
        # 그래서 id와 name을 다시 작성하지 않아도 됩니다.
        super().__init__(id, name)
        # 관리자의 직책을 title이라는 이름표에 넣습니다.
        self.title = title

    # 관리자는 사람 정보와 직책을 함께 보여 줍니다.
    def printInfo(self):
        print(f"ID: {self.id}, Name: {self.name}, Title: {self.title}")


# Employee는 Person을 물려받은 직원 설계도입니다.
# Person의 id와 name을 사용하면서 skill도 하나 더 가집니다.
class Employee(Person):
    # 직원을 만들 때 번호, 이름, 잘하는 일을 받습니다.
    def __init__(self, id, name, skill):
        # 부모 Person에게 번호와 이름을 맡겨서 저장합니다.
        super().__init__(id, name)
        # 직원이 잘하는 일을 skill이라는 이름표에 넣습니다.
        self.skill = skill

    # 직원은 사람 정보와 잘하는 일을 함께 보여 줍니다.
    def printInfo(self):
        print(f"ID: {self.id}, Name: {self.name}, Skill: {self.skill}")


# 여러 사람을 한 줄씩 꺼내 볼 수 있도록 상자(리스트)에 넣습니다.
people = [
    # Person으로 만든 일반 사람 3명입니다.
    Person(1, "김민수"),
    Person(2, "이영희"),
    Person(3, "박준호"),
    # Manager로 만든 관리자 3명입니다.
    Manager(4, "최지훈", "팀장"),
    Manager(5, "정수진", "부장"),
    Manager(6, "강현우", "과장"),
    # Employee로 만든 직원 4명입니다.
    Employee(7, "윤서연", "Python"),
    Employee(8, "한지민", "Java"),
    Employee(9, "오세훈", "Database"),
    Employee(10, "임채원", "Web Development"),
]

# people 상자에서 사람을 한 명씩 꺼냅니다.
for person in people:
    # 꺼낸 사람의 종류에 맞는 printInfo가 자동으로 실행됩니다.
    person.printInfo()