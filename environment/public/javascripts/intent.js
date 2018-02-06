var slots = [];

$( document ).ready(function() {
    $("#synonyms-text").keypress(function (event) {
        synonymsTextKeyPressed(event)
    });

    $("#value-text").keypress(function (event) {
        valueTextKeyPressed(event)
    });

    $("#utterance-text").keypress(function (event) {
        utteranceTextKeyPressed(event)
    });
});

function valueTextKeyPressed(event) {
    if (event.which === 13) { //Enter key is pressed
        enterKeyPressed();
    }
}

function synonymsTextKeyPressed(event) {
    if (event.which === 0) { //Tab key is pressed
        var synonymsText = $("#synonyms-text");
        var value = synonymsText.val();
        synonymsText.val('');
        event.preventDefault();

        button = createSynonym(value);
        var synonymsCol = document.getElementById("synonyms-col");
        synonymsCol.appendChild(button);

    } else if (event.which === 13) { //Enter key is pressed
        enterKeyPressed();
    }
}

function enterKeyPressed() {
    var slotValueText = $("#value-text");
    var slotValue = slotValueText.val();
    slotValueText.val('');

    var synonyms = [];

    var synonymsCol = document.getElementById("synonyms-col");
    var buttons = synonymsCol.childNodes;
    for (var i = 0; i < buttons.length; i++) {
        var spans = buttons[i].childNodes;
        var value = spans[1].innerHTML;
        synonyms.push(value)
    }
    synonymsCol.innerHTML = "";

    var slotData = document.getElementById("slot-data");
    slotData.appendChild(addSlotValue(slotValue, synonyms));

    document.getElementById("value-text").focus();
}

function createSynonym(value) {
    var button = document.createElement("div");
    button.classList.add("btn");
    button.classList.add("btn-outline-primary");

    var closeButton = document.createElement('span');
    closeButton.innerHTML = "&times;&nbsp;";
    closeButton.onclick = function () {
        button.remove();
    };
    var buttonText = document.createElement('span');
    buttonText.innerHTML = value;

    button.appendChild(closeButton);
    button.appendChild(buttonText);
    return button
}

function addSlotValue(slotValue, synonymsArray) {
    var slotValueP = document.createElement("p");
    slotValueP.classList.add("h5");
    slotValueP.innerHTML = slotValue;

    var slotValueData = document.createElement('td');
    slotValueData.appendChild(slotValueP);

    var synonymsData = document.createElement('td');

    synonymsArray.forEach(function(synonym) {
        var button = createSynonym(synonym);
        synonymsData.appendChild(button);
    });

    var row = document.createElement('tr');
    row.appendChild(slotValueData);
    row.appendChild(synonymsData);
    return row;
}

function updateSlot() {
    var slotData = {};

    var slotName = $("#slot-name").val();
    var isUpdatingSlot = false;
    slots.forEach(function (slot) {
        if (slot.name === slotName) {
            isUpdatingSlot = true;
        }
    });

    var slotDataTable = document.getElementById("slot-data");
    var slotDataRows = slotDataTable.rows;

    var values = [];
    var synonyms = [];
    for (var i = 0; i < slotDataRows.length; i++) {
        var row = slotDataRows[i].childNodes;

        var valueCol = row[0];
        var value = valueCol.childNodes[0].innerHTML;
        values.push(value);

        var synonymsCol = row[1];
        var synonymsButtons = synonymsCol.childNodes;
        if (synonymsButtons.length > 0) {
            var synonymData = {};
            synonymData['value'] = value;
            var synonymsArray = [];
            for (var j = 0; j < synonymsButtons.length; j++) {
                var spans = synonymsButtons[j].childNodes;
                var synonym = spans[1].innerHTML;
                synonymsArray.push(synonym);
            }
            synonymData['synonyms'] = synonymsArray;
            synonyms.push(synonymData);
        }
    }

    slotDataTable.innerHTML = "";
    $("#createSlotModal").modal('hide');

    if (!isUpdatingSlot) {
        slotData['name'] = slotName;
        slotData['values'] = values;
        slotData['synonyms'] = synonyms;

        showCreatedSlot(slotData);
        slots.push(slotData);
    } else {
        slots.forEach(function (slot) {
            if (slot.name === slotName) {
                slot['values'] = values;
                slot['synonyms'] = synonyms;
            }
        });
    }

}

