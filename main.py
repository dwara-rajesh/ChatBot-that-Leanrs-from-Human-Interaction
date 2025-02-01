import json
import sys
import random
from difflib import get_close_matches
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QPlainTextEdit, QHBoxLayout, QScrollArea, QLabel,QLineEdit
from PyQt5.QtCore import QTimer, Qt

class ChatbotUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Chatbot UI')
        self.showMinimized()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.label = QPlainTextEdit("Bot: I want to learn your language. Teach me please. Ask me a question and let us see if I know the answer. You may type 'quit' to stop teaching me\n")
        self.label.setReadOnly(True)  # Set it to read-only to prevent user input
        #self.label.setGeometry(10,10,1800,900)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.label)

        self.text = QLineEdit()
        self.text.setFixedHeight(50)
        self.send_button = QPushButton('Send')
        self.send_button.setFixedHeight(50)
        self.text.returnPressed.connect(self.on_send_clicked)
        self.send_button.clicked.connect(self.on_send_clicked)
        
        self.sendlayout = QHBoxLayout()
        self.sendlayout.addWidget(self.text)
        self.sendlayout.addWidget(self.send_button)

        self.title = QLabel("LearniChat - A chatbot that learns from users")
        self.title.setAlignment(Qt.AlignCenter)

        self.mainlayout = QVBoxLayout()
        self.mainlayout.addWidget(self.title)
        self.mainlayout.addWidget(self.label)
        self.mainlayout.addLayout(self.sendlayout)

        self.central_widget.setLayout(self.mainlayout)
        
    def on_send_clicked(self):
        self.userinput = self.text.text()
        self.text.clear()
        if self.userinput == "":
            newtext = "Bot: Enter a valid question\n"
            self.updatelabel(newtext)
        else:
            self.text.returnPressed.disconnect()
            self.send_button.clicked.disconnect()
            newtext = "You: " + self.userinput + "\n"
            self.updatelabel(newtext)
            if self.userinput == "quit":
                self.quitbot()
            else:
                self.knowledge_base = self.loadknowledgebase("knowledgebase.json") #loads memory
                self.best_match = self.bestmatches(self.userinput, (q["question"] for q in self.knowledge_base["questions"])) #find the best matches for user question in memory
                if self.best_match:
                    answer = self.bestresponse(self.best_match, self.knowledge_base) #if best match found, respond with an answer
                    if answer == "":
                        newtext = "Bot: This question is stored in my memory but you didn't teach me how to answer it. So teach me please or type 'skip'\n" #requests for synonymous answers
                        self.updatelabel(newtext)
                        self.questionexists = True
                        self.text.returnPressed.connect(self.getnewanswer)
                        self.send_button.clicked.connect(self.getnewanswer)
                    else:
                        newtext = "Bot: " + answer + "\n"
                        self.updatelabel(newtext)
                        newtext = "Bot: Is there any other way of responding to this question? If so, teach me please or type 'skip'\n" #requests for synonymous answers
                        self.updatelabel(newtext)
                        self.questionexists = True
                        self.text.returnPressed.connect(self.getnewanswer)
                        self.send_button.clicked.connect(self.getnewanswer)
                else:
                    newtext = "Bot: I don't understand you. How should I respond to that? Type answer to teach me or type 'skip'\n" #else respond with can you teach me
                    self.updatelabel(newtext)
                    self.questionexists = False
                    self.text.returnPressed.connect(self.getnewanswer)
                    self.send_button.clicked.connect(self.getnewanswer)
                
    def getnewanswer(self):
        self.newanswer = self.text.text()
        self.text.clear()
        if self.newanswer == "":
            newtext = "Bot: Enter a valid answer\n"
            self.updatelabel(newtext)
        else:
            newtext = "You: " + self.newanswer + "\n"
            self.updatelabel(newtext)
            if self.questionexists == False:
                if self.newanswer != "skip": #if user enters answer, then add to memory
                    self.newquestion(self.knowledge_base, self.userinput, self.newanswer)
                else:
                    self.newquestion(self.knowledge_base, self.userinput, "")
                    newtext = "Bot: Teach me more or type 'quit' to stop teaching me\n"
                    self.updatelabel(newtext)
                    self.text.returnPressed.disconnect()
                    self.send_button.clicked.disconnect()
                    self.text.returnPressed.connect(self.on_send_clicked)
                    self.send_button.clicked.connect(self.on_send_clicked)
            else:
                if self.newanswer != "skip": #if user enters answer, then add to memory
                    self.addnewanswertoknowledgebase(self.knowledge_base,self.best_match,self.newanswer)
                else:
                    newtext = "Bot: Teach me more or type 'quit' to stop teaching me\n"
                    self.updatelabel(newtext)
                    self.text.returnPressed.disconnect()
                    self.send_button.clicked.disconnect()
                    self.text.returnPressed.connect(self.on_send_clicked)
                    self.send_button.clicked.connect(self.on_send_clicked)

    def loadknowledgebase(self,filepath):
        with open(filepath, 'r') as file:
            data = json.load(file)
        return data

    def quitbot(self):
        newtext = "Bot: See you soon!\n"
        self.updatelabel(newtext)
        QTimer.singleShot(2000, QApplication.quit)

    def bestmatches(self,userinput, question):
        matches = get_close_matches(userinput, question, n = 1, cutoff = 0.6) #n = number of answers to said question, cutoff = accuracy of response
        if matches:
            return matches[0]
        else:
            return None            

    def bestresponse(self, question, knowledgebase):
        answers = []
        for q in knowledgebase["questions"]:
            if q["question"] == question:
                answers.extend(q["answers"])
        if answers:
            answer = random.choice(answers)
        else:
            answer = ""
        return answer

    def newquestion(self,knowledge_base, question,newanswer):
        if newanswer == "":
            knowledge_base["questions"].append({"question" : question, "answers" : []})
            newtext = "Bot: You have not taught me how to answer that question\n"
            self.updatelabel(newtext)
            newtext = "Bot: Teach me more or type 'quit' to stop teaching me\n"
            self.updatelabel(newtext)
        else:
            knowledge_base["questions"].append({"question" : question, "answers" : [newanswer]})
            newtext = "Bot: I learnt something new! Thank you!\n"
            self.updatelabel(newtext)
            newtext = "Bot: Teach me more or type 'quit' to stop teaching me\n"
            self.updatelabel(newtext)
        self.updateknowledgebase("knowledgebase.json", knowledge_base)
        self.text.returnPressed.disconnect()
        self.send_button.clicked.disconnect()
        self.text.returnPressed.connect(self.on_send_clicked)
        self.send_button.clicked.connect(self.on_send_clicked)

    def addnewanswertoknowledgebase(self, knowledge_base, question,newanswer):
        for q in knowledge_base["questions"]:
            if q["question"] == question:
                if newanswer not in q["answers"]:
                    q["answers"].append(newanswer)
                    self.updateknowledgebase("knowledgebase.json", knowledge_base)
                    newtext = "Bot: I learnt something new! Thank you!\n"
                    self.updatelabel(newtext)
                    newtext = "Bot: Teach me more or type 'quit' to stop teaching me\n"
                    self.updatelabel(newtext)
                    self.text.returnPressed.disconnect()
                    self.send_button.clicked.disconnect()
                    self.text.returnPressed.connect(self.on_send_clicked)
                    self.send_button.clicked.connect(self.on_send_clicked)
                else:
                    newtext = "Bot: Already entered this answer. Is there any other way to answer this question? If yes, type answer or else type 'skip'\n"
                    self.updatelabel(newtext)
                    

    def updatelabel(self, newtext):
        self.label.appendPlainText(newtext)
    
    def updateknowledgebase(self,filepath, data):
        with open(filepath, 'w') as file:
            json.dump(data, file, indent = 2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChatbotUI()
    window.show()
    sys.exit(app.exec_())