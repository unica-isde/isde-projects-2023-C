

$(document).ready(function () {
    var scripts = document.getElementById('makeGraph');
    var classification_scores = scripts.getAttribute('classification_scores');
    makeGraph(classification_scores);
});

function makeGraph(results) {
    console.log(results);
    results = JSON.parse(results);
    var ctx = document.getElementById("histogramOutput").getContext('2d');

}