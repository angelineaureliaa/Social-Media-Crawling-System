<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PawSearch</title>
  <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@500&family=Pacifico&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="container">
    <img src="img/logo-iir.png" style="width:40%;">
    <form method="post" action="result.php">
    <div class="search-bar">
      <input type="text" placeholder="Search here..." id="search-box" name="keyword" autocomplete="off">
      <!--klo gak ada radio button atau text yang diisi, maka munculin exception-->
      <button type="submit" id="search-btn" name="search">Go</button>
    </div>
    <div class="options">
      <div class="source-section">
        <span class="label">Source:</span>
        <div class="checkboxes">
          <label>
            <input type="checkbox" name="x" value="x">
            X
          </label>
          <label>
            <input type="checkbox" name="ig" value="instagram">
            Instagram
          </label>
          <label>
            <input type="checkbox" name="youtube" value="youtube">
            YouTube
          </label>
        </div>
      </div>
      <div class="method-section">
        <span class="label">Method:</span>
        <div class="radio-buttons">
          <label>
            <input type="radio" name="method" value="jaccard">
            Jaccard
          </label>
          <label>
            <input type="radio" name="method" value="cosine">
            Cosine
          </label>
        </div>
      </div>
    </div>
    </form>
  </div>
</body>
</html>
