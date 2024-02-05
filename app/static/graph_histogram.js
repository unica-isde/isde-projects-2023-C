
$(document).ready(function () {
    var scripts = document.getElementById('makeHistogram');
    var image = document.getElementById("image");
    image.onload = makeGraph;
});

function makeGraph() {
    /* Function dedicated to the histogram generation. */

    var image = document.getElementById("image");
    var canvas = document.getElementById('histogramOutput');
    var ctx = canvas.getContext('2d'); //added

    ctx.drawImage(image, 0, 0, canvas.width, canvas.height);

    // Histogram settings
    let src = cv.imread('histogramOutput');
    cv.cvtColor(src, src, cv.COLOR_RGBA2GRAY, 0);
    let srcVec = new cv.MatVector();
    srcVec.push_back(src);
    let accumulate = false;
    let channels = [0];
    let histSize = [256];
    let ranges = [0, 255];
    let hist = new cv.Mat();
    let mask = new cv.Mat();
    let color = new cv.Scalar(255, 255, 255);
    let scale = 2;

    // Histogram processing
    cv.calcHist(srcVec, channels, mask, hist, histSize, ranges, accumulate);
    let result = cv.minMaxLoc(hist, mask);
    let max = result.maxVal;
    let dst = new cv.Mat.zeros(src.rows, histSize[0] * scale,
        cv.CV_8UC3);

    // Draw histogram
    for (let i = 0; i < histSize[0]; i++) {
        let binVal = hist.data32F[i] * src.rows / max;
        let point1 = new cv.Point(i * scale, src.rows - 1);
        let point2 = new cv.Point((i + 1) * scale - 1, src.rows - binVal);
        cv.rectangle(dst, point1, point2, color, cv.FILLED);
    }

    cv.imshow('histogramOutput', dst);
    src.delete();
    dst.delete();
    srcVec.delete();
    mask.delete();
    hist.delete();

}


