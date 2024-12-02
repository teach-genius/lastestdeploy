from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from utilisateur import CandidateData
from model import Modele

# Modèle pour la requête
class CommandRequest(BaseModel):
    query: str  # La réponse ou question du candidat

class Evaluation(BaseModel):
    id: int
    question: str
    reponse_candidat: str
    Score: str
    Feedback: str
    KeyImprovements: List[str]

class CalculerScoresResponse(BaseModel):
    general_pourcentage: int
    quiz_pourcentage: float
    evaluation_pourcentage: float

class InfoInter(BaseModel):
    role_job: str
    interviewer: str

class Question(BaseModel):
    question: str
    reponse_candidat: str
    bonne_reponse: str

# Modèle pour valider les données entrantes
class InterviewerChoice(BaseModel):
    interviewer_number: str # Numéro de l'intervieweur

class TimeData(BaseModel):
    remaining_time: int

class TimeData2(BaseModel):
    remaining_time: str

# Modèle Pydantic pour valider les données reçues
class QuizAnswer(BaseModel):
    question: str
    reponse_candidat: str
    bonne_reponse: str

# Modèle de la requête pour recevoir les données
class JobQuery(BaseModel):
    title: str
    description: str
    name_company: str   


# Initialisation de l'application FastAPI
app = FastAPI()
# Chemin relatif pour atteindre le dossier App/static depuis le fichier main.py
static_dir = "static"
# Monter le dossier 'App/static' comme serveur de fichiers statiques
app.mount("/static", StaticFiles(directory=static_dir), name="static")
# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
chat = Modele()
Candidat = CandidateData() 

# Endpoint pour récupérer les évaluations
@app.get("/api/evaluation/endpoint/interview", response_model=List[Evaluation])
async def get_evaluations_interview():
    evaluations=Candidat.get_evaluations()
    print(evaluations)
    if not evaluations:
        raise HTTPException(status_code=404, detail="Aucune évaluation disponible.")
    return evaluations

# Variable globale pour suivre la dernière question posée
last_question = None
# Endpoint pour gérer les requêtes
@app.post("/endpoint")
async def process_command(request: CommandRequest):
    global last_question
    query = request.query
    if query == "None":
        query = None
    # # Obtenir la réponse et la prochaine question
    response, question = chat.interview(query)

    # # Si une dernière question existe, on l'associe à la réponse actuelle
    if last_question:
        Candidat.add_question_interview(last_question, query)
    
    # # Met à jour la dernière question pour la prochaine réponse
    last_question = question
    print(Candidat.interview_log)
    Candidat.saveinterview()
    return {"response": response, "next_question": question}

# Route GET pour renvoyer les résultats
@app.get("/api/calculer-scores", response_model=CalculerScoresResponse)
async def obtenir_scores():
    try:
        resultats = Candidat.calculer_scores()  # Retourne le bon format
        print(resultats)
        return resultats
    except Exception as e:
        print(f"Erreur lors de l'obtention des scores : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")
    
# Route GET pour renvoyer les résultats
@app.get("/api/InfoInter", response_model=InfoInter)
async def obtenir_InfoInter():
    try:
        resultats = chat.get_job_info()  # Retourne le bon format
        print(resultats)
        return resultats
    except Exception as e:
        print(f"Erreur lors de l'obtention des scores : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")
    
@app.get("/api/evaluation/quiz/feed/endpoint", response_model=List[Question])
async def get_evaluations_quiz():
    eval = Candidat.get_quiz_questions()
    if not eval:
        raise HTTPException(status_code=404, detail="Aucune évaluation disponible.")
    return eval

# Route pour accepter le choix de l'intervieweur
@app.post("/api/interview/choose-interviewer")
async def choose_interviewer(choice: InterviewerChoice):
    chat.add_interviewer(choice.interviewer_number)
    print(choice.interviewer_number)
    Candidat.update_interviewer(choice.interviewer_number)
    print(f"intervieweur choisi : {choice.interviewer_number}")

    return {
        "message": "Numéro d'intervieweur enregistré avec succès",
        "interviewer": choice.interviewer_number
    }

@app.post("/api/quiz/save-end-time")
async def save_end_time(data: TimeData):
    """
    Enregistrer le temps restant ou initial à la fin du quiz.
    """
    remaining_time = data.remaining_time
    Candidat.set_test_completion_time(remaining_time)
    # Ajoutez votre logique pour sauvegarder ces données
    # Exemple : enregistrez dans une base de données ou un fichier
    print(f"Temps restant reçu : {remaining_time} secondes")
    # Réponse API
    return {"message": "Temps enregistré avec succès", "remaining_time": remaining_time}