function showCreatedSlot(slotData) {
    var createdSlotsDiv = document.getElementById("created-slots");

    var slot = document.createElement("div");
    slot.classList.add("created-slot");

    var slotNameSpan = document.createElement('span');
    slotNameSpan.classList.add("h5");
    slotNameSpan.innerHTML = "{ " + slotData.name + " }";
    slot.appendChild(slotNameSpan);

    var deleteButton = document.createElement("button");
    deleteButton.setAttribute("type", "button");
    deleteButton.classList.add("btn");
    deleteButton.classList.add("btn-danger");
    deleteButton.innerHTML = '<i class="mdi mdi-delete"></i>';
    deleteButton.onclick = function () {
        var index = slots.indexOf(slotData);
        slots.splice(index, 1);
        slot.remove();
        console.log(JSON.stringify(slots, null, 2));
    };
    slot.appendChild(deleteButton);

    var editButton = document.createElement("button");
    editButton.setAttribute("type", "button");
    editButton.classList.add("btn");
    editButton.classList.add("btn-secondary");
    editButton.innerHTML = '<i class="mdi mdi-pencil"></i>';
    editButton.onclick = function () {
        $("#createSlotModal").modal('show');
        populateCreateSlotModal(slotData);
    };
    slot.appendChild(editButton);

    createdSlotsDiv.appendChild(slot)
}

function populateCreateSlotModal(slotData) {
    document.getElementById("slot-name").value = slotData.name;

    var slotDataTable = document.getElementById("slot-data");
    var values = slotData.values;
    var synonyms = slotData.synonyms;
    values.forEach(function (slotValue) {
        var slotSynonyms = [];
        synonyms.forEach(function (synonym) {
            if (synonym.value === slotValue) {
                slotSynonyms = synonym.synonyms;
            }
        });
        slotDataTable.appendChild(addSlotValue(slotValue, slotSynonyms));
    });
}

function utteranceTextKeyPressed(event) {
    if (event.which === 13) { //Enter key is pressed
        var utteranceText = $("#utterance-text");
        var utterance = utteranceText.val();
        utteranceText.val('');

        var sampleUtterancesDiv = document.getElementById("sample-utterances");
        var utteranceDiv = document.createElement("div");
        utteranceDiv.classList.add("sample-utterance");

        var spanIcon = document.createElement("span");
        spanIcon.classList.add("input-group-btn");
        spanIcon.innerHTML = '<button type="button" class="btn btn-icon">' +
                                    '<i class="mdi mdi-format-quote-open"></i>' +
                            '</button>';
        utteranceDiv.appendChild(spanIcon);

        var utteranceTextSpan = document.createElement('span');
        utteranceTextSpan.classList.add("h5");
        utteranceTextSpan.innerHTML = utterance;
        utteranceDiv.appendChild(utteranceTextSpan);

        var deleteButton = document.createElement("button");
        deleteButton.setAttribute("type", "button");
        deleteButton.classList.add("btn");
        deleteButton.classList.add("btn-icon");
        deleteButton.classList.add("delete-utterance");
        deleteButton.innerHTML = '<i class="mdi mdi-close-circle"></i>';
        deleteButton.onclick = function () {
            utteranceDiv.remove();
        };
        utteranceDiv.appendChild(deleteButton);

        sampleUtterancesDiv.appendChild(utteranceDiv);
    }
}

function updateIntent(){
    var intentNameText = $("#intent-name");
    var intentName = intentNameText.val();

    var initiativeSelect = document.getElementById('initiative-select');
    var initiative = initiativeSelect.options[initiativeSelect.selectedIndex].value;

    var sampleUtterances = [];
    var sampleUtterancesDiv = document.getElementById("sample-utterances");
    var utteranceDivs = sampleUtterancesDiv.childNodes;
    for (var i = 0; i < utteranceDivs.length; i++) {
        var spans = utteranceDivs[i].childNodes;
        var utterance = spans[1].innerHTML;
        sampleUtterances.push(utterance);
    }

    var intent = {};
    intent['name'] = intentName;
    intent['initiative'] = initiative;
    intent['sample_utterances'] = sampleUtterances;
    intent['slots'] = slots;

    // console.log(JSON.stringify(intent, null, 2));
    $.ajax({
        type: "POST",
        contentType: 'application/json',
        dataType: "json",
        url: "/operation/intent/update",
        data: JSON.stringify(intent),
        success: function (result) {
            window.location = '/app';
        },
        error: function (error) {
            if (error.status === 500) {
                //TODO: Display error
            }
        }
    });
}

function clearModal() {
    document.getElementById("slot-name").value = "";
    document.getElementById("value-text").value = "";
    document.getElementById("synonyms-text").value = "";
    document.getElementById("slot-data").innerHTML = "";
}