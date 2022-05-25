var squares;
var squares2;
var squares20;
var squares19;
var squares3;
var squares9;
var squares10;
var squares12;
var squares17;
var squares5;
var squares6;
var squares16;
var squares13;
var squares11;
var squares8;
var squares7;
var squares4;
var number_of_attackers;
var number_of_attackers2;


function onDrop(source, target, piece, orientation) {
  var pn = piece.includes('b')
    ? piece.toUpperCase().substring(1, 2)
    : piece.substring(1, 2);
  pn = piece.includes('P') ? '' : pn;
  var move = piece.includes('P')
    ? source + target
    : pn + source.substring(0, 1) + target;
  move =
    piece.includes('P') && target.includes('8')
      ? target.substring(0, 1) + '8Q'
      : move; // pawn promotion

  $.get('/move', {move: move}, function(data) {
    console.log(data);
    //document.querySelector('tbody#pgn-moves');
    //document.querySelector('#pgn').innerText = data.pgn;
    moves = data.moves;
    squares = data.squares;
    squares2 = data.squares2;
    squares20 = data.squares20;
    squares19 = data.squares19;
    squares3 = data.squares3;
    squares9 = data.squares9;
    squares10 = data.squares10;
    squares12 = data.squares12;
    squares17 = data.squares17;
    squares5 = data.squares5;
    squares6 = data.squares6;
    squares16 = data.squares16;
    squares13 = data.squares13;
    squares11 = data.squares11;
    squares8 = data.squares8;
    squares7 = data.squares7;
    squares4 = data.squares4;
    number_of_attackers = data.number_of_attackers;
    number_of_attackers2 = data.number_of_attackers2;

    removeGreySquares()

    const boxes = document.querySelectorAll('.Added-images');
    boxes.forEach(box => {
      box.remove();
    });


    if (data.game_over !== 'true') {
      var tbody = document.getElementById('pgn-moves');
      tbody.innerHTML = '';
      i = 0;
      var m_len = moves.length;
      var row_number = 1;
      while (i < m_len) {
        var tr = document.createElement('tr');
        var th = document.createElement('th');
        th.setAttribute('scope', row_number.toString());
        th.innerText = row_number.toString();
        tr.appendChild(th);
        var td = document.createElement('td');
        td.innerText = moves[i].toString();
        tr.appendChild(td);
        if (m_len % 2 != 1) {
          var td = document.createElement('td');
          td.innerText = moves[i + 1].toString();
          tr.appendChild(td);
        }
        i += 2;
        row_number++;
        tbody.appendChild(tr);
      }
      board.position(data.fen);
      $(".card-body#game-moves").scrollTop($(".card-body#game-moves")[0].scrollHeight);
    } else {
        document.querySelectorAll(".game-over")[1].innerText = "Game lost";
    }
  });
}



var whiteSquareGrey = '#a9a9a9'
var blackSquareGrey = '#696969'
  
function removeGreySquares () {
    $('#board .square-55d63').css('background', '')
    const boxes = document.querySelectorAll('.Added-images');
    boxes.forEach(box => {
      box.remove();
    });
  }

  
function greySquare (square) {
  var $square = $('#board .square-' + square)
  
  var background = whiteSquareGrey
  if ($square.hasClass('black-3c85d')) {
    background = blackSquareGrey
  }
  
  $square.css('background', background)
}


function Highlight () {
    for (var i = 0; i < squares.length; i++) {
      greySquare(squares[i])
    }
}

function Highlight2 () {
  for (var i = 0; i < squares2.length; i++) {
    greySquare(squares2[i])
  }
}

function Highlight3 () {
  for (var i = 0; i < squares20.length; i++) {
    greySquare(squares20[i])
  }
  for (var i = 0; i < squares20.length; i++) {
    var src = "'img/numbers/number" + number_of_attackers[i] + ".png'";
    $('#board .square-' + squares20[i]).append("<img class = 'Added-images'  src = " + src +  " style='width: 20px;height: 20px;'>");

  } 
}

function Highlight4 () {
  for (var i = 0; i < squares19.length; i++) {
    greySquare(squares19[i])
  }
  for (var i = 0; i < squares19.length; i++) {
    var src = "'img/numbers/number" + number_of_attackers2[i] + ".png'";
    $('#board .square-' + squares19[i]).append("<img class = 'Added-images'  src = " + src +  " style='width: 20px;height: 20px;'>");

  }
}

function Highlight5 () {
  for (var i = 0; i < squares3.length; i++) {
    greySquare(squares3[i])
  }
}

function Highlight6 () {
  for (var i = 0; i < squares9.length; i++) {
    greySquare(squares9[i])
  }
}

function Highlight7 () {
  for (var i = 0; i < squares10.length; i++) {
    greySquare(squares10[i])
  }
}

function Highlight8 () {
  for (var i = 0; i < squares12.length; i++) {
    greySquare(squares12[i])
  }
}

function Highlight9 () {
  for (var i = 0; i < squares17.length; i++) {
    greySquare(squares17[i])
  }
}

function greySquareOtherColors (square,color) {
  var $square = $('#board .square-' + square)
  
  var background = color
  if ($square.hasClass('black-3c85d')) {
    background = color
  }
  
  $square.css('background', color)
}

function Highlight10 () {
  var colors = ["#1b93d8","#da123d","#1bd844","#ee0a74","#0aeebd","#eeea0a","#f1f1f1","#5f0558"];
    
  for (var i = 0; i < squares5.length; i++) {
    var pin = squares5[i];
    
    for (var j = 0; j < pin.length; j++) {
      greySquareOtherColors(pin[j],colors[i])
    }
  }
}

function Highlight11 () {
  var colors = ["#1b93d8","#da123d","#1bd844","#ee0a74","#0aeebd","#eeea0a","#f1f1f1","#5f0558"];
    
  for (var i = 0; i < squares6.length; i++) {
    var check = squares6[i];
    
    for (var j = 0; j < check.length; j++) {
      greySquareOtherColors(check[j],colors[i])
    }
  }
}

function Highlight12 () {
  for (var i = 0; i < squares16.length; i++) {
    greySquare(squares16[i])
  }
}

function Highlight13 () {
  for (var i = 0; i < squares13.length; i++) {
    greySquare(squares13[i])
  }
}

function Highlight14 () {
  for (var i = 0; i < squares11.length; i++) {
    greySquare(squares11[i])
  }
}

function Highlight15 () {
  for (var i = 0; i < squares8.length; i++) {
    greySquare(squares8[i])
  }
}

function Highlight16 () {
  var colors = ["#1b93d8","#da123d","#1bd844","#ee0a74","#0aeebd","#eeea0a","#f1f1f1","#5f0558"];
    
  for (var i = 0; i < squares7.length; i++) {
    var check = squares7[i];
    
    for (var j = 0; j < check.length; j++) {
      greySquareOtherColors(check[j],colors[i])
    }
  }
}

function Highlight17 () {
  var colors = ["#1b93d8","#da123d","#1bd844","#ee0a74","#0aeebd","#eeea0a","#f1f1f1","#5f0558"];
    
  for (var i = 0; i < squares4.length; i++) {
    var pin = squares4[i];
    
    for (var j = 0; j < pin.length; j++) {
      greySquareOtherColors(pin[j],colors[i])
    }
  }
}

function Openform(){
  document.getElementById('form1').style.display = 'block';
}


$('#startBtn').on('click', board.start)
