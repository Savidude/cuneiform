$( document ).ready(function() {
    var intentName = document.getElementById("intent-name").value;
    var intentData = {};
    intentData['name'] = intentName;

    $.ajax({
        type: "POST",
        contentType: 'application/json',
        dataType: "json",
        url: "/operation/intent/get",
        data: JSON.stringify(intentData),
        success: function (result) {
            generateIntentData(result);
        },
        error: function (error) {
            if (error.status === 404) {
                console.log("404 error")
            }
        }
    });
});

function generateIntentData(intent) {
    document.getElementById("intent-name-text").value = intent.name;

    var initiativeSelect = document.getElementById("initiative-select");
    initiativeSelect.value = intent.initiative;

    var sampleUtterances = intent.sample_utterances;
    sampleUtterances.forEach(function (utterance) {
        displayUtterance(utterance);
    });

    slots = intent.slots;
    slots.forEach(function (slot) {
        showCreatedSlot(slot);
    });
}