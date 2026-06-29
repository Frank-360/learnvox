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

const answer = await response.text();

const answerBox = document.getElementById("answerBox");

answerBox.style.display = "block";

answerBox.innerHTML = answer;

// Clear the input after sending
document.getElementById("question").value = "";

}

// ======================================
// QUICK LEARN
// ======================================

async function openQuickLearn() {

    const output = document.getElementById("studyOutput");

    output.innerHTML = `
        <h2>⚡ Building Quick Learn...</h2>
        <p>
            LearnVox is finding the fastest way
            to help you understand this topic.
        </p>
    `;

    try {

        const response = await fetch("/quick-learn", {

            method: "POST"

        });

        const data = await response.json();

        if (!data.success) {

            output.innerHTML = `
                <h2>Error</h2>

                <p>${data.message}</p>
            `;

            return;

        }

        output.innerHTML = `

        <div class="lesson-page">

            <h1>

                ⚡ Quick Learn

            </h1>

            <p>

                Understand this topic in about
                3 minutes.

            </p>

            <hr>

            <div class="summary-content">

                ${data.quick}

            </div>

            <hr>

            <button
                class="chat-btn"
                onclick="openDeepDive()">

                📚 Tutor Me

            </button>

        </div>

        `;


    }

    catch(error){

        console.error(error);

    }

}


// ======================================
// AI TUTOR
// ======================================

async function openDeepDive() {

    console.log("AI Tutor clicked");


    const output = document.getElementById("studyOutput");

    console.log("Output element:", output);

output.innerHTML = `
    <h2>🧠 Your AI Tutor is Getting Ready...</h2>
    <p>
        Reading your document...
        <br>
        Finding the most important concepts...
        <br>
        Preparing a step-by-step tutoring session...
    </p>
`;

    try {

        const response = await fetch("/summary", {
            method: "POST"
        });

        const data = await response.json();

        console.log(data);

        if (!data.success) {

            output.innerHTML = `
                <h2>Error</h2>
                <p>${data.message}</p>
            `;

            return;
        }

        
    output.innerHTML = `

<div class="lesson-page">

    <h1>

    🧠 Learn With Your AI Tutor

    </h1>

    <p>
        I'll guide you through this topic, explain the tricky parts, and help you truly understand it.

    </p>

    <hr>

    <div class="summary-content">

        ${data.lesson}

    </div>

   <hr>

<div class="audio-section">

    <h3>🎧 Listen to Your AI Tutor</h3>

    <audio controls preload="metadata" style="width:100%; margin-top:15px;">

        <source
            src="${data.audio_file}"
            type="audio/mpeg">

        Your browser does not support audio playback.

    </audio>

</div>

<hr>

<div class="tutor-next">

    <h3>🚀 Continue Learning</h3>

    <p>Choose what you'd like to do next.</p>

    <div class="tutor-actions">

        <button
            class="chat-btn"
            onclick="openQuiz()">

            ❓ Quiz Me

        </button>

        <button
            class="chat-btn"
            onclick="openFlashcards()">

            📝 Flashcards

        </button>

    </div>

</div>

<hr>

<div class="save-section">

    <h3>📥 Save for Later</h3>

    <div class="tutor-actions">

        <a
            class="download-btn"
            href="${data.lesson_file}"
            target="_blank">

            📄 Download Tutor Notes

        </a>

        <a
            class="download-btn"
            href="${data.audio_file}"
            download>

            🎧 Download Audio

        </a>

    </div>

</div>

</div>

`;


    }

    catch (error) {

        console.error(error);

        output.innerHTML = `
            <h2>Something went wrong.</h2>
            <p>Please try again.</p>
        `;

    }

}

// ======================================
// QUIZ
// ======================================

let quizQuestions = [];
let currentQuestion = 0;
let score = 0;

async function openQuiz() {

    const output = document.getElementById("studyOutput");

    output.innerHTML = `
        <div class="lesson-page">

            <h2>🧠 Preparing Your Quiz...</h2>

            <p>
                Your AI Tutor is creating personalized questions...
            </p>

        </div>
    `;

    try {

        const response = await fetch("/quiz", {
            method: "POST"
        });

        const data = await response.json();

        if (!data.success) {

            output.innerHTML = `
                <div class="lesson-page">

                    <h2>Error</h2>

                    <p>${data.message}</p>

                </div>
            `;

            return;

        }

        startQuiz(data.quiz.questions);

    }

    catch (error) {

        console.error(error);

        output.innerHTML = `
            <div class="lesson-page">

                <h2>Something went wrong.</h2>

                <p>Please try again.</p>

            </div>
        `;

    }

}


