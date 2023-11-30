

$(document).ready(function () {
    var scripts = document.getElementById('makeGraph');
    makeGraph();
});

function makeGraph() {
    //var ctx = document.getElementById("histogramOutput").getContext('2d');
    var image = document.getElementById("image")

    const canvas = document.getElementById('histogramOutput');
    const ctx = canvas.getContext('2d'); //added

    // Load image and generate histogram when the image is loaded
      ctx.drawImage(image, 0, 0, canvas.width, canvas.height);

      // Get image data
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imageData.data;

      // Create histogram
      const histogram = new Array(256).fill(0);

      for (let i = 0; i < data.length; i += 4) {
        const pixelValue = data[i]; // Assuming grayscale, use data[i], data[i + 1], data[i + 2] for RGB
        histogram[pixelValue]++;
      }

      // Draw the histogram
      //drawHistogram(histogram, ctx, canvas);

}


function drawHistogram(histogram, ctx, canvas) {
  ctx.fillStyle = 'red';

  const maxValue = Math.max(...histogram);
  const scale = canvas.height / maxValue;

  for (let i = 0; i < histogram.length; i++) {
    const barHeight = histogram[i] * scale;
    ctx.fillRect(i, canvas.height - barHeight, 1, barHeight);
  }
}

