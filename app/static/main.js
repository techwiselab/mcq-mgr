const API_URL = 'http://127.0.0.1:5001';

global_questionSets = []
global_attempts = []
merged = []
quizData = {}

// Function to calculate percentage
function calculatePercentage(correct, attempted) {
    return ((correct / attempted) * 100).toFixed(2);
}

// Function to create table rows
function createTableRows(merged) {
    const tbody = document.getElementById('quiz-table-body');
    merged.forEach(item => {
        const row = document.createElement('tr');

        // row.innerHTML = `
        //     <td>${item.questionsetId}</td>
        row.innerHTML = `
            <td> 
                <p  data-bs-toggle="tooltip" data-bs-placement="bottom" title="${item.description}" onclick="reattemptAll('${item.questionsetId}')" >${item.name}</p> 
            </td>         
            <td>${item.timestamp ? formatDateTime(item.timestamp) : ' - '}</td>            
            <td>${item.result ? item.result.attempted : ' - '}</td>
            <td>${item.result ? item.result.correct : ' - '}</td>
            <td>${item.result ? item.result.incorrect : ' - '}</td>
            <td>${item.result ? calculatePercentage(item.result.correct, item.result.attempted) : ' - '}</td>            
            `;
            // <td><button onclick="reattemptAll('${item.questionsetId}')"> ${item.timestamp ? 'Rea' : 'A'}ttempt All</button></td>
            //     <td>${item.timestamp ? '<button onclick="reattemptIncorrect(\'${item.questionsetId}\')">Reattempt Incorrect</button>' : ' - '}</td>          
        // `;

        tbody.appendChild(row);
    });
}

// Call the function to create table rows initially
createTableRows(merged);

// Placeholder functions for reattempt buttons
function reattemptAll(questionsetId) {
    console.log(`Reattempt all for ${questionsetId}`);
    // Hide the table
    document.getElementById('dashboard').style.display = 'none';
    // Show the quiz container
    document.getElementById('quiz-container').style.display = 'block';
    // Load the quiz data (assuming you have a function to load the quiz)
    loadQuiz(questionsetId);
}

function reattemptIncorrect(questionsetId) {
    console.log(`Reattempt incorrect for ${questionsetId}`);
}

let currentSlide = 0;
// Navigation controls
const backBtn = document.getElementById('back');
const nextBtn = document.getElementById('next');
const skipBtn = document.getElementById('skip');
const submitBtn = document.getElementById('submit');
userAnswers = new Array(1);  // to store selected indices (undefined for none)


// Function to load the quiz data
async function loadQuiz(questionsetId) {

    // Find the question set by questionsetId
    const questionSet = global_questionSets.find(qs => qs.questionsetId === questionsetId);
    if (!questionSet) {
        console.error(`Question set with ID ${questionsetId} not found.`);
        return;
    }

    // Fetch the questions for the question set
    try {
        const response = await fetch(`../questions/${questionsetId}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        questionSet.questions = data;
    } catch (error) {
        console.error('Error fetching questions:', error);
        return;
    }

    // console.log(questionSet);

    // Use the found question set to populate the quiz data
    //const 
    quizData = {
        name: questionSet.name,
        description: questionSet.description,
        questions: questionSet.questions,
        questionsetId : questionSet.questionsetId
    };

    userAnswers = new Array(quizData.questions.length);

    console.log(quizData)

    // Populate the quiz container with the quiz data
    const questionContainer = document.getElementById('question-container');
    questionContainer.innerHTML = ''; // Clear any existing content

    // Build quiz question slides
    quizData.questions.forEach((q, index) => {
        // Create slide container
        const slide = document.createElement('div');
        slide.className = 'slide';

        // Question text
        const questionElem = document.createElement('p');
        questionElem.textContent = q.text;
        slide.appendChild(questionElem);

        slide.appendChild(document.createElement('br'));

        // Answers container
        const optionsElem = document.createElement('div');
        optionsElem.className = 'options';

        // Create a radio button for each option
        q.choices.forEach((answerObj, optIndex) => {
            const optionId = `q${index}_opt${optIndex}`;
            const label = document.createElement('label');
            label.class = "form-check-label"
            label.htmlFor = optionId;
            // Radio input
            const input = document.createElement('input');
            input.type = 'radio';
            input.class = "form-check-input";
            input.name = `question${index}`;
            input.id = optionId;
            input.value = optIndex;  // store answer index as value
            // Add event listener to handle selection (enable Next when chosen)
            input.addEventListener('change', () => {
                userAnswers[index] = Number(input.value);       // record the selected answer index
                if (index === currentSlide) {
                    nextBtn.disabled = false;  // enable Next button once an option is selected
                }
            });
            label.appendChild(input);
            // Append the answer text to the label
            label.appendChild(document.createTextNode("  " + answerObj.text));
            optionsElem.appendChild(label);
        });

        slide.appendChild(optionsElem);
        questionContainer.appendChild(slide);
    });

    // Show the first slide
    showSlide(0);
}


// Function to show a specific slide
function showSlide(n) {
    const slides = document.querySelectorAll('.slide');
    console.log(currentSlide)
    if (slides[currentSlide] != undefined) {
        slides[currentSlide].classList.remove('active-slide');   // hide current question
        slides[n].classList.add('active-slide');                 // show target question
        currentSlide = n;
        // Handle Back button visibility
        backBtn.style.display = (currentSlide === 0) ? 'none' : 'inline-block';
        // Handle Next/Submit button visibility on last slide
        if (currentSlide === slides.length - 1) {
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'inline-block';
            skipBtn.style.display = 'none';  // hide Skip on last question
        } else {
            nextBtn.style.display = 'inline-block';
            submitBtn.style.display = 'none';
            skipBtn.style.display = 'inline-block';
        }
        // Set Next button disabled state based on whether current question already answered
        const anyChecked = !!document.querySelector(`input[name="question${currentSlide}"]:checked`);
        nextBtn.disabled = !anyChecked;
    }
}

// Initialize the quiz container to be hidden initially
document.getElementById('quiz-container').style.display = 'none';

// Function to fetch the latest question sets and attempts from the backend
async function fetchLatestData() {
    try {
        const questionSetsResponse = await fetch('../questionsets');
        const attemptsResponse = await fetch('../attempts');

        if (!questionSetsResponse.ok || !attemptsResponse.ok) {
            throw new Error('Failed to fetch data from the backend');
        }

        const questionSets = await questionSetsResponse.json();
        const attempts = await attemptsResponse.json();

        // Merge the fetched data
        const mergedData = [];
        questionSets.forEach(qs => {
            const attempt = attempts.find(at => at.questionsetId === qs.questionsetId);
            if (attempt) {
                mergedData.push({
                    ...qs,
                    ...attempt
                });
            } else {
                mergedData.push(qs);
            }
        });

        // Update the global merged variable and refresh the table
        global_questionSets = questionSets
        global_attempts = attempts
        merged = mergedData;
        // refreshTable();
    } catch (error) {
        console.error('Error fetching latest data:', error);
    }
}

// Call the function to fetch and merge data initially
refreshTable();


// Function to refresh the table
async function refreshTable() {

    await fetchLatestData();
    const tbody = document.getElementById('quiz-table-body');
    tbody.innerHTML = ''; // Clear existing rows
    createTableRows(merged); // Repopulate the table with updated data
}


function goNext() {
    // Only proceed if an answer is selected (safety check)
    if (!nextBtn.disabled) {
        showSlide(currentSlide + 1);
    }
}

function goBack() {
    showSlide(currentSlide - 1);
}

function skipQuestion() {
    // Mark current question as skipped (no answer)
    userAnswers[currentSlide] = undefined;
    // Clear any selected radio in this question (so it's truly unanswered)
    document.querySelectorAll(`input[name="question${currentSlide}"]`).forEach(input => {
        input.checked = false;
    });
    showSlide(currentSlide + 1);
}

// Attach event listeners to navigation buttons
backBtn.addEventListener('click', goBack);
nextBtn.addEventListener('click', goNext);
skipBtn.addEventListener('click', skipQuestion);

// ...existing code...

async function submitQuiz() {
    // Disable all inputs to prevent changes after submission
    document.querySelectorAll('input[type="radio"]').forEach(input => {
        input.disabled = true;
    });

    const allResults = [];
    const correctResults = [];
    const wrongResults = [];

    // Evaluate each question
    quizData.questions.forEach((q, index) => {
        const correctIdx = q.choices.findIndex(answerObj => answerObj.isCorrect);
        const userIdx = userAnswers[index];
        const result = {
            question: q.text,
            choices: q.choices,
            correctIdx: correctIdx,
            userIdx: userIdx
        };
        allResults.push(result);
        if (userIdx === correctIdx) {
            correctResults.push(result);
        } else {
            wrongResults.push(result);
        }
    });

    // Hide the quiz container and navigation buttons
    document.getElementById('quiz-container').style.display = 'none';
    document.getElementById('navigation').style.display = 'none';

    // Show the results container
    document.getElementById('results-container').style.display = 'block';
    showTab('all')

    // Update the result tab buttons with counts
    document.querySelector('button[onclick="showTab(\'all\')"]').textContent = `All (${allResults.length})`;
    document.querySelector('button[onclick="showTab(\'correct\')"]').textContent = `Correct (${correctResults.length})`;
    document.querySelector('button[onclick="showTab(\'wrong\')"]').textContent = `Wrong (${wrongResults.length})`;

    // Populate the results tabs
    populateResultsTab('all', allResults);
    populateResultsTab('correct', correctResults);
    populateResultsTab('wrong', wrongResults);

    // Prepare data for upsert
    const incorrectQuestionIds = wrongResults.map((result, index) => ({
        S: index.toString()
    }));

    try {

        console.log(quizData)

        const upsertData = {
            questionsetId: quizData.questionsetId,
            incorrect_questionids: incorrectQuestionIds,        
            result: {
                    attempted: allResults.length.toString(),
                    correct: correctResults.length.toString(),
                    incorrect: wrongResults.length.toString()                
                }
            }
        
        console.log(upsertData)


        const response = await fetch(`../attempts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(upsertData)
        });

        if (!response.ok) {
            throw new Error('Failed to upsert attempt data');
        }

        console.log('Attempt data upserted successfully');
    } catch (error) {
        console.error('Error upserting attempt data:', error);
    }
}