function startQuiz(questions) {

    quizQuestions = questions;

    currentQuestion = 0;

    score = 0;

    showQuestion();

}


function showQuestion() {

    const q = quizQuestions[currentQuestion];

    const output = document.getElementById("studyOutput");

    output.innerHTML = `

<div class="lesson-page">

    <h1>🧠 Quiz Me</h1>


       <p class="quiz-progress">

        Question ${currentQuestion + 1} of ${quizQuestions.length}

        </p>

        <h2 class="quiz-question">

            ${q.question}

        </h2>

    <div class="quiz-options">

        ${q.options.map((option, index) => `

            <button
                class="quiz-option"
                onclick="submitAnswer(${index})">

                ${option}

            </button>

        `).join("")}

    </div>

</div>

`;

}



function submitAnswer(choice) {

    const q = quizQuestions[currentQuestion];

    const output = document.getElementById("studyOutput");

    const correct = choice === q.answer;

    if (correct) {

        score++;

    }

    const isLastQuestion = currentQuestion === quizQuestions.length - 1;

    output.innerHTML = `

<div class="lesson-page">

    <h1>

        ${correct ? "🎉 Excellent!" : "❌ Not Quite"}

    </h1>

    <p style="font-size:20px; line-height:1.8;">

        ${q.explanation}

    </p>

    ${!correct ? `

    <p style="margin-top:20px;font-weight:bold;color:#16a34a;">

        ✅ Correct Answer:
        ${q.options[q.answer]}

    </p>

    ` : ""}

    <div class="quiz-score">

        ⭐ Score

        <strong>

            ${score} / ${quizQuestions.length}

        </strong>

    </div>

    <button
        class="chat-btn"
        onclick="${isLastQuestion ? 'finishQuiz()' : 'nextQuestion()'}">

        ${isLastQuestion ? '🎉 Finish Quiz' : 'Next →'}

    </button>

</div>

`;

}

function nextQuestion() {

    currentQuestion++;

    if (currentQuestion >= quizQuestions.length) {

        finishQuiz();

        return;

    }

    showQuestion();

}


function finishQuiz() {

    const output = document.getElementById("studyOutput");

    const percentage = (score / quizQuestions.length) * 100;

    let feedback = "";

    if (percentage >= 90) {

        feedback = "🌟 Outstanding! You have an excellent understanding of this topic.";

    } else if (percentage >= 75) {

        feedback = "👏 Great job! You're very close to mastering this topic.";

    } else if (percentage >= 50) {

        feedback = "📘 Good effort! Review the AI Tutor lesson and try the quiz again to strengthen your understanding.";

    } else {

        feedback = "💪 Don't give up! Learning takes practice. Go through the AI Tutor lesson once more and then retake the quiz.";

    }

    output.innerHTML = `

<div class="lesson-page">

    <h1>

        🎉 Quiz Complete!

    </h1>

    <h2>

        You scored ${score} / ${quizQuestions.length}

    </h2>

    <p>

        ${feedback}

    </p>

    <div class="tutor-actions">

        <button
            class="chat-btn"
            onclick="openDeepDive()">

            👨‍🏫 Return to AI Tutor

        </button>

        <button
            class="chat-btn"
            onclick="openQuiz()">

            🔄 Try Again

        </button>

    </div>

</div>

`;

}


// ======================================
// FLASHCARDS
// ======================================

function openFlashcards() {

    document.getElementById("studyOutput").innerHTML =
    "<h2>📝 Flashcards</h2><p>Coming soon...</p>";

}



function openTeach() {

    document.getElementById("studyOutput").innerHTML =
    "<h2>🎓 Teach Me</h2><p>Coming soon...</p>";

}

// ======================================
// FOCUS CHAT
// ======================================

function focusChat() {

    document
        .getElementById("question")
        .focus();

}