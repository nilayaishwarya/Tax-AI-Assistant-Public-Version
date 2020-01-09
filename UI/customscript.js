var SpeechRecognition = SpeechRecognition || webkitSpeechRecognition
var SpeechGrammarList = SpeechGrammarList || webkitSpeechGrammarList
var SpeechRecognitionEvent = SpeechRecognitionEvent || webkitSpeechRecognitionEvent

//var colors = [ 'aqua' , 'azure' , 'beige', 'bisque', 'black', 'blue', 'brown', 'chocolate', 'coral', 'crimson', 'cyan', 'fuchsia', 'ghostwhite', 'gold', 'goldenrod', 'gray', 'green', 'indigo', 'ivory', 'khaki', 'lavender', 'lime', 'linen', 'magenta', 'maroon', 'moccasin', 'navy', 'olive', 'orange', 'orchid', 'peru', 'pink', 'plum', 'purple', 'red', 'salmon', 'sienna', 'silver', 'snow', 'tan', 'teal', 'thistle', 'tomato', 'turquoise', 'violet', 'white', 'yellow'];
//var grammar = '#JSGF V1.0; grammar colors; public <color> = ' + colors.join(' | ') + ' ;'

var recognition = new SpeechRecognition();
recognition.lang = 'en-US';
recognition.interimResults = false;
recognition.maxAlternatives = 1;

var diagnostic = document.querySelector('.output');
var bg = document.querySelector('html');
var hints = document.querySelector('.hints');

var reply = '';
//colors.forEach(function(v, i, a){
//  console.log(v, i);
//  colorHTML += '<span style="background-color:' + v + ';"> ' + v + ' </span>';
//});
hints.innerHTML = reply + '.';

document.body.onclick = function () {
  // $('#mybutton').click(function () {
  //   recognition.start();
  //   console.log('Ready to receive a command.');
  // });
}

$('#mybutton').click = function () {
  recognition.start();
  console.log('Ready to receive a command.');
};

function dborder() {
  document.getElementById("mydiv").style.border = "thick solid #86BC25";
}

function microphone() {
  //debugger;
  $('#DeloitteHeader').hide();
  $('#canvas').remove();
  $( "p.output" ).empty();
  $('#divMicrophone').css('margin-top', '40px');
  $("#mybutton").removeClass("notRec");
  $('.microphonebutton').css('width', '23%');
  recognition.start();
  $('#mydiv').css('border', '1px solid rgb(134, 188, 37)');
  $("#mybutton").addClass("Rec");
  // document.getElementById("mybutton")
  console.log('Ready to receive a command.');
}
var spoken = "";

recognition.onresult = async function (event) {

  // The SpeechRecognitionEvent results property returns a SpeechRecognitionResultList object
  // The SpeechRecognitionResultList object contains SpeechRecognitionResult objects.
  // It has a getter so it can be accessed like an array
  // The [last] returns the SpeechRecognitionResult at the last position.
  // Each SpeechRecognitionResult object contains SpeechRecognitionAlternative objects that contain individual results.
  // These also have getters so they can be accessed like arrays.
  // The [0] returns the SpeechRecognitionAlternative at position 0.
  // We then return the transcript property of the SpeechRecognitionAlternative object

  $("#mybutton").removeClass("Rec");
  var last = event.results.length - 1;
  var replyyy = event.results[last][0].transcript;
  var x = await addPost(replyyy);

  await resetCanvas();
  //then(e => e.json().then(x=>console.log(x.response)));
  //var y = await x.json();
  //console.log(y.response);
  //var sp= x.response;
  //debugger;
  //console.log(sp)

  spoken = "" + replyyy;
  var speak_text = "" + x.response
  if (x.graph == true) {
    //call graph function
    if (x.graph_type == 'bar') {
      await barplotter(x);
      $('#canvas').css("background-color", "white");

    }

    if (x.graph_type == 'pie') {
      await pieplotter(x);
      $('#canvas').css("background-color", "white");
    }

  }
  else {
    document.getElementById("container").style.display = "none";
  }
  responsiveVoice.speak(speak_text);
  //await plotter();
  // debugger;

  textContent = "Deloitte Assistant";
  diagnostic.textContent =  x.response;
  console.log('Confidence: ' + event.results[0][0].confidence);

}

recognition.onspeechend = function () {
  recognition.stop();  
}

