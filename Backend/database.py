from datatypes import *
from sqlalchemy import create_engine, Column, Integer, String, Boolean, select, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
engine = create_engine("sqlite:///coc.db",echo=True,connect_args={"check_same_thread": False})
Base = declarative_base()
session = Session(engine)
class UserTable(Base):
    __tablename__ = 'user'
    rating = Column(Integer)
    handle = Column(String,primary_key=True)
    hashpwrd = Column(String)
    submissionnum = Column(Integer)
    rank = Column(String)
class SubmissionTable(Base):
    __tablename__ = 'submission'
    submissionid = Column(String, primary_key=True)
    content = Column(String)
    handle = Column(String)
    timestamp = Column(Integer)
    verdict = Column(String)
    problemid = Column(String)
    lang = Column(String)
    memkb = Column(Integer)
    timems = Column(Integer)
    incontest = Column(Boolean)
class TestTable(Base):
    __tablename__ = 'pretest'
    id = Column(Integer, primary_key=True)
    testin = Column(String)
    testout = Column(String)
class ProblemTable(Base):
    __tablename__ = 'problem'
    problemid = Column(String, primary_key=True)
    title = Column(String)
    content = Column(String)
    rating = Column(Integer)
    memkb = Column(Integer)
    timems = Column(Integer)
    testsids = Column(String)
    submissionsids = Column(String)
    contestid = Column(String)
    score = Column(Integer)
    correctparticipants = Column(String)
    correctparticipantss = Column(String)
    tries = Column(String)
    triesam = Column(String)
class ContestTable(Base):
    __tablename__ = 'contest'
    authors = Column(String)
    testers = Column(String)
    contestid = Column(String,primary_key=True)
    problemsids = Column(String)
    title = Column(String)
    time = Column(DateTime)
    duration = Column(Integer)
    participants = Column(String)
    wrongpenalty = Column(Integer)
    tenminpenalty = Column(Integer)
    ratedparticipants = Column(String)
def registerUserDB(user: User):
    newuser = UserTable(rating=user.rating, handle=user.handle, hashpwrd=user.hashpwrd, submissionnum=user.submissionnum, rank=user.rank)
    session.add_all([newuser])
    session.commit()
def getUserDB(handle: str):
    selected = select(UserTable).where(UserTable.handle.in_([handle]))
    temp = [x for x in session.scalars(selected)]
    if len(temp) == 0:
        return "NOTEXIST"
    udb = temp[0]
    return User(udb.rating,udb.handle, udb.hashpwrd, udb.submissionnum,udb.rank)
def updateUserRatingDB(handle: str, newrating: int):
    selected = select(UserTable).where(UserTable.handle.in_([handle]))
    [x for x in session.scalars(selected)][0].rating = newrating
    session.commit()
def updateUserRankDB(handle: str, newrank: str):
    selected = select(UserTable).where(UserTable.handle.in_([handle]))
    [x for x in session.scalars(selected)][0].rank = newrank
    session.commit()
def updateUserSubmissionnumDB(handle: str, newsubmissionnum: int):
    selected = select(UserTable).where(UserTable.handle.in_([handle]))
    [x for x in session.scalars(selected)][0].submissionnum = newsubmissionnum
    session.commit()    
def storeSubmissionDB(submission: Submission):
    newsubmission = SubmissionTable(submissionid=submission.submissionid,content=submission.content,handle=submission.handle,timestamp=submission.timestamp,verdict=submission.verdict,problemid=submission.problemid,lang=submission.lang,memkb=submission.memkb,timems=submission.timems,incontest=submission.incontest)
    session.add_all([newsubmission])
    session.commit()
def getSubmissionDB(submissionid: str):
    selected = select(SubmissionTable).where(SubmissionTable.submissionid.in_([submissionid]))
    temp = [x for x in session.scalars(selected)]
    if len(temp) == 0:
        return "NOTEXIST"
    sdb = temp[0]
    return Submission(sdb.submissionid,sdb.content,sdb.handle,sdb.timestamp,sdb.verdict,sdb.problemid,sdb.lang,sdb.memkb,sdb.timems,sdb.incontest)
def storeProblemDB(problem: Problem):
    tid = session.query(TestTable).count()
    tids = []
    ts = []
    for inp,out in problem.tests:
        ts.append(TestTable(id=tid, testin=inp, testout=out))
        tids.append(str(tid))
        tid += 1
    session.add_all(ts)
    session.add_all([ProblemTable(problemid=problem.problemid,title=problem.title,content=problem.content,rating=problem.rating,memkb=problem.memkb,timems=problem.timems,testsids=" ".join(tids),submissionsids=" ".join(map(str,problem.submissionsids)),contestid=problem.contestid,score=problem.score,correctparticipants=" ".join(problem.correctparticipants),correctparticipantss=" ".join(map(str,problem.correctparticipantss)),tries=" ".join(problem.tries),triesam=" ".join(map(str,problem.triesam)))])
    session.commit()
