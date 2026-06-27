async function askTutor(){

    const question=document.getElementById("question").value;

    if(question.trim()===""){
        return;
    }

    const response=await fetch("/ask",{

        method:"POST",

        headers:{
            "Content-Type":"application/x-www-form-urlencoded"
        },

        body:"question="+encodeURIComponent(question)

    });

    const answer=await response.text();

    const answerBox=document.getElementById("answerBox");

    answerBox.style.display="block";

    answerBox.innerHTML=answer;

}