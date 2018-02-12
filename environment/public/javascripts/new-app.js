const USER = "user";
const SYSTEM = "system";
const NONE = "None";

var isTryVisible = false;
var isCodeVisible = true;

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

    $("#properties").hide();

    $("#var-name").keypress(function (event) {
        variableKeyPressed(event)
    });
    $("#var-value-text").keypress(function (event) {
        variableKeyPressed(event)
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

    var intentData = {};
    intentData['name'] = intent.name;
    $.ajax({
        type: "POST",
        contentType: 'application/json',
        dataType: "json",
        url: "/operation/intent/code",
        data: JSON.stringify(intentData),
        success: function (result) {
            var globalVariables = result.global_variables;
            globalVariables.forEach(function (variable) {
                var name = variable.name;
                var value;
                if (variable.value === null) {
                    value = "";
                } else {
                    value = variable.value;
                }
                showVariable(name, value);
            });
        },
        error: function (error) {
            if (error.status === 500) {
                //TODO: Display error
            }
        }
    });
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
        if (isCodeVisible) {
            $('#code').addClass('animated slideOutRight').one(animationEnd, function () {
                $(this).removeClass('animated slideOutRight');
                $(this).hide()

                $('#properties').show();
                $('#properties').addClass('animated slideInRight').one(animationEnd, function () {
                    $(this).removeClass('animated slideInRight');
                });
            });
            isCodeVisible = false;
        } else {
            $('#properties').show();
            $('#properties').addClass('animated slideInRight').one(animationEnd, function () {
                $(this).removeClass('animated slideInRight');
            });
        }
    }
    isTryVisible = !isTryVisible;
}

function toggleIntentCode() {
    if (isCodeVisible) {
        $('#code').addClass('animated slideOutRight').one(animationEnd, function () {
            $(this).removeClass('animated slideOutRight');
            $(this).hide()
        });
    } else {
        if (isTryVisible) {
            $('#properties').addClass('animated slideOutRight').one(animationEnd, function () {
                $(this).removeClass('animated slideOutRight');
                $(this).hide();

                $('#code').show();
                $('#code').addClass('animated slideInRight').one(animationEnd, function () {
                    $(this).removeClass('animated slideInRight');
                });
            });
            isTryVisible = false;
        } else {
            $('#code').show();
            $('#code').addClass('animated slideInRight').one(animationEnd, function () {
                $(this).removeClass('animated slideInRight');
            });
        }

    }
    isCodeVisible = !isCodeVisible;
}

function toggleVarType() {
    var text = document.getElementById("var-value-text");
    var select = document.getElementById("var-value-select");

    if (text.style.display === "none") {
        text.style.display = "block";
    } else {
        text.style.display = "none";
    }

    if (select.style.display === "none") {
        select.style.display = "block";
    } else {
        select.style.display = "none";
    }
}

function variableKeyPressed(event) {
    if (event.which === 13) { //Enter key is pressed
        var varName = $("#var-name");
        var name = varName.val();
        varName.val("");

        var varValueText = $("#var-value-text");
        var value = varValueText.val();
        varValueText.val("");

        showVariable(name, value);
        varName.focus();
    }
}

function showVariable(name, value) {
    var row = document.createElement("tr");

    var nameData = document.createElement("td");
    nameData.innerHTML = name;
    row.appendChild(nameData);

    var valueData = document.createElement("td");
    valueData.innerHTML = value;
    row.appendChild(valueData);

    var buttonData = document.createElement("td");
    var deleteButton = document.createElement("button");
    deleteButton.classList.add("btn");
    deleteButton.classList.add("btn-icon");
    deleteButton.innerHTML = '<i class="mdi mdi-close-circle"></i>';
    deleteButton.onclick = function () {
        row.remove()
    };
    buttonData.appendChild(deleteButton);
    row.appendChild(buttonData);

    document.getElementById("variables-table").append(row);
}

function saveIntentCode() {
    var intentName = currentIntent;
    var globalVariables = getGlobalVariables();

    var intent = {};
    intent['name'] = intentName;
    intent['global_variables'] = globalVariables;

    var l = Ladda.create(document.querySelector("#save-btn"));
    l.start();

    $.ajax({
        type: "POST",
        contentType: 'application/json',
        dataType: "json",
        url: "/operation/intent/save",
        data: JSON.stringify(intent),
        success: function (result) {
            l.stop();
        },
        error: function (error) {
            if (error.status === 500) {
                //TODO: Display error
            }
        }
    });
    
    function getGlobalVariables() {
        var variablesTable = document.getElementById("variables-table");
        var rows = variablesTable.childNodes;
        var globalVariables = [];
        for (var i = 3; i < rows.length; i++) {
            var varData = rows[i].childNodes;
            var name = varData[0].innerHTML;
            var value = varData[1].innerHTML;
            if (value === "") {
                value = null;
            } else if (!isNaN(Number(value))) {
                value = Number(value);
            }

            var variable = {};
            variable['name'] = name;
            variable['value'] = value;
            globalVariables.push(variable);
        }
        return globalVariables;
    }
}