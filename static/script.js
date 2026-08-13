// =======================================================
// CAPSTONE AI PIPELINE
// Part 1 - Authentication & Dashboard
// =======================================================

// ---------- DOM ELEMENTS ----------

const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");

const loginBtn = document.getElementById("loginBtn");

const loginStatus = document.getElementById("loginStatus");

const tokenBox = document.getElementById("tokenBox");

const showTokenBtn = document.getElementById("showTokenBtn");
const copyTokenBtn = document.getElementById("copyTokenBtn");
const clearTokenBtn = document.getElementById("clearTokenBtn");

const healthBtn = document.getElementById("healthBtn");
const dashboardBtn = document.getElementById("dashboardBtn");
const historyBtn = document.getElementById("historyBtn");

const loadingOverlay = document.getElementById("loadingOverlay");
const toast = document.getElementById("toast");

const jsonResponse = document.getElementById("jsonResponse");

let tokenVisible = false;

// =======================================================
// Utility Functions
// =======================================================

function showLoading() {
    loadingOverlay.classList.remove("hidden");
}

function hideLoading() {
    loadingOverlay.classList.add("hidden");
}

function showToast(message) {

    toast.innerText = message;

    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 2500);
}

function updateJsonViewer(data) {

    jsonResponse.textContent = JSON.stringify(
        data,
        null,
        4
    );

}

function getToken() {

    return localStorage.getItem("jwt_token");

}

function setToken(token) {

    localStorage.setItem(
        "jwt_token",
        token
    );

}

function removeToken() {

    localStorage.removeItem(
        "jwt_token"
    );

}

function maskToken(token) {

    if (!token)
        return "";

    if (token.length < 30)
        return token;

    return (
        token.substring(0, 20)
        +
        "*********************"
        +
        token.substring(token.length - 15)
    );

}

function displayStoredToken() {

    const token = getToken();

    if (!token) {

        tokenBox.value = "";

        loginStatus.innerHTML =
            "Not Logged In";

        return;
    }

    if (tokenVisible)
        tokenBox.value = token;

    else
        tokenBox.value = maskToken(token);

}

// =======================================================
// Generic Fetch Wrapper
// =======================================================

async function apiCall(
    endpoint,
    method = "GET",
    body = null,
    requiresAuth = false
) {

    const headers = {
        "Content-Type": "application/json"
    };

    if (requiresAuth) {

        const token = getToken();

        if (!token)
            throw new Error(
                "Please login first."
            );

        headers["Authorization"] =
            "Bearer " + token;
    }

    const options = {
        method,
        headers
    };

    if (body)
        options.body =
            JSON.stringify(body);

    const response =
        await fetch(endpoint, options);

    const data =
        await response.json();

    if (!response.ok)
        throw new Error(
            data.detail ||
            "API Error"
        );

    return data;

}

// =======================================================
// LOGIN
// =======================================================

loginBtn.addEventListener(
    "click",
    async () => {

        const username =
            usernameInput.value.trim();

        const password =
            passwordInput.value.trim();

        if (!username || !password) {

            showToast(
                "Enter username and password."
            );

            return;
        }

        showLoading();

        try {

            const result =
                await apiCall(
                    "/token",
                    "POST",
                    {
                        username,
                        password
                    }
                );

            setToken(
                result.access_token
            );

            tokenVisible = false;

            displayStoredToken();

            loginStatus.innerHTML =
                "✅ Logged in as <b>"
                + username +
                "</b>";

            updateJsonViewer(result);

            showToast(
                "Login Successful!"
            );

        }

        catch (err) {

            showToast(
                err.message
            );

        }

        finally {

            hideLoading();

        }

    }
);

// =======================================================
// TOKEN BUTTONS
// =======================================================

showTokenBtn.addEventListener(
    "click",
    () => {

        tokenVisible =
            !tokenVisible;

        showTokenBtn.innerText =
            tokenVisible
                ? "Hide"
                : "Show";

        displayStoredToken();

    }
);

copyTokenBtn.addEventListener(
    "click",
    () => {

        const token =
            getToken();

        if (!token) {

            showToast(
                "No token found."
            );

            return;
        }

        navigator.clipboard.writeText(
            token
        );

        showToast(
            "Token copied!"
        );

    }
);

clearTokenBtn.addEventListener(
    "click",
    () => {

        removeToken();

        displayStoredToken();

        loginStatus.innerHTML =
            "Not Logged In";

        showToast(
            "Token removed."
        );

    }
);

// =======================================================
// HEALTH
// =======================================================

healthBtn.addEventListener(
    "click",
    async () => {

        showLoading();

        try {

            const result =
                await apiCall(
                    "/health"
                );

            updateJsonViewer(
                result
            );

            showToast(
                "Health loaded."
            );

        }

        catch (err) {

            showToast(
                err.message
            );

        }

        finally {

            hideLoading();

        }

    }
);

// =======================================================
// DASHBOARD
// =======================================================

dashboardBtn.addEventListener(
    "click",
    async () => {

        showLoading();

        try {

            const result =
                await apiCall(
                    "/dashboard",
                    "GET",
                    null,
                    true
                );

            updateJsonViewer(
                result
            );

            showToast(
                "Dashboard loaded."
            );

        }

        catch (err) {

            showToast(
                err.message
            );

        }

        finally {

            hideLoading();

        }

    }
);

// =======================================================
// HISTORY
// =======================================================

