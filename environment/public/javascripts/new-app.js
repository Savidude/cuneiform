const USER = "user";
const SYSTEM = "system";
const NONE = "None";

var isTryVisible = true;
var currentIntent;
var sessionId = "123";

$( document ).ready(function() {
    $.ajax({
        type: "POST",
        contentType: 'application/json',
        dataType: "json",
        url: "/operation/intents",
        success: function (result) {
            addIntentNavs(result);
            showIntentEnvironment(result.intents[0]);
        },
        error: function (error) {
            if (error.status === 500) {
                //TODO: Display error
            }
        }
    });

    $("#message-text").keypress(function (event) {
        if (event.which == 13) { //Enter key is pressed
            sendMessage();
        }
    });
});

function sendMessage() {
    var messageText = document.getElementById("message-text");
    var message = messageText.value;
    messageText.value = "";

    var messageData = {};
    messageData['sessionid'] = sessionId;
    messageData['message'] = message;
    generateMessage(USER, message);

    $.ajax({
        type: "POST",
        contentType: 'application/json',
        dataType: "json",
        url: "/operation/responder",
        data: JSON.stringify(messageData),
        success: function (result) {
            sessionId = result['sessionid'];
            var response = result['response'];
            if (response !== NONE) {
                generateMessage(SYSTEM, response);
            }
        },
        error: function (error) {
            if (error.status === 500) {
                //TODO: Display error
            }
        }
    });
}

function generateMessage(actor, message) {
    var containerDiv = document.createElement("div");
    containerDiv.classList.add("row");
    containerDiv.classList.add("flex-nowrap");
    containerDiv.classList.add("message-row");
    containerDiv.classList.add("p-4");
    if (actor === USER) {
        containerDiv.classList.add("user");
    } else if (actor === SYSTEM) {
        containerDiv.classList.add("system");
    }

    var bubbleDiv = document.createElement("div");
    bubbleDiv.classList.add("bubble");
    containerDiv.appendChild(bubbleDiv);

    var messageDiv = document.createElement("div");
    messageDiv.classList.add("message");
    messageDiv.innerHTML = message;
    bubbleDiv.appendChild(messageDiv);

    var messageList = document.getElementById("message-list");
    messageList.appendChild(containerDiv);
}

function addIntentNavs(intents) {
    var intentArray = intents.intents;
    intentArray.forEach(function (intent) {
        var navLi = document.createElement('li');
        navLi.classList.add("nav-item");
        navLi.onclick = function () {
            showIntentEnvironment(intent);
        };

        var navA = document.createElement('a');
        navA.classList.add("nav-link");
        navA.classList.add("ripple");
        navA.innerHTML = intent.name;
        navLi.appendChild(navA);

        var sideNav = document.getElementById("sidenav");
        sideNav.appendChild(navLi);
    });
}

function showIntentEnvironment(intent) {
    currentIntent = intent.name;
    var intentName = document.getElementById("intent-name");
    intentName.innerHTML = intent.name;
}

function createNewIntent() {
    window.location = '/new-intent';
}

function getIntentProperties() {
    window.location = '/intent/' + currentIntent;
}

var animationEnd = (function(el) {
    var animations = {
        animation: 'animationend',
        OAnimation: 'oAnimationEnd',
        MozAnimation: 'mozAnimationEnd',
        WebkitAnimation: 'webkitAnimationEnd'
    };

    for (var t in animations) {
        if (el.style[t] !== undefined) {
            return animations[t];
        }
    }
})(document.createElement('div'));

function toggleTry() {
    if (isTryVisible) {
        $('#properties').addClass('animated slideOutRight').one(animationEnd, function () {
            $(this).removeClass('animated slideOutRight');
            $(this).hide()
        });
    } else {
        $('#properties').show();
        $('#properties').addClass('animated slideInRight').one(animationEnd, function () {
            $(this).removeClass('animated slideInRight');
        });
    }
    isTryVisible = !isTryVisible
}