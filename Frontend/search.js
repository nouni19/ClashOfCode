function contestsearch(){
	window.location.replace("contest.html?contestid="+document.getElementById("searchinput").value);
}
function problemsearch(){
	window.location.replace("problem.html?problemid="+document.getElementById("searchinput").value);
}
function usersearch(){
	window.location.replace("user.html?handle="+document.getElementById("searchinput").value);
}