historyBtn.addEventListener(
    "click",
    async () => {

        showLoading();

        try {

            const result =
                await apiCall(
                    "/history",
                    "GET",
                    null,
                    true
                );

            updateJsonViewer(
                result
            );

            showToast(
                "History loaded."
            );

        }

        catch (err) {

            showToast(
                err.message
            );

        }

        finally {

            hideLoading();

        }

    }
);

// =======================================================
// INITIALIZE
// =======================================================

displayStoredToken();

showToast(
    "Capstone AI Pipeline Ready"
);

// =======================================================
// PART 2 - AI CHAT & RESPONSE HANDLING
// Append this below Part 1
// =======================================================

// ---------- DOM ----------

const askBtn = document.getElementById("askBtn");

const questionInput = document.getElementById("question");

const answerContainer = document.getElementById("answerContainer");

const responseTime = document.getElementById("responseTime");

const cachedValue = document.getElementById("cachedValue");

const currentUser = document.getElementById("currentUser");

// =======================================================
// Escape HTML
// =======================================================

function escapeHtml(text) {

    if (!text) return "";

    const div = document.createElement("div");

    div.innerText = text;

    return div.innerHTML;

}

// =======================================================
// Render AI Response
// =======================================================

function renderAnswer(data) {

    answerContainer.innerHTML = "";

    const wrapper = document.createElement("div");

    wrapper.innerHTML = `

        <div style="
            white-space:normal;
            line-height:1.0;
            font-size:15px;
        ">
            ${escapeHtml(data.answer.trim())}
        </div>
    `;

    answerContainer.appendChild(wrapper);

}

// =======================================================
// Update Statistics
// =======================================================

function updateStatistics(data) {

    responseTime.innerText =
        Number(data.response_time).toFixed(3) + " sec";

    cachedValue.innerText =
        data.cached ? "Yes" : "No";

    currentUser.innerText =
        data.user;

}

// =======================================================
// ASK AI
// =======================================================

async function askQuestion() {

    const question =
        questionInput.value.trim();

    if (!question) {

        showToast("Please enter a question.");

        return;

    }

    showLoading();

    askBtn.disabled = true;

    askBtn.innerText = "Thinking...";

    try {

        const result =
            await apiCall(
                "/ask",
                "POST",
                {
                    question: question
                },
                true
            );

        renderAnswer(result);

        updateStatistics(result);

        updateJsonViewer(result);

        showToast("Answer generated.");

    }

    catch(err) {

        answerContainer.innerHTML =
            `
            <div style="
                color:#ef4444;
                font-size:16px;
            ">
                ❌ ${err.message}
            </div>
            `;

        showToast(err.message);

    }

    finally {

        hideLoading();

        askBtn.disabled = false;

        askBtn.innerText = "Ask Question";

    }

}

// =======================================================
// BUTTON EVENT
// =======================================================

askBtn.addEventListener(
    "click",
    askQuestion
);

// =======================================================
// ENTER TO SEND
// Shift+Enter -> New Line
// Enter -> Ask
// =======================================================

questionInput.addEventListener(
    "keydown",
    function(e){

        if(
            e.key==="Enter"
            &&
            !e.shiftKey
        ){

            e.preventDefault();

            askQuestion();

        }

    }
);

// =======================================================
// Restore Token On Refresh
// =======================================================

window.addEventListener(
    "load",
    ()=>{

        displayStoredToken();

        if(getToken()){

            loginStatus.innerHTML =
            "✅ Token loaded from browser";

        }

    }
);

// =======================================================
// Auto Resize Question Box
// =======================================================

questionInput.addEventListener(
    "input",
    ()=>{

        questionInput.style.height="auto";

        questionInput.style.height=
            questionInput.scrollHeight+"px";

    }
);

// =======================================================
// CTRL + L
// Focus Login Username
// =======================================================

document.addEventListener(
    "keydown",
    function(e){

        if(e.ctrlKey && e.key==="l"){

            e.preventDefault();

            usernameInput.focus();

        }

    }
);

// =======================================================
// CTRL + Q
// Focus Question Box
// =======================================================

document.addEventListener(
    "keydown",
    function(e){

        if(e.ctrlKey && e.key==="q"){

            e.preventDefault();

            questionInput.focus();

        }

    }
);

// =======================================================
// Copy Answer
// Double Click
// =======================================================

answerContainer.addEventListener(
    "dblclick",
    ()=>{

        navigator.clipboard.writeText(
            answerContainer.innerText
        );

        showToast(
            "Answer copied."
        );

    }
);

// =======================================================
// Periodic Health Check
// Every 60 seconds
// =======================================================

setInterval(async()=>{

    try{

        const data =
            await apiCall("/health");

        document.querySelector(".status-dot")
            .style.background="#22c55e";

    }

    catch{

        document.querySelector(".status-dot")
            .style.background="#ef4444";

    }

},60000);

// =======================================================
// Welcome Message
// =======================================================

answerContainer.innerHTML=`

<div style="
text-align:center;
padding:20px;
color:#94a3b8;
">

<h2>
🤖 Welcome
</h2>

<br>

Ask anything from your
knowledge base.

<br><br>

Examples:

<br><br>

• What is Retrieval Augmented Generation?

<br>

• Summarize document 2

<br>

• Explain LangChain

<br>

• What are embeddings?

</div>

`;

console.log(
    "Capstone AI Pipeline Frontend Loaded"
);