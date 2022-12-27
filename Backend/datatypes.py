from datetime import datetime, timedelta
class Submission:
    def __init__(self, submissionid: str, content: str, handle: str, timestamp: int, verdict: str, problemid: str, lang: str, memkb: int, timems: int,incontest: bool): ## /submissions/{id}
        self.submissionid = submissionid
        self.content = content
        self.handle = handle
        self.timestamp = timestamp
        self.verdict = verdict
        self.problemid = problemid
        self.lang = lang
        self.memkb = memkb
        self.timems = timems
        self.incontest = incontest
    def toDict(self):
        return {"submissionid":self.submissionid, "content":self.content,"handle":self.handle,"timestamp":self.timestamp,"verdict":self.verdict,"problemid":self.problemid,"lang":self.lang,"memkb":self.memkb,"timems":self.timems,"incontest":self.incontest}
class Problem:
    def __init__(self, problemid: str, title: str, content: str, rating: int, memkb: int, timems: int, tests: list[tuple[str]], submissionsids: list, contestid: str, score: int, correctparticipants: list[str], correctparticipantss: list[int], tries: list[str], triesam: list[int]): ## /problems/problemid
        self.problemid = problemid
        self.title = title
        self.content = content
        self.rating = rating
        self.memkb = memkb
        self.timems = timems
        self.tests = tests  ## this is a list of tuples : input and output
        self.submissionsids = submissionsids
        self.contestid = contestid
        self.score = score
        self.correctparticipants = correctparticipants
        self.correctparticipantss = correctparticipantss
        self.tries = tries
        self.triesam = triesam
    def toDict(self):
        return {"problemid":self.problemid,"title":self.title,"content":self.content,"rating":self.rating,"memkb":self.memkb,"dimems":self.timems,"tests":self.tests,"submissionsids":self.submissionsids,"contestid":self.contestid,"score":self.score,"correctparticipants":self.correctparticipants,"correctparticipantss":self.correctparticipantss,"tries":self.tries,"triesam":self.triesam}
    def toDictSafe(self):
        return {"problemid":self.problemid,"title":self.title,"content":self.content,"rating":self.rating,"memkb":self.memkb,"timems":self.timems,"submissionsids":self.submissionsids,"contestid":self.contestid,"score":self.score,"correctparticipants":self.correctparticipants,"correctparticipantss":self.correctparticipantss,"tries":self.tries,"triesam":self.triesam}       
class Contest:
    def __init__(self, authors: list[str], testers: list[str], contestid: str, problemsids: list[str], title: str, time: datetime, duration: int, participants: list[str], wrongpenalty: int, tenminpenalty: int, ratedparticipants: list[str]):
        self.authors = authors
        self.testers = testers
        self.contestid = contestid
        self.problemsids = problemsids
        self.title = title
        self.time = time
        self.duration = duration
        self.participants = participants
        self.wrongpenalty = wrongpenalty
        self.tenminpenalty = tenminpenalty
        self.ratedparticipants = ratedparticipants
    def toDict(self):
        return {"authors":self.authors,"testers":self.testers,"contestid":self.contestid,"problemsids":self.problemsids,"title":self.title,"time":self.time,"duration":self.duration,"participants":self.participants,"wrongpenalty":self.wrongpenalty,"tenminpenalty":self.tenminpenalty,"ratedparticipants":self.ratedparticipants}
    def toDictSafe(self):
        return {"authors":self.authors,"testers":self.testers,"contestid":self.contestid,"title":self.title,"time":self.time,"duration":self.duration,"participants":self.participants,"wrongpenalty":self.wrongpenalty,"tenminpenalty":self.tenminpenalty,"ratedparticipants":self.ratedparticipants}
    def isPublic(self):
        if self.time <=  datetime.utcnow():
            return True
        return False
    def isRunning(self):
        if (self.time + timedelta(minutes=self.duration)) > datetime.utcnow():
            if self.isPublic():
                return True
            return False
        return False
class User:
    def __init__(self, rating: int, handle: str, hashpwrd: str, submissionnum: int, rank: str):
        self.rating = rating
        self.handle = handle
        self.hashpwrd = hashpwrd
        self.submissionnum = submissionnum
        self.rank = rank
    def toDict(self):
        return {"rating":self.rating,"handle":self.handle,"hashpwrd":self.hashpwrd,"submissionnum":self.submissionnum,"rank":self.rank}
    def toDictSafe(self):
        return {"rating":self.rating,"handle":self.handle,"submissionnum":self.submissionnum,"rank":self.rank}
