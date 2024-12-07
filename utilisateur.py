import json
path = "infos_user.json"
data = {
            "candidat": {"role": "", "interviewer": ""},
            "job": {"titre": "", "description": "", "campagne": ""},
            "test_quiz": {
                "questions": [],
                "temps_fin_test": "",
                "evaluations": [] 
            },
            "interview": {
                "questions": [],
                
                "temps_fin_interview": "",
                
                "evaluations": []
            },
    
        }

class CandidateData:
    def __init__(self):
        self.interview_log = []
        update_data(path,data)
        
    def add_question_interview(self, question, response):
        add_question_interview(path,load_data(path),question,response)

    def saveinterview(self):
        """Sauvegarder les questions de l'interview loggées."""
        for item in self.interview_log:
            self.add_question_interview(item["question"], item["response"])
        self.interview_log.clear()

    def add_job_info(self,titre,description,compagnie):
        update_job_info(path,load_data(path),titre,description,compagnie)

    def add_quiz_answer(self, question,reponse,good_response):
        add_quiz_questions(path,load_data(path),question,reponse,good_response)

    def set_test_completion_time(self, temps_fin):
        update_end_time_quiz(path,load_data(path),temps_fin)

    def set_interview_completion_time(self, temps_fin):
        update_time_interview(path,load_data(path),temps_fin)

    def add_evaluation(self,score, feedback, improvements):
        add_evaluation(path,load_data(path),score, feedback, improvements)

    def calculer_et_stocker_score(self):
        calculer_et_stocker_score_quiz(path,load_data(path))

    def update_interview_time(self, update_time):
       update_time_interview(path,load_data(path),update_time)
 
    def update_role_and_interviewer(self,role,interviewer):
        update_candidat(path,load_data(path),role,interviewer)

    def get_quiz_percentage(self):
        return get_evaluation_quiz(load_data(path))["pourcentage"]
    
    def get_quiz_questions(self):
        return get_questions(load_data(path))

    def get_evaluations(self):
        get_evaluations(load_data(path))
            
    def calculer_scores(self):
        get_final_scores(load_data(path))
    
@staticmethod
def get_final_scores(data):
    entretiens = get_evaluations(data)
    score_quiz = get_evaluation_quiz(data)['pourcentage']
    score = [int(evaluation["score"].split("/")[0]) for evaluation in entretiens].sum()
    moyenne_entretien = (score/(len(entretiens)*10))*100
    moyenne_generale = (score_quiz+moyenne_entretien)/2
    # Création du dictionnaire de résultat
    resultats = {
    "general_pourcentage": int(moyenne_generale),
    "quiz_pourcentage": score_quiz,
    "evaluation_pourcentage": moyenne_entretien
    }
    return resultats

@staticmethod
def calculer_et_stocker_score_quiz(path,data):
    questions = data["test_quiz"]["questions"]
    bonnes_reponses = sum(1 for q in questions if q["reponse_candidat"] == q["bonne_reponse"])
    total_questions = len(questions)
    pourcentage = (bonnes_reponses / total_questions) * 100 if total_questions else 0
    data["test_quiz"]["evaluations"] = {
        "score": bonnes_reponses,
        "pourcentage": round(pourcentage, 2)
    }
    update_data(path,data)
    
@staticmethod
def get_evaluations(data):
    return data["interview"]["evaluations"] 

@staticmethod
def get_questions(data):
    return data["interview"]["questions"]

@staticmethod
def get_liste_evaluations(data):
    return get_evaluations(data)

@staticmethod
def get_order_evaluations(data):
    questions = get_questions(data)
    evaluations = get_liste_evaluations(data)
    order_evaluations = [{
        "id":index+1,
        "question":Q["question"],
        "reponse":Q["reponse_candidat"],
        "score":E["Score"],
        "Feedback":E["Feedback"],
        "KeyImprovements":[key for key in E["Key Improvements"] if key!=""]
        
    } for index,(Q,E) in enumerate(zip(questions,evaluations))]
    return order_evaluations

@staticmethod
def get_quiz_questions(data):
    return data["test_quiz"]["questions"]

@staticmethod
def get_candidat_info(data):
    return data["candidat"]

@staticmethod
def get_job_info(data):
    return data["job"]

@staticmethod
def get_evaluation_quiz(data):
    return data["test_quiz"]["evaluations"]

@staticmethod
def get_time_interview(data):
    return  data["interview"]["temps_fin_interview"]

@staticmethod
def add_question_interview(path,data,question,reponse):
    info = {
        "question":question,
        "reponse_candidat":reponse
    }
    data["interview"]["questions"].append(info)
    update_data(path,data)
    
@staticmethod
def add_quiz_questions(path,data,question,reponse,good_response):
    info={
        "question":question,
        "reponse_candidat":reponse ,
        "bonne_reponse":good_response
    }
    data["test_quiz"]["questions"].append(info)
    update_data(path,data)
    
@staticmethod
def add_evaluation(path,data,score,feed,keys):
    info = {
        "Score":score,
        "Feedback":feed,
        "Key Improvements":keys
    }
    data["interview"]["evaluations"].append(info)
    update_data(path,data)
    
@staticmethod
def update_job_info(path,data,titre,description,compagnie):
    data["job"]["titre"] = titre,
    data["job"]["description"] = description,
    data["job"]["campagne"] = compagnie
    update_data(path,data)
    
@staticmethod
def update_candidat(path,data,role,interviewer):
    data["candidat"]["role"]=role,
    data["candidat"]["interviewer"]=interviewer
    update_data(path,data)
    
@staticmethod
def update_end_time_quiz(path,data,time):
    data["test_quiz"]["temps_fin_test"]=time
    update_data(path,data)
    
@staticmethod
def update_evaluation_quiz(path,data,score,pourcentage):
    info = {
        "score": score,
        "pourcentage": pourcentage
    }
    data["test_quiz"]["evaluations"]=info
    update_data(path,data)
    
@staticmethod
def update_time_interview(path,data,time):
    data["interview"]["temps_fin_interview"]=time
    update_data(path,data)
    
@staticmethod  
def update_data(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f)
        
@staticmethod
def load_data(path):
    with open(path,"r",encoding="utf-8") as f:
        data = json.load(f)
    return data