def getProblemDB(problemid: str):
    selected = select(ProblemTable).where(ProblemTable.problemid.in_([problemid]))
    temp = [x for x in session.scalars(selected)]
    if len(temp) == 0:
        return "NOTEXIST"
    pdb = temp[0]
    tests = []
    for i in pdb.testsids.split():
        selected = select(TestTable).where(TestTable.id.in_([int(i)]))
        tdb = [x for x in session.scalars(selected)][0]
        tests.append((tdb.testin,tdb.testout))
    problem = Problem(pdb.problemid, pdb.title,pdb.content,pdb.rating,pdb.memkb,pdb.timems,tests,pdb.submissionsids.split(),pdb.contestid,pdb.score,pdb.correctparticipants.split(),list(map(int,pdb.correctparticipantss.split())),pdb.tries.split(),list(map(int,pdb.triesam.split())))
    return problem
def updateProblemDB(problemid: str, newsubmissions: list, newcorrectparticipants: list, newcorrectparticipantss: list, newtries: list[str], newtriesam: list[int]):
    selected = select(ProblemTable).where(ProblemTable.problemid.in_([problemid]))
    temp = [x for x in session.scalars(selected)]
    if len(temp) == 0:
        return "NOTEXIST"
    pdb = temp[0]
    pdb.submissionsids = " ".join(pdb.submissionsids.split() + newsubmissions)
    pdb.correctparticipants = " ".join(pdb.correctparticipants.split() + newcorrectparticipants)
    pdb.correctparticipantss = " ".join(pdb.correctparticipantss.split() + list(map(str,newcorrectparticipantss)))
    pdb.tries = " ".join(pdb.tries.split()+newtries)
    pdb.triesam = " ".join(pdb.triesam.split()+list(map(str,newtriesam)))
    session.commit()
def incTriesDB(problemid: str, handle: str):
    selected = select(ProblemTable).where(ProblemTable.problemid.in_([problemid]))
    temp = [x for x in session.scalars(selected)]
    if len(temp) == 0:
        return "NOTEXIST"
    pdb = temp[0]
    updated = pdb.triesam.split()
    ind = pdb.tries.split().index(handle)
    updated[ind] = str(int(updated[ind])+1) 
    pdb.triesam = " ".join(updated)
    session.commit() 
def storeContestDB(contest: Contest):
    authors = " ".join(contest.authors)
    testers = " ".join(contest.testers)
    problemsids = " ".join(contest.problemsids)
    participants = " ".join(contest.participants)
    ratedparticipants = " ".join(contest.ratedparticipants)
    session.add_all([ContestTable(authors=authors,testers=testers,contestid=contest.contestid,problemsids=problemsids,title=contest.title,time=contest.time,duration=contest.duration,participants=participants,wrongpenalty=contest.wrongpenalty,tenminpenalty=contest.tenminpenalty,ratedparticipants=ratedparticipants)])
    session.commit()
def getContestDB(contestid: str):
    selected = select(ContestTable).where(ContestTable.contestid.in_([contestid]))
    temp = [x for x in session.scalars(selected)]
    if len(temp) == 0:
        return "NOTEXIST"
    cdb = temp[0]
    contest = Contest(cdb.authors.split(),cdb.testers.split(),cdb.contestid,cdb.problemsids.split(),cdb.title,cdb.time,cdb.duration,cdb.participants.split(),cdb.wrongpenalty,cdb.tenminpenalty,cdb.ratedparticipants.split())
    return contest
def updateContestDB(contestid: str, newparticipants: list = [], newauthors: list = [], newtesters: list = [], newtime: DateTime = None, newduration: int = None, newratedparticipants: list = []):
    selected = select(ContestTable).where(ContestTable.contestid.in_([contestid]))
    temp = [x for x in session.scalars(selected)]
    if len(temp) == 0:
        return "NOTEXIST"
    cdb = temp[0]
    if len(newparticipants):
        cdb.participants = " ".join(cdb.participants.split() + newparticipants)
    if len(newauthors):
        cdb.authors = " ".join(cdb.authors.split() + newauthors)
    if len(newtesters):
        cdb.testers = " ".join(cdb.testers.split() + newtesters)
    if len(newratedparticipants):
        cdb.ratedparticipants = " ".join(cdb.ratedparticipants.split() + newratedparticipants)
    if newtime != None:
        cdb.time = newtime
    if newduration != None:
        cdb.duration = newduration
    session.commit()
Base.metadata.create_all(engine)