@app.post("/api/quiz/save-end-time_interview")
async def save_end_time_interview(data: TimeData2):
    """
    Enregistrer le temps de l'interview .
    """
    remaining_time = data.remaining_time
    Candidat.update_interview_time(remaining_time)
    # Ajoutez votre logique pour sauvegarder ces données
    # Exemple : enregistrez dans une base de données ou un fichier
    print(f"Temps restant reçu : {remaining_time} secondes")
    
    # Réponse API
    return {"message": "Temps enregistré avec succès", "remaining_time": remaining_time}


@app.post("/api/quiz/save-answer")
async def save_quiz_answer(answer: QuizAnswer):
    # Validation automatique grâce à Pydantic
    try:
        Candidat.add_quiz_answer(
            question=answer.question,
            reponse_candidat=answer.reponse_candidat,
            bonne_reponse=answer.bonne_reponse
        )
        return {"message": "Answer saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    

@app.post("/api/quiz/endpoint")
async def receive_job_query(query: JobQuery):
    try:
        print("request give qcm")
        chat.add_infos_job(query.title, query.description, query.name_company)
        Candidat.update_role(query.title)
        # Générer les questions
        questions = chat.generate_qcm_question()# exampleQuestions #chat.generate_qcm_question()#
        Candidat.add_job_info(query.title, query.description, query.name_company)
        if not questions:
            return {"message": "Aucune question générée", "data": []}

        # Retourner les questions
        return {"message": "Questions générées avec succès!", "data": questions}

    except Exception as e:
        # Gérer les erreurs imprévues
        raise HTTPException(status_code=500, detail=f"Erreur interne du serveur : {str(e)}")

# Route pour servir le fichier HTML
@app.get("/", response_class=HTMLResponse)
async def read_index():
    # Chemin vers le fichier index.html
    html_path = Path("static\\templates\\home.html")
    if html_path.exists():
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    return HTMLResponse(content="<h1>Fichier non trouvé</h1>", status_code=404)


# Route pour servir le fichier HTML
@app.get("/about", response_class=HTMLResponse)
async def read_index():
    # Chemin vers le fichier index.html
    html_path = Path("static\\templates\\about.html")
    if html_path.exists():
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    return HTMLResponse(content="<h1>Fichier non trouvé</h1>", status_code=404)


# Route pour servir le fichier HTML
@app.get("/how", response_class=HTMLResponse)
async def read_index():
    # Chemin vers le fichier index.html
    html_path = Path("static\\templates\\how.html")
    if html_path.exists():
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    return HTMLResponse(content="<h1>Fichier non trouvé</h1>", status_code=404)


# Route pour servir le fichier HTML
@app.get("/next", response_class=HTMLResponse)
async def read_index():
    # Chemin vers le fichier index.html
    html_path = Path("static\\templates\\next.html")
    if html_path.exists():
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    return HTMLResponse(content="<h1>Fichier non trouvé</h1>", status_code=404)

# Route pour servir le fichier HTML
@app.get("/start", response_class=HTMLResponse)
async def read_index():
    # Chemin vers le fichier index.html
    html_path = Path("static\\templates\\start.html")
    if html_path.exists():
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    return HTMLResponse(content="<h1>Fichier non trouvé</h1>", status_code=404)


# Route pour servir le fichier HTML
@app.get("/interviwers", response_class=HTMLResponse)
async def read_index():
    Candidat.calculer_et_stocker_score()
    # Chemin vers le fichier index.html
    html_path = Path("static\\templates\\interviwer.html")
    if html_path.exists():
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    return HTMLResponse(content="<h1>Fichier non trouvé</h1>", status_code=404)

# Route pour servir le fichier HTML
@app.get("/congrate", response_class=HTMLResponse)
async def read_index():
    Candidat.update_interview_evaluations(chat.evaluate())
    # Chemin vers le fichier index.html
    html_path = Path("static\\templates\\congrate_page.html")
    if html_path.exists():
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    return HTMLResponse(content="<h1>Fichier non trouvé</h1>", status_code=404)


@app.get("/interview_page", response_class=HTMLResponse)
async def read_index():
    html_path = Path("static\\templates\\interview_page.html")
    if html_path.exists():
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    return HTMLResponse(content="<h1>Fichier non trouvé</h1>", status_code=404)



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)