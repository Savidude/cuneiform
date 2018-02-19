const USER = "user";
const SYSTEM = "system";
const NONE = "None";
const INFO = "system:info";

var isTryVisible = false;
var isCodeVisible = true;

var currentIntent;
var sessionId = "123";

var intentCodeEditor;
var newNodeEditor;
var nodeCodeEditor;

var nodes = [];

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

    newNodeEditor = CodeMirror(document.getElementById("new-node-code-editor"), {
        mode: "javascript",
        theme: "elegant",
        lineNumbers: true
    });
    newNodeEditor.refresh();

    intentCodeEditor = CodeMirror(document.getElementById("intent-code-editor"), {
        mode: "javascript",
        theme: "elegant",
        lineNumbers: true
    });

    nodeCodeEditor = CodeMirror(document.getElementById("node-code-editor"), {
        mode: "javascript",
        theme: "elegant",
        lineNumbers: true
    });
});

function loadIntentCodeEditor() {
    setTimeout(function () {
        intentCodeEditor.refresh();
    }, 500);
}

function sendMessage() {
    var messageText = document.getElementById("message-text");
    var message = messageText.value;
    messageText.value = "";

    if (message !== "") {
        var messageData = {};
        messageData['sessionid'] = sessionId;
        messageData['message'] = message;
        if (message !== INFO) {
            generateMessage(USER, message);
        }

        $.ajax({
            type: "POST",
            contentType: 'application/json',
            dataType: "json",
            url: "/operation/responder",
            data: JSON.stringify(messageData),
            success: function (result) {
                sessionId = result['sessionid'];
                var response = result['response'];
                var actionType = result['action_type'];
                if (response !== NONE) {
                    generateMessage(SYSTEM, response);
                }
                //Send an empty message if the action type is "info"
                if (actionType === "info") {
                    messageText.value = INFO;
                    sendMessage();
                }
            },
            error: function (error) {
                if (error.status === 500) {
                    //TODO: Display error
                }
            }
        });
    }
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
    document.getElementById("variables-table-body").innerHTML = "";

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
            nodes = result.nodes;
            if (globalVariables !== null) {
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
            }
            updateIntentCode();
            showNodes();
            generateGraph(nodes);
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
        updateIntentCode();
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

    document.getElementById("variables-table-body").appendChild(row);
}

