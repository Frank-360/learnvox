async function askTutor() {

    const question = document
        .getElementById("question")
        .value
        .trim();

    if (!question) return;

    const answerBox = document.getElementById("answerBox");

    answerBox.innerHTML = `

        <div class="thinking-card">

            <div class="thinking-spinner"></div>

            <h3>🧠 LearnVox is thinking...</h3>

            <p>

                Preparing the best explanation for you.

            </p>

        </div>

    `;

    try {

        const response = await fetch("/ask", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                question: question

            })

        });

        const data = await response.json();

        answerBox.innerHTML = `

<div class="chat-message student">

    <div class="chat-avatar">

        👤

    </div>

    <div class="chat-bubble student-bubble">

        ${question}

    </div>

</div>

<div class="chat-message tutor">

    <div class="chat-avatar">

        🧠

    </div>

    <div class="chat-bubble tutor-bubble">

        ${data.answer}

    </div>

</div>

<div class="follow-up-box">

    💡 Try asking:

    <br><br>

    • Explain this more simply

    <br>

    • Give another example

    <br>

    • Test my understanding

    <br>

    • Compare the concepts

</div>

`;

        document.getElementById("question").value = "";

    }

    catch(error){

        answerBox.innerHTML = `

<div class="study-card">

<h2>

❌ Error

</h2>

<p>

Unable to contact your AI Tutor.

</p>

</div>

`;

    }

}

// =========================================
// FOCUS STUDY WORKSPACE
// =========================================

function focusWorkspace(button = null) {

    const workspace = document.getElementById("studyWorkspace");

    if (button) {

        button.style.transform = "scale(.96)";

    }

    workspace.classList.add("workspace-focus");

    workspace.scrollIntoView({

        behavior: "smooth",

        block: "start"

    });

    setTimeout(() => {

        workspace.classList.remove("workspace-focus");

        if (button) {

            button.style.transform = "";

        }

    }, 1200);

}


// =========================================
// SHOW LOADING
// =========================================

function showLoading(title, message) {

    const workspace =
        document.getElementById("studyOutput");

    workspace.innerHTML = `

    <div class="loading-screen">

        <div class="loading-emoji">

            🧠

        </div>

        <h2>

            ${title}

        </h2>

        <div class="loading-bar">

            <div class="loading-progress"></div>

        </div>

        <p>

            ${message}

        </p>

    </div>

    `;

}

// =========================================
// LEARNVOX MODAL
// =========================================

function showModal(html){

    document.getElementById("learnvoxModal")
        .style.display = "flex";

    document.getElementById("learnvoxModalContent")
        .innerHTML = html;

}

function closeModal(){

    document.getElementById("learnvoxModal")
        .style.display = "none";

}


// =========================================
// DAILY LEARNING COMPLETE
// =========================================

function showDailyLearningComplete(studentName, documents){

    showModal(`

        <div class="moment-icon">

            🎉

        </div>

        <h1>

            Daily Learning Complete

        </h1>

        <p class="moment-message">

            Excellent work today,
            <strong>${studentName}</strong>!

        </p>

        <p>

            Here's what you achieved today:

        </p>

        <div class="moment-benefits">

            <div>⚡ 2 Quick Learn Sessions</div>

            <div>🧠 1 Deep Dive Session</div>

            <div>📄 ${documents} Documents in Your Study Library</div>

        </div>

       <p class="progress-message">

                🌱 You're building a great learning habit.

        </p>

        <div class="moment-divider"></div>

        <h3>

                ⭐ Keep your momentum going.

        </h3>

        <p>

            You've completed today's free learning.

            Continue learning now with Founding Membership,
            or return tomorrow for another free learning session.

        </p>

        <button
            class="primary-btn"
            onclick="window.location='/pricing'">

            👑 Become a Founding Member

        </button>

        <p class="payment-note">

            🔒 Lock in your ₦1,000/month Founding Member launch price.

        </p>

    `);

}


// =========================================
// LOADING MESSAGES
// =========================================

let loadingInterval = null;

function animateLoading(messages) {

    const text = document.querySelector(".loading-screen p");

    if (!text) return;

    let index = 0;

    text.innerHTML = messages[0];

    clearInterval(loadingInterval);

    loadingInterval = setInterval(() => {

        index = (index + 1) % messages.length;

        text.innerHTML = messages[index];

    }, 1200);

}
// =========================================
// QUICK LEARN
// =========================================

async function openQuickLearn(event) {

    const workspace = document.getElementById("studyWorkspace");

    workspace.style.display = "block";

    focusWorkspace(event.currentTarget);

    showLoading(
        "🧠 I'm reading your document...",
        "Finding the key ideas..."
    );

    animateLoading([
        "Finding the key ideas...",
        "Connecting important concepts...",
        "Preparing your personalised lesson..."
    ]);
    // ------------------------------------
// Jump to workspace
// ------------------------------------

    console.log("openQuickLearn() called");

    const studentName = document.getElementById("studentName").value;

    workspace.style.display = "block";

    const output = document.getElementById("studyOutput");


    try {

        console.log("Sending request to /quick-learn...");

        const response = await fetch("/quick-learn", {

            method: "POST"

        });

       const data = await response.json();

        clearInterval(loadingInterval);

        const loadingText =
            document.querySelector(".loading-screen p");

        if (loadingText){

            loadingText.innerHTML =
                "✨ Your lesson is ready...";

            await new Promise(resolve =>
                setTimeout(resolve, 500)
            );

        }

       if (!data.success) {

    // User has reached free limit
   if (data.upgrade) {

    const displayName = studentName
        .split(" ")
        .map(name =>
            name.charAt(0).toUpperCase() +
            name.slice(1).toLowerCase()
        )
        .join(" ");

    showModal(`

        <div class="moment-icon">

            👑

        </div>

            <h1>🚀 Unlock Unlimited Learning</h1>

        <p class="moment-message">

            🎉 Congratulations,
            <strong>${displayName}</strong>!

        </p>

        <p>

            You've made great progress today.

        </p>

        <p>

            Your free learning session is complete.

        </p>

        <p>

            <strong>Keep your momentum going.</strong>

            Become a Founding Member and continue learning without limits.

        </p>
        
        <div class="moment-benefits">

            <div>♾️ Unlimited Quick Learn</div>

            <div>♾️ Unlimited Deep Dive</div>

            <div class="featured-benefit">

                ⭐ Unlimited AI Tutor

                    <span>

                         Most Popular

                    </span>

        </div>

            <div>♾️ Unlimited Quizzes</div>

            <div>♾️ Unlimited Flashcards</div>

            <div>🎧 Unlimited Audio Lessons</div>

        </div>

        <button
            class="primary-btn"
            onclick="window.location='/pricing'">

            👑 Become a Founding Member

        </button>

    `);

    return;

}

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

            <div class="quick-complete">

                <h3>

                    🎉 Great Job!

                </h3>

                <p>

                    You've understood the fundamentals of this topic.

                    You're now ready for a complete AI tutoring session where
                    we'll explore the topic in much greater depth.

                </p>

        <button

                class="primary-btn tutor-btn"

                onclick="openDeepDive({ currentTarget: this })">

                🧠 Tutor Me

            </button>

        </div>

        </div>

        `;

        loadAccount();


    }

    catch(error){

        console.error(error);

    }

}

// ======================================
// AI TUTOR
// ======================================

  async function openDeepDive(event) {

    const workspace = document.getElementById("studyWorkspace");

    workspace.style.display = "block";

    focusWorkspace(event.currentTarget);

    showLoading(
        "📖 I'm preparing today's lesson...",
        "Organising the topic into simple explanations..."
    );

animateLoading([

    "Organising the topic into simple explanations...",

     "Preparing your audio lesson...",

    "Creating quizzes and flashcards..."

]);
    // ------------------------------------
// Jump to workspace
// ------------------------------------

    workspace.style.display = "block";

    const output = document.getElementById("studyOutput");

    try {

        const response = await fetch("/summary", {
            method: "POST"
        });

        const data = await response.json();

clearInterval(loadingInterval);

if (!data.success) {

    // 🎉 Daily learning completed
    if (data.daily_complete) {

        const studentName =
            document.getElementById("studentName").value;

        const displayName = studentName
            .split(" ")
            .map(name =>
                name.charAt(0).toUpperCase() +
                name.slice(1).toLowerCase()
            )
            .join(" ");

        showDailyLearningComplete(
            displayName,
            data.documents_uploaded
        );

        return;
    }

    // Other errors
    output.innerHTML = `
        <h2>Error</h2>
        <p>${data.message}</p>
    `;

    return;
}

const loadingText =
    document.querySelector(".loading-screen p");

if (loadingText) {

    loadingText.innerHTML =
        "✨ Your lesson is ready...";

    await new Promise(resolve =>
        setTimeout(resolve, 500));
}


    const studentName = document.getElementById("studentName").value;

    const documentName = document.getElementById("documentName").value;

        
  output.innerHTML = `

<div class="lesson-page">

    <div class="tutor-banner">

        <span class="workspace-badge">

            AI Personal Tutor

        </span>

    <h1>

    👋 Hi ${studentName},

</h1>

<p>

    Today we'll explore:

    <strong>${documentName}</strong>

</p>

<p>

    I'll guide you through each concept step by step, explain the difficult
    parts clearly, and help you build confidence before we move on to quizzes
    and flashcards.

</p>

    </div>


    <!-- =========================
            TEACH ME
    ========================== -->

    <div class="study-card">

        <div class="card-title">

            <span>📖</span>

            <h2>Teach Me</h2>

        </div>

        <div class="summary-content">

            ${data.lesson}

        </div>

    </div>



    <!-- =========================
            LISTEN
    ========================== -->

    <div class="study-card">

        <div class="card-title">

            <span>🎧</span>

            <h2>Listen</h2>

        </div>

        <p>

            Prefer listening? Your AI Tutor has prepared an audio lesson.

        </p>

        <audio
            controls
            preload="metadata"
            style="width:100%;margin-top:20px;">

            <source
                src="${data.audio_file}"
                type="audio/mpeg">

        </audio>

    </div>



    <!-- =========================
            CONTINUE
    ========================== -->

    <div class="study-card">

        <div class="card-title">

            <span>🚀</span>

            <h2>Continue Learning</h2>

        </div>

        <p>

            Great progress! Strengthen your understanding with a quiz
            or revise using flashcards.

        </p>

        <div class="lesson-actions">

            <button
                class="primary-btn"
                onclick="openQuiz()">

                ❓ Quiz Me

            </button>

            <button
                class="secondary-btn"
                onclick="openFlashcards()">

                📝 Flashcards

            </button>

        </div>

    </div>



    <!-- =========================
            SAVE
    ========================== -->

    <div class="study-card">

        <div class="card-title">

            <span>💾</span>

            <h2>Save For Later</h2>

        </div>

        <p>

            Continue learning offline whenever it suits you.

        </p>

        <div class="lesson-actions">

            <a
                class="primary-btn"
                href="${data.lesson_file}"
                target="_blank">

                📄 Save Study Notes

            </a>

            <a
                class="secondary-btn"
                href="${data.audio_file}"
                download>

                🎧 Save Audio Lesson

            </a>

        </div>

    </div>

</div>

`;

loadAccount();

    }

    catch (error) {

        console.error(error);

        output.innerHTML = `
            <h2>Something went wrong.</h2>
            <p>Please try again.</p>
        `;

    }

}


async function openAskMe(event) {

    focusWorkspace(event.currentTarget);

    showLoading(
    "💬 I'm thinking about your question...",
    "Finding the best explanation..."
);

animateLoading([

    "Finding the best explanation...",

    "Looking through your document...",

    "Preparing an easy-to-understand answer..."

]);
    // ------------------------------------
// Jump to workspace
// ------------------------------------

    const workspace = document.getElementById("studyWorkspace");

    workspace.style.display = "block";

    const output = document.getElementById("studyOutput");

    output.innerHTML = `

<div class="chat-section">

    <div class="chat-header">

        <span class="workspace-badge">

            Unlimited Tutoring

        </span>

        <h2>

            Ask Me Anything

        </h2>

        <p>

            I'm here to explain, simplify and answer every question until you understand the topic.

        </p>

    </div>

    <div class="example-prompts">

        <span>Try asking:</span>

        <div class="prompt-tags">

            <span>Explain this simply</span>

            <span>Give another example</span>

            <span>Quiz me</span>

            <span>What should I remember?</span>

        </div>

    </div>

    <div class="chat-box">

        <input
            id="question"
            type="text"
            placeholder="Ask your AI Tutor anything...">

        <button
            class="primary-btn"
            onclick="askTutor()">

            Ask Me

        </button>

    </div>

    <div
        id="answerBox"
        class="answer-box">

    </div>

</div>

`;

    document.getElementById("question").focus();

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

        clearInterval(loadingInterval);

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

    const progress =
        ((currentQuestion + 1) / quizQuestions.length) * 100;

    output.innerHTML = `

<div class="lesson-page">

    <div class="tutor-banner">

        <span class="workspace-badge">

            AI Quiz Session

        </span>

        <h1>

            🧠 Quiz Me

        </h1>

        <p>

            Let's see how well you've understood today's lesson.

            Take your time and choose the best answer.

        </p>

    </div>


    <div class="study-card">

        <div class="quiz-header">

            <span>

                Question ${currentQuestion + 1}

            </span>

            <span>

                ${quizQuestions.length} Questions

            </span>

        </div>

        <div class="progress-bar">

            <div
                class="progress-fill"
                style="width:${progress}%">

            </div>

        </div>

        <h2 class="quiz-question">

            ${q.question}

        </h2>

        <div class="quiz-options">

            ${q.options.map((option,index)=>`

                <button
                    class="quiz-option"
                    onclick="submitAnswer(${index})">

                    ${option}

                </button>

            `).join("")}

        </div>

    </div>

</div>

`;

}


function submitAnswer(selectedIndex) {

    const q = quizQuestions[currentQuestion];

    const output = document.getElementById("studyOutput");

    const correct = selectedIndex === q.answer;

    if (correct) {

        score++;

    }

    output.innerHTML = `

<div class="lesson-page">

    <div class="study-card">

        <h1>

            ${correct ? "✅ Correct!" : "❌ Not Quite"}

        </h1>

        <h2>

            ${q.question}

        </h2>

        <div class="answer-feedback ${correct ? "correct-card" : "wrong-card"}">

            <strong>

                ${
                    correct
                    ? "Excellent!"
                    : "The correct answer is:"
                }

            </strong>

            <p>

                ${q.options[q.answer]}

            </p>

        </div>

        <div class="explanation-box">

            <h3>

                💡 Why?

            </h3>

            <p>

                ${q.explanation}

            </p>

        </div>

        <div class="quiz-footer">

            <span>

                Score:

                <strong>

                    ${score}

                </strong>

                /

                ${quizQuestions.length}

            </span>

            <button

                class="primary-btn"

                onclick="nextQuestion()">

                ${
                    currentQuestion + 1 === quizQuestions.length
                    ? "🏆 Finish Quiz"
                    : "➡ Next Question"
                }

            </button>

        </div>

    </div>

</div>

`;

}

function nextQuestion() {

    currentQuestion++;

    if (currentQuestion < quizQuestions.length) {

        showQuestion();

    }

    else {

        finishQuiz();

    }

}


function finishQuiz() {

    const output = document.getElementById("studyOutput");

    const percentage = (score / quizQuestions.length) * 100;

    let feedback = "";
    let emoji = "";
    let title = "";

    if (percentage >= 90) {

        emoji = "🏆";
        title = "Outstanding!";
        feedback = "Excellent work! You've mastered this topic. Keep up the fantastic learning.";

    }

    else if (percentage >= 75) {

        emoji = "🌟";
        title = "Great Job!";
        feedback = "You're very close to mastering this topic. A quick review will make you even stronger.";

    }

    else if (percentage >= 50) {

        emoji = "📘";
        title = "Good Effort!";
        feedback = "You've understood many of the ideas. Review the lesson once more and you'll improve quickly.";

    }

    else {

        emoji = "💪";
        title = "Keep Going!";
        feedback = "Learning takes practice. Revisit the AI Tutor lesson and try the quiz again. You've got this!";

    }

    output.innerHTML = `

<div class="lesson-page">

    <div class="tutor-banner">

        <span class="workspace-badge">

            Quiz Complete

        </span>

        <h1>

            ${emoji} ${title}

        </h1>

        <p>

            You've completed today's quiz.

        </p>

    </div>

    <div class="study-card">

        <div class="quiz-score-card">

            <h2>

                Your Score

            </h2>

            <div class="score-circle">

                ${score}/${quizQuestions.length}

            </div>

            <p>

                ${feedback}

            </p>

        </div>

    </div>

    <div class="study-card">

        <h2>

            🚀 What's Next?

        </h2>

        <p>

            Continue strengthening your understanding using any of the learning tools below.

        </p>

        <div class="lesson-actions">

            <button
                class="primary-btn"
                onclick="openDeepDive()">

                📖 Review Lesson

            </button>

            <button
                class="secondary-btn"
                onclick="openFlashcards()">

                📝 Flashcards

            </button>

            <button
                class="secondary-btn"
                onclick="openQuiz()">

                🔄 Try Again

            </button>

        </div>

    </div>

</div>

`;

}


// ======================================
// FLASHCARDS
// ======================================

let flashcards = [];

let currentFlashcard = 0;

let showingAnswer = false;


async function openFlashcards() {

    const output = document.getElementById("studyOutput");

    output.innerHTML = `

        <div class="loading-box">

            <h2>📝 Building Flashcards...</h2>

            <p>

                LearnVox is creating your study cards...

            </p>

        </div>

    `;

try {

    const response = await fetch("/flashcards");

    const data = await response.json();

    if (!data.success) {

        throw new Error("Unable to generate flashcards.");

    }

    flashcards = data.flashcards;

    currentFlashcard = 0;

    showingAnswer = false;

    showFlashcard();

} catch (error) {

    console.error(error);

    output.innerHTML = `

        <div class="study-card">

            <h2>❌ Error</h2>

            <p>${error.message}</p>

        </div>

    `;

}
}

function showFlashcard(){

    const card = flashcards[currentFlashcard];

    const output = document.getElementById("studyOutput");

    output.innerHTML = `

<div class="lesson-page">

    <div class="tutor-banner">

        <span class="workspace-badge">

            Flashcards

        </span>

        <h1>

            🃏 Flashcard ${currentFlashcard+1}

        </h1>

        <p>

            Card ${currentFlashcard+1} of ${flashcards.length}

        </p>

    </div>


    <div class="study-card">

        <h2>

            ${showingAnswer ? "Answer" : "Question"}

        </h2>

        <div class="flashcard-content">

            ${showingAnswer ? card.answer : card.question}

        </div>

        <div class="lesson-actions">

            <button

                class="secondary-btn"

                onclick="flipFlashcard()">

                🔄 ${showingAnswer ? "Show Question" : "Flip Card"}

            </button>

        </div>

    </div>


    <div class="lesson-actions">

        <button

            class="secondary-btn"

            onclick="previousFlashcard()"

            ${currentFlashcard===0 ? "disabled":""}>

            ◀ Previous

        </button>

        <button

            class="primary-btn"

            onclick="nextFlashcard()">

            ${currentFlashcard===flashcards.length-1 ? "🎉 Finish" : "Next ▶"}

        </button>

    </div>

</div>

`;

}


function flipFlashcard(){

    const card = document.querySelector(".flashcard-content");

    card.classList.add("flashcard-flip");

    setTimeout(()=>{

        showingAnswer=!showingAnswer;

        showFlashcard();

    },250);

}


function nextFlashcard(){

    if(currentFlashcard < flashcards.length-1){

        currentFlashcard++;

        showingAnswer=false;

        showFlashcard();

    }

    else{

        finishFlashcards();

    }

}


function previousFlashcard(){

    if(currentFlashcard>0){

        currentFlashcard--;

        showingAnswer=false;

        showFlashcard();

    }

}


function finishFlashcards(){

    const output=document.getElementById("studyOutput");

    output.innerHTML=`

<div class="lesson-page">

    <div class="tutor-banner">

        <h1>

            🎉 Excellent!

        </h1>

        <p>

            You've completed all the flashcards.

        </p>

    </div>

    <div class="study-card">

        <h2>

            Great Revision!

        </h2>

        <p>

            You've reviewed every important concept from today's lesson.

        </p>

        <div class="lesson-actions">

            <button

                class="primary-btn"

                onclick="openQuiz()">

                ❓ Quiz Again

            </button>

            <button

                class="secondary-btn"

                onclick="openDeepDive()">

                📖 Review Lesson

            </button>

        </div>

    </div>

</div>

`;

}

// ======================================
// FOCUS CHAT
// ======================================

function focusChat() {

    document
        .getElementById("question")
        .focus();

}


// =========================================
// LOAD USER ACCOUNT
// =========================================

async function loadAccount() {

    try {

        const response = await fetch("/account");

        const data = await response.json();

        if (!data.success) return;

        const plan = document.getElementById("planName");

        const quick = document.getElementById("quickRemaining");

        const deep = document.getElementById("deepRemaining");

        const documents = document.getElementById("documentsUploaded");

        const documentsDescription =
             document.getElementById("documentsDescription");

        const description = document.getElementById("planDescription");


        const label = document.getElementById("planLabel");

        const planCard = document.getElementById("planCard");

        // -----------------------------
        // Founding Member
        // -----------------------------

        if (data.plan === "pro") {

            planCard.classList.add("founding-member");

            label.innerHTML =
                "👑 Founding Member";

            plan.innerHTML =
                "⭐ Lifetime Launch Member";

                description.innerHTML =
                    "You locked in your exclusive ₦1,000/month Founding Member launch price.";

            quick.innerHTML = "♾️ Unlimited";

            deep.innerHTML = "♾️ Unlimited";

            documents.innerHTML = data.documents_uploaded;

            documentsDescription.innerHTML =
            "Documents you've studied with LearnVox.";

            return;
        }

        // -----------------------------
        // Free Plan
        // -----------------------------


        label.innerHTML =
             "👑 Your Plan";

        plan.innerHTML = "Free Plan";

        planCard.classList.remove("founding-member");

        description.innerHTML =
            "You're currently enjoying LearnVox Free.";

        const quickRemaining = Math.max(0, 2 - data.quick_learn_used);

        const deepRemaining = Math.max(0, 1 - data.deep_dive_used);

        quick.innerHTML = quickRemaining + " Remaining";

        deep.innerHTML = deepRemaining + " Remaining";

        documents.innerHTML = data.documents_uploaded;

        documentsDescription.innerHTML =
         "Documents you've studied with LearnVox.";


    }

    catch(error){

        console.error("Unable to load account.", error);

    }

}

loadAccount();