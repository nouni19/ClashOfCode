from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from datatypes import *
from database import *
from testcode import *
from threading import Timer
import time
SECRET_KEY="df27454d3ae20239395a94dc5deb4db3d9a05dd34704ed0222dc101fb1186a35"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str
class TestModel(BaseModel):
    inputtest: str
    outputtest: str
class ProblemModel(BaseModel):
    problemid: str
    title: str
    content: str
    rating: int
    memkb: int
    timems: int
    tests: list[TestModel]
    contestid: str
    score: int
def mapTestModel(t: TestModel):
    return (t.inputtest,t.outputtest)
class ContestModel(BaseModel):
    authors: list[str]
    testers: list[str]
    contestid: str
    problemsids: list[str]
    title: str
    time: datetime
    duration: int
    participants: list[str]
    wrongpenalty: int
    tenminpenalty: int
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verifyPassword(plain_password, hashed_password):
    return pwd_context.verify(plain_password,hashed_password)

def getPasswordHash(password):
    return pwd_context.hash(password)

def authenticateUser(username: str, password: str):
    user = getUserDB(username)
    if user == "NOTEXIST":
        return False
    if not verifyPassword(password,user.hashpwrd):
        return False
    return user

def createAccessToken(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def getCurrentUser(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = username
    except JWTError:
        raise credentials_exception
    user = getUserDB(token_data)
    if user == "NOTEXIST":
        raise credentials_exception
    return user
def getCurrentActiveUser(current_user: User = Depends(getCurrentUser)):
    return current_user
#storeSubmissionDB(Submission("sub1","print('hi')","HusseinFarhat",6,"AC","1","py",567,750))
#registerUserDB(User(1300,"HusseinFarhat",getPasswordHash("test"),0,"Owner"))
#storeProblemDB(Problem("1","Hi!","Print hi",800,1024,800,[("5","5")],[("6","5"),("5","6")],True,False,["sub1"]))
#updateUserRatingDB("HusseinFarhat",1350)

#storeContestDB(Contest(["HusseinFarhat"],[],"cont1",["prob1"],"bestcontest",True,True,3,5,["NewAccount"]))
#storeProblemDB(Problem("prob1","bestproblem","printha",1250,1024,1000,[("a","o")],[("e","i")],[],"cont1"))
@app.post("/token",response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticateUser(form_data.username,form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = createAccessToken(data={"sub":user.handle},expires_delta=access_token_expires)
    #response.set_cookie(key="access_token", value="Bearer "+access_token)
    return {"access_token": access_token, "token_type":"bearer"}
@app.post("/register")
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    if getUserDB(form_data.username) != "NOTEXIST":
        raise HTTPException(status_code=400,detail="User already exists")
    if len(form_data.username) < 3:
        raise HTTPException(status_code=400,detail="Username too short")
    if len(form_data.username) > 16:
        raise HTTPException(status_code=400,detail="Username too long")
    if len(form_data.password) < 3:
        raise HTTPException(status_code=400,detail="Password too short")
    registerUserDB(User(1400, form_data.username, getPasswordHash(form_data.password),0,"User")) # ranks can be: User / Moderator / Manager / Owner
    return {"Success":"Registered user"}
@app.post("/setrank/{handle}/{new_rank}")
async def setRank(handle: str, new_rank: str, current_user: User = Depends(getCurrentActiveUser)):
    if current_user.rank != "Owner":
        raise HTTPException(status_code=403,detail="Not owner")
    user = getUserDB(handle)
    if user == "NOTEXIST":
        raise HTTPException(status_code=404,detail="User doesn't exist")
    updateUserRankDB(handle,new_rank)
    return {"Success":"Set rank of user"}
@app.get("/submission/{submission_id}")
async def getSubmission(submission_id: str):
    subm = getSubmissionDB(submission_id)
    if subm == "NOTEXIST":
        raise HTTPException(status_code=404,detail="Submission doesn't exist")
    contest = getContestDB(getProblemDB(subm.problemid).contestid)
    if contest.isPublic() and (not contest.isRunning()):
        return subm.toDict()
    raise HTTPException(status_code=401,detail="Submission not public")
@app.get("/privatesubmission/{submission_id}")
async def getPrivateSubmission(submission_id: str, current_user: User = Depends(getCurrentActiveUser)):
    subm = getSubmissionDB(submission_id)
    if subm == "NOTEXIST":
        raise HTTPException(status_code=404,detail="Submission doesn't exist")
    contest = getContestDB(getProblemDB(subm.problemid).contestid)
    if contest.isPublic() and (not contest.isRunning()):
        return subm.toDict()
    if (current_user.handle == subm.handle) or (current_user.handle in contest.authors):
        return subm.toDict()
    raise HTTPException(status_code=403,detail="Access denied")
@app.get("/getmysubmissions/{problem_id}")
async def getMySubmissions(problem_id: str, current_user: User = Depends(getCurrentActiveUser)):
    problem = getProblemDB(problem_id)
    if problem == "NOTEXIST":
        raise HTTPException(status_code=404,detail="Problem doesn't exist")
    returned = []
    for s in problem.submissionsids:
        if getSubmissionDB(s).handle == current_user.handle:
            returned.append(s)
    return {"Submissions":returned}
@app.post("/submit/{problem_id}/{lang}")
async def submit(problem_id: str, lang: str, content: str, current_user: User = Depends(getCurrentActiveUser)):
    problem = getProblemDB(problem_id)
    if problem == "NOTEXIST":
        raise HTTPException(status_code=404,detail="Problem doesn't exist")
    contest = getContestDB(problem.contestid)
    if not contest.isPublic():
        raise HTTPException(status_code=403,detail="Problem not public")
    if contest.isRunning() and (not (current_user.handle in contest.participants)):
        raise HTTPException(status_code=403,detail="Not a participant")
    if lang not in ["py","c++"]:
        raise HTTPException(status_code=400,detail="Not supported language")
    updateUserSubmissionnumDB(current_user.handle, current_user.submissionnum+1)
    submid = current_user.handle+("_"*(16-len(current_user.handle)))+str(current_user.submissionnum)
    subm = Submission(submid,content,current_user.handle,int((datetime.utcnow()-contest.time).total_seconds()),"QU",problem_id,lang,0,0,contest.isRunning())   
    return {"Verdict":await testsubmission(subm,submid,problem,contest)}
@app.get("/problem/{problem_id}")
async def getProblem(problem_id: str):
    problem = getProblemDB(problem_id)
    if problem == "NOTEXIST":
        raise HTTPException(status_code=404,detail="Problem doesn't exist")
    if getContestDB(problem.contestid).isPublic():
        return problem.toDictSafe()
    raise HTTPException(status_code=403,detail="Problem not public")

@app.get("/privateproblem/{problem_id}")
async def getPrivateProblem(problem_id: str, current_user: User = Depends(getCurrentActiveUser)):
    problem = getProblemDB(problem_id)
    if problem == "NOTEXIST":
        raise HTTPException(status_code=404, detail="Problem doesn't exist")
    contest = getContestDB(problem.contestid)
    if not ((current_user.handle in contest.authors) or (current_user.handle in contest.testers) or (current_user.rank == "Owner")):
        raise HTTPException(status_code=403,detail="Access denied")
    return problem.toDict()
@app.get("/user/me")
async def getUserMe(current_user: User = Depends(getCurrentActiveUser)):
    d = current_user.toDict()
    del d["hashpwrd"]   # delete the hashed password for security
    return d
@app.get("/user/{user_handle}")
async def getUser(user_handle: str):
    user = getUserDB(user_handle)
    if user == "NOTEXIST":
        raise HTTPException(status_code=404,detail="User doesn't exist")
    return user.toDictSafe()
@app.get("/contest/{contest_id}")
async def getContest(contest_id: str):
    contest = getContestDB(contest_id)
    if contest == "NOTEXIST":
        raise HTTPException(status_code=404,detail="Contest doesn't exist")
    if not contest.isPublic():
        return contest.toDictSafe()
    return contest.toDict()
@app.get("/privatecontest/{contest_id}")
async def getPrivateContest(contest_id: str, current_user: User = Depends(getCurrentActiveUser)):
    contest = getContestDB(contest_id)
    if contest == "NOTEXIST":
        raise HTTPException(status_code=404,detail="Contest doesn't exist")
    if (not contest.isPublic()) and (not ((current_user.handle in contest.authors) or (current_user.handle in contest.testers))):
        return contest.toDictSafe()
    return contest.toDict()
@app.post("/registertocontest/{contest_id}")
async def registerToContest(contest_id: str, current_user: User = Depends(getCurrentActiveUser)):
    contest = getContestDB(contest_id)
    if contest == "NOTEXIST":
        raise HTTPException(status_code=404,detail="Contest doesn't exist")
    if current_user.handle in contest.participants:
        return {"Success":"Already registered to contest"}
    if contest.isPublic():
        raise HTTPException(status_code=403,detail="Contest registration ended")
    updateContestDB(contest_id,newparticipants=[current_user.handle])
    return {"Success":"Registered to contest"}
@app.post("/createproblem")
async def createProblem(problem: ProblemModel, current_user: User = Depends(getCurrentActiveUser)):
    if (current_user.rank != "Owner") and (current_user.rank != "Manager"):
        raise HTTPException(status_code=403,detail="Not owner or manager")
    storeProblemDB(Problem(problem.problemid,problem.title,problem.content,problem.rating,problem.memkb,problem.timems,map(mapTestModel,problem.tests),[],problem.contestid,problem.score,[],[],[],[]))
    return {"Success":"Created problem"}
@app.post("/createcontest")
async def createContest(contest: ContestModel, current_user: User = Depends(getCurrentActiveUser)):
    if (current_user.rank != "Owner") and (current_user.rank != "Manager"):
        raise HTTPException(status_code=403,detail="Not owner or manager")
    storeContestDB(Contest(contest.authors,contest.testers,contest.contestid,contest.problemsids,contest.title,contest.time,contest.duration,contest.participants,contest.wrongpenalty,contest.tenminpenalty,[]))
    timer = Timer((contest.time.replace(tzinfo=None)+timedelta(minutes=contest.duration)-datetime.utcnow()).total_seconds(),onContestEnd,[contest.contestid])
    timer.start()
    return {"Success":"Created contest"}
@app.get("/nextcontest")
async def nextContest():
    return {"contestid":"aaa"}