recognition.onnomatch = function (event) {
  diagnostic.textContent = "I didn't recognise that.";
}

recognition.onerror = function (event) {
  diagnostic.textContent = 'Error occurred in recognition: ' + event.error;
}

async function addPost(x) {
  //let response = new Object(); // "object constructor" syntax
  var response = await fetch('https://deloitteassistantapi.azurewebsites.net/responder', {
    method: 'POST',
    body: JSON.stringify({
      text_query: x,
    }),
    headers: {
      "Content-type": "application/json; charset=UTF-8"
    }
  }).then(x => x.json())//.then(y=>function x(){
  //   //let p = new Object(); // "object constructor" syntax
  //debugger;
  //   var p = {
  //     "graph": null,
  //     "graph_data": {
  //         "data": null,
  //         "index": null,
  //         "name": null
  //     },
  //     "graph_type": null,
  //     "graph_x": null,
  //     "graph_y": null,
  //     "note": null,
  //     "response": null
  // };
  // debugger;
  // p.graph = y.graph;
  // p.graph_data.data = y.graph_data.data;
  // p.graph_data.index = y.graph_data.index;
  // p.graph_data.name = y.graph_data.name;
  // p.graph_type = y.graph_type;
  // p.graph_x = y.graph_x;
  // p.graph_y = y.graph_y;
  // p.note = y.note;
  // p.response = y.response;
  // return p; 
  // });
  //   .then(response => response.json())
  //   .then(json => y = json.response);
  //   console.log('y----->',y);
  return response;
  //   .then(
  //     return json.response;
  //   )

}

async function barplotter(inp) {
  //debugger;
  document.getElementById("container").style.display = "block";
  var fortitle = "Number of " + inp.graph_y + " for the different " + inp.graph_x;
  //could be something else ?

  var x = ['RPA LTD', 'TEST DG LTD'];
  var color = Chart.helpers.color;
  var barChartData = {
    labels: inp.graph_data.index,
    datasets: [{
      label: fortitle,
      backgroundColor: "rgba(134, 188, 37, 1)",
      borderColor: 'rgb(218, 41, 28)',
      borderWidth: 1,
      data: inp.graph_data.data
    }]

  };

  var ctx = document.getElementById('canvas').getContext('2d');
  window.myBar = new Chart(ctx, {
    type: 'bar',
    data: barChartData,
    options: {
      responsive: true,
      legend: {
        position: 'top',
        fontSize: 30,
        labels: {

          fontColor: 'white',
          fontSize: 30,
        }
      },
      title: {
        display: true,
        text: 'Bar Chart'
      }
    }
  });

}

async function pieplotter(inp) {
  //debugger;
  document.getElementById("container").style.display = "block";

  var fortitle = "Number of " + inp.graph_y + " for the different " + inp.graph_x;

  var config = {
    type: 'pie',
    data: {
      datasets: [{
        data: inp.graph_data.data,
        backgroundColor: [
          'rgba(218, 41, 28, 1)',
          'rgba(0, 151, 169, 1)',
          'rgba(196, 214, 0, 1)',
          'rgba(255, 205, 0, 1)',
          'rgba(83, 86, 90, 1)',
          'rgba(1, 33, 105, 1)'
        ],
        borderColor: [
          'rgba(255,99,132,1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)'
      ],
      borderWidth: 1,

        label: fortitle
      }],
      labels: inp.graph_data.index
    },
    options: {
      responsive: true
    },
    legend: {
      fontSize: "20px",
    }
  };
  var ctx = document.getElementById('canvas').getContext('2d');
  window.myPie = new Chart(ctx, config);

}
document.getElementById("container").style.display = "none";
//var colorNames = Object.keys(window.chartColors);

async function resetCanvas() {
  //debugger;
  $('#canvas').remove(); // this is my <canvas> element

  $('#chartWrapper').append('<canvas id="canvas" style="display block;" width="1422" height="300" class="chartjs-render-monitor"></canvas>');
  canvas = document.querySelector('canvas');
  ctx = canvas.getContext('2d');
  ctx.canvas.width = $('#graph').width(1422); // resize to parent width
  ctx.canvas.height = $('#graph').height(711); // resize to parent height
  var x = canvas.width / 2;
  var y = canvas.height / 2;
  ctx.font = '10pt Verdana';
  ctx.textAlign = 'center';
  ctx.fillText('This text is centered on the canvas', x, y);
};