function updateIntentCode() {
    var intentName = currentIntent;
    var globalVariables = getGlobalVariables();

    var code = generateCuneiformCode();
    intentCodeEditor.getDoc().setValue(code);
    setTimeout(function () {
        this.intentCodeEditor.refresh();
    }, 1);

    function getGlobalVariables() {
        var variablesTableBody = document.getElementById("variables-table-body");
        var rows = variablesTableBody.childNodes;
        var globalVariables = [];
        for (var i = 0; i < rows.length; i++) {
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

    function generateCuneiformCode() {
        var code = intentName + ' {\n';
        code += generateGlobalVariableCode();
        code += '\n';
        code += genereateNodeCode();
        code += '}';
        return code;

        function generateGlobalVariableCode() {
            var globalVariableCode = '';
            globalVariables.forEach(function (variable) {
                var name = variable.name;
                var value = variable.value;
                globalVariableCode += '\tvar ' + name;
                if (value === null) {
                    globalVariableCode += ';\n';
                } else {
                    if (isNaN(value)) {
                        globalVariableCode += ' = "' + value + '";\n';
                    } else {
                        globalVariableCode += ' = ' + value + ';\n'
                    }
                }
            });
            return globalVariableCode;
        }

        function genereateNodeCode() {
            var nodesCode = '';
            if (nodes !== null) {
                nodes.forEach(function (node) {
                    var nodeCode = '';
                    var name = node.name;
                    nodeCode += '\tnode ' + name + ' {\n';

                    var priority = node.priority;
                    nodeCode += '\t\tpriority : ' + priority + ';\n\n';

                    var preconditions = node.preconditions;
                    nodeCode += '\t\tpreconditions {\n';
                    if (preconditions === null) {
                        preconditions = "";
                    }
                    nodeCode += '\t\t\t' + preconditions + '\n';
                    nodeCode += '\t\t}\n\n';

                    var actionCode = node.action_code;
                    nodeCode += '\t\taction {\n';
                    nodeCode += '\t\t\t' + actionCode + '\n';
                    nodeCode += '\t\t}\n';

                    nodeCode += '\t}\n';

                    nodesCode += nodeCode;
                });
            }
            return nodesCode;
        }
    }
}

function saveIntentCode() {
    var intentCode = intentCodeEditor.getValue();

    var l = Ladda.create(document.querySelector("#save-btn"));
    l.start();

    $.ajax({
        type: "POST",
        contentType: 'text/plain',
        dataType: "json",
        url: "/operation/intent/" + currentIntent + "/save",
        data: intentCode,
        success: function (result) {
            l.stop();
        },
        error: function (error) {
            if (error.status === 500) {
                //TODO: Display error
            }
        }
    });
}

function clearNodeEditor() {
    newNodeEditor.getDoc().setValue("");
    nodeCodeEditor.getDoc().setValue("");
}

function createNode() {
    var nameText = document.getElementById("name-text");
    var name = nameText.value;
    nameText.value = "";

    var priorityNum = document.getElementById("priority-input");
    var priority = priorityNum.value;
    priorityNum.value = 5;

    var preconditionsText = document.getElementById("preconditions-text");
    var preconditions = preconditionsText.value;
    preconditionsText.value = "";

    var actionCode = newNodeEditor.getValue();
    newNodeEditor.getDoc().setValue("");

    var node = {};
    node['name'] = name;
    node['priority'] = priority;
    node['preconditions'] = preconditions;
    node['action_code'] = actionCode;
    nodes.push(node);

    showNodes();
    updateIntentCode();
}

function showNodes() {
    var nodesList = document.getElementById("nodes-list");
    nodesList.innerHTML = "";

    if (nodes !== null) {
        nodes.forEach(function (node) {
            var card = document.createElement("div");
            card.classList.add("card");

            var cardBody = document.createElement("div");
            cardBody.classList.add("card-body");
            card.appendChild(cardBody);

            var nodeName = document.createElement("h4");
            nodeName.classList.add("card-title");
            nodeName.innerHTML = node.name;
            cardBody.appendChild(nodeName);

            var nodePriority = document.createElement("h6");
            nodePriority.classList.add("card-subtitle");
            nodePriority.classList.add("mb-2");
            nodePriority.classList.add("text-muted");
            nodePriority.innerHTML = "Priority: " + node.priority;
            cardBody.appendChild(nodePriority);

            var nodePreconditions = document.createElement("p");
            nodePreconditions.classList.add("card-text");
            nodePreconditions.innerHTML = "Preconditions:<br>" + node.preconditions;
            cardBody.appendChild(nodePreconditions);

            var nodeActionButton = document.createElement("button");
            nodeActionButton.setAttribute("type", "button");
            nodeActionButton.classList.add("btn");
            nodeActionButton.classList.add("btn-outline-secondary");
            nodeActionButton.classList.add("btn-lg");
            nodeActionButton.classList.add("btn-block");
            nodeActionButton.innerHTML = '<i class="mdi mdi-code-braces"></i>' +
                '<span>Action Code</span>';
            nodeActionButton.onclick = function () {
                $('#node-action-modal').modal('show');
                nodeCodeEditor.getDoc().setValue(node.action_code);

                document.getElementById("update-btn").onclick = function () {
                    node['action_code'] = nodeCodeEditor.getValue();
                };
            };
            cardBody.appendChild(nodeActionButton);
            nodesList.appendChild(card);
        });
    }
}