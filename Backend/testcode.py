import subprocess
from datetime import datetime
from database import *
from datatypes import *
# this function calculates rating change and does it (gets run in the end of contest)
# uses ELO
def onContestEnd(contestid: str):
	contest = getContestDB(contestid)
	scores = {}
	print(contest.ratedparticipants)
	for handle in contest.ratedparticipants:
		scores[handle] = 0
	for problemid in contest.problemsids:
		problem = getProblemDB(problemid)
		for ind, handle in enumerate(problem.correctparticipants):
			if not (handle in scores):
				scores[handle] = 0
			scores[handle] += problem.correctparticipantss[ind]
	transformed_ratings = {}
	for handle in list(scores.keys()):
		transformed_ratings[handle] = (10**(getUserDB(handle).rating/400))
	expected_scores = {}
	real_scores = {}
	for handle in list(scores.keys()):
		expected_scores[handle] = 0
		real_scores[handle] = 0
		for handle2 in list(scores.keys()):
			if handle2 not in list(real_scores.keys()):
				real_scores[handle2] = 0
			if handle != handle2:
				expected_scores[handle] += 1/(1+(10**((transformed_ratings[handle2]-transformed_ratings[handle])/400)))
				if scores[handle] == scores[handle2]:
					real_scores[handle] += 0.5
					real_scores[handle2] += 0.5
				elif scores[handle] > scores[handle2]:
					real_scores[handle] += 1
				else:
					real_scores[handle2] += 1
	for handle in list(scores.keys()):
		updateUserRatingDB(handle,int(getUserDB(handle).rating + (32*(real_scores[handle]-expected_scores[handle])))) 
# this function tests a whole submission and updates everything, like the score
async def testsubmission(submission: Submission, submissionid: str, problem: Problem, contest: Contest):
	verdict  = await testcode(submission.content,submission.lang,problem.tests,problem.timems,problem.memkb)
	submission.verdict = verdict[0]
	submission.memkb = 5
	submission.timems = 6
	storeSubmissionDB(submission)
	correctparticipants = []
	correctparticipantss = []
	tries = []
	triesam = []
	if (not (submission.handle in problem.correctparticipants)) and (submission.incontest):
		if verdict == 'AC':
			correctparticipants = [submission.handle]
			triesdebuff = 0
			if submission.handle in problem.tries:
				triesdebuff = (problem.triesam[problem.tries.index(submission.handle)])*contest.wrongpenalty # lower score if has tried before
			timedebuff = (submission.timestamp // 600) * contest.tenminpenalty # lower score by how many tens of minutes passed
			correctparticipantss = [problem.score-triesdebuff-timedebuff]
			if not (submission.handle in contest.ratedparticipants):
				updateContestDB(contest.contestid,newratedparticipants=[submission.handle])
				print("EEEEEEEEEEEEEEEEE")
		else:
			if submission.handle in problem.tries:
				incTriesDB(problem.problemid,submission.handle)
			else:
				tries = [submission.handle]
				triesam = [1]
			if not (submission.handle in contest.ratedparticipants):
				updateContestDB(contest.contestid,newratedparticipants=[submission.handle])
				print("AAAAAAAAAAAAAAAA")
			print(contest.ratedparticipants)
	updateProblemDB(problem.problemid,[submission.submissionid],correctparticipants,correctparticipantss,tries,triesam)
	return verdict
# this function tests code and gives verdict, nothing else
async def testcode(code: str, lang: str, tests: list[tuple[str]], timems: int, memkb: int):
	with open(f"test.{lang}",'w') as f:
		f.write(code)
	if lang == 'py':
		args = ["python3.9","test.py"]
	for ind,test in enumerate(tests):
		process = subprocess.run(args,input=test[0],capture_output=True,text=True)
		if process.returncode:
			return ("RE",ind+1)
		print(process.stdout)
		print(test[0])
		print(test[1])
		if process.stdout.replace("\n","") != test[1].replace("\n",""):
			return ("WA",ind+1)
	return ("AC",0)