// Function to go back to the Question Sets
function goBackToQuestionSets() {
    document.getElementById('results-container').style.display = 'none';    
    document.getElementById('dashboard').style.display = 'block';
    refreshTable();
}

// Attach event listener to the submit button
submitBtn.addEventListener('click', submitQuiz);

// ...existing code...
/*
function populateResultsTab(tabId, results) {
    const tabContent = document.getElementById(tabId);
    tabContent.innerHTML = ''; // Clear existing content

    results.forEach(result => {
        const questionElem = document.createElement('div');
        questionElem.className = 'result-question';
        questionElem.textContent = result.question;

        const choicesElem = document.createElement('div');
        choicesElem.className = 'result-choices';

        result.choices.forEach((choice, idx) => {
            const choiceElem = document.createElement('div');
            choiceElem.className = 'result-choice';
            choiceElem.textContent = choice.text;

            if (idx === result.correctIdx) {
                choiceElem.classList.add('correct');
            }
            if (idx === result.userIdx && idx !== result.correctIdx) {
                choiceElem.classList.add('incorrect');
            }

            choicesElem.appendChild(choiceElem);
        });

        tabContent.appendChild(questionElem);
        tabContent.appendChild(choicesElem);
    });
}
*/

function populateResultsTab(tabId, results) {
    const tabContent = document.getElementById(tabId);
    tabContent.innerHTML = ''; // Clear existing content

    results.forEach(result => {
        const questionElem = document.createElement('div');
        questionElem.className = 'result-question';
        questionElem.textContent = result.question;

        const choicesElem = document.createElement('div');
        choicesElem.className = 'result-choices';

        result.choices.forEach((choice, idx) => {
            const choiceElem = document.createElement('div');
            choiceElem.className = 'result-choice';
            choiceElem.textContent = choice.text;

            if (idx === result.correctIdx) {
                choiceElem.classList.add('correct');
            }
            if (idx === result.userIdx && idx !== result.correctIdx) {
                choiceElem.classList.add('incorrect');
                const feedbackElem = document.createElement('div');
                feedbackElem.className = 'feedback';
                feedbackElem.textContent = `${choice.targetedResponse}`;
                choiceElem.appendChild(feedbackElem);
            }

            choicesElem.appendChild(choiceElem);
        });

        tabContent.appendChild(questionElem);
        tabContent.appendChild(choicesElem);
    });
}


function showTab(tabId) {
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => {
        tab.style.display = 'none';
    });

    document.getElementById(tabId).style.display = 'block';
}

// Helper function to format the date and time
function formatDateTime(timestamp) {
    if (!timestamp) return ' - ';
    const date = new Date(timestamp);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = String(date.getFullYear());
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${day}-${month}-${year} ${hours}:${minutes}`;
}