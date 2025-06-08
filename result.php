<?php
require_once __DIR__ . '/vendor/autoload.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Crawling Result</title>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;600&family=Great+Vibes&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: Quicksand, sans-serif;
      background: #ffe4ec;
      margin: 0;
      padding: 20px;
      text-align: center;
    }

    h1 {
      color: black;
      margin-bottom: 20px;
      font-family: 'Pacifico', cursive;
      font-size: 48px;
    }

    .card {
      position: relative;
      background: #fff;
      padding: 20px;
      margin: 15px auto;
      width: 80%;
      max-width: 600px;
      border-radius: 15px;
      box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.1), -5px -5px 10px rgba(255, 255, 255, 0.7);
    }

    .text-container {
      text-align: left;
      margin-top: 60px;
    }

    .text-container p {
      margin: 5px 0;
      color: #555;
    }

    .source-container {
      position: absolute;
      top: 15px;
      right: 20px;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .source {
      font-size: 14px;
      color: #888;
    }

    .logo {
      width: 40px;
      height: 40px;
      background: #ddd;
      border-radius: 50%;
      display: flex;
      justify-content: center;
      align-items: center;
      font-size: 12px;
      font-weight: bold;
      color: #fff;
      box-shadow: inset 3px 3px 5px rgba(0, 0, 0, 0.2), inset -3px -3px 5px rgba(255, 255, 255, 0.5);
    }
    #customAlert {
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background-color: rgba(0, 0, 0, 0.5); /* Background semi-transparan */
      width: 100%;
      height: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 1000; /* Pastikan alert di atas elemen lain */
    }

    .alert-box {
      background-color: #fff;
      padding: 20px;
      border-radius: 5px;
      box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
      text-align: center;
    }

    .alert-box button {
      background-color: #ff6ba6; /* Warna pink */
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 5px;
      cursor: pointer;
    }
  </style>
</head>
<header style="display: flex; align-items: center; justify-content: space-between; padding: 20px 10px;">
  <img src="img/logo-iir.png" alt="logo" style="width: 100px; height: auto; margin-left: 20px;">
  <div style="flex-grow: 1; text-align: center;">
    <h1 style="font-family: 'Nunito', sans-serif; font-size: 48px; color: #333; margin: 0;">
      Crawling Result
    </h1>
    <h2 style="font-family: 'Quicksand', sans-serif; font-size: 32px; color: #555; margin: 10px 0;">
      <?=$_POST['keyword']?>
    </h2>
  </div>
  <h2 style="font-family: 'Quicksand', sans-serif; font-size: 20px; margin: 0; color: #555; text-align: right; margin-right: 20px;text-transform:'uppercase'">Method: <?=$_POST['method']?>
</header>
<body>
  <div id="customAlert" style="display: none;">
    <div class="alert-box">
      <p id="alertMessage"></p>
      <button onclick="hideAlert()">OK</button>
    </div>
  </div>

  <script>
    function showAlert(message) {
    document.getElementById("alertMessage").innerText = message;
    document.getElementById("customAlert").style.display = "flex";
  }

    function hideAlert() {
      document.getElementById("customAlert").style.display = "none";
    }
  </script>


<?php
  $crawling_all_result = [];
  set_time_limit(0); //harus diset time limitnya 0 biar klo dia ngecrawl gak tb" gagal, soalnya proses crawlingnya lama TT
  if (isset($_POST['search'])) { //klo user klik tombol search
    $check_process = shell_exec("pgrep -fl chromedriver");
    if (!empty($check_process)) {
      shell_exec("pkill -f 'chromedriver'");
    }
    $keyword = $_POST['keyword']; //cari keywordnya apa

    $alertMessages = [];
    if(isset($_POST['ig'])){
      //BACA METHODNYA
      $method = $_POST['method'];
      $query_search = str_replace(" ", "#", $keyword);
      $insta_crawling_result = json_decode(shell_exec("py insta.py $query_search $method"), true);
      if(is_array($insta_crawling_result) && count($insta_crawling_result) > 0){
        foreach ($insta_crawling_result as $key => $value) {
          if($value['sim']>0){ #karena klo dia 0 berarti hasil crawl tdk mengandung keyword
            $crawling_all_result[] = [
              'source' => 'Instagram',
              'image' => 'img/instagram.png',
              'ori_text' => $value['ori'],
              'preprocess_text' => $value['preprocessed'],
              'similarity' => $value['sim']
            ];
          }
        }
      }
      else{
        echo "<script>showAlert('Tidak ada hasil crawling dari Instagram.');</script>";
      }
    }
    if (isset($_POST['youtube'])) {
      //BACA METHODNYA
      $method = $_POST['method'];
      //klo user checklist youtube, maka panggil file crawling youtube
      //waktu buka file skalian kirim keyword yang ditulis user
      //klo user kirim pake spasi, maka replace dulu dengan #
      $query_search = str_replace(" ", "#", $keyword);
      //ini simpen data hasil crawling >> true nunjukin klo associative array
      //kirim parameter keyword sekaligus methodnya apa
      $youtube_crawling_result = json_decode(shell_exec("py ytb.py $query_search $method"), true);
      //print_r($youtube_crawling_result);
      if(is_array($youtube_crawling_result) && count($youtube_crawling_result)>0){
        foreach ($youtube_crawling_result as $key => $value) {
          if($value['sim']>0){ #karena klo dia 0 berarti hasil crawl tdk mengandung keyword
            $crawling_all_result[] = [
              'source' => 'Youtube',
              'image' => 'img/youtube.png',
              'ori_text' => $value['ori'],
              'preprocess_text' => $value['preprocessed'],
              'similarity' => $value['sim']
            ];
          }
        }
      }
      else{
        echo "<script>showAlert('Tidak ada hasil crawling dari Youtube.');</script>";
      }
    }
    if (isset($_POST['x'])) {
      //BACA METHODNYA
      $method = $_POST['method'];
      $query_search = str_replace(" ", "#", $keyword);
      //ini simpen data hasil crawling >> true nunjukin klo associative array
      //kirim parameter keyword sekaligus methodnya apa
      $x_crawl_result = json_decode(shell_exec("python coba.py $query_search $method"), true);
      if(is_array($x_crawl_result) && count($x_crawl_result) > 0){
        foreach ($x_crawl_result as $key => $value) {
          if($value['sim']>0){ #karena klo dia 0 berarti hasil crawl tdk mengandung keyword
            $crawling_all_result[] = [
              'source' => 'X',
              'image' => 'img/x-logo.png',
              'ori_text' => $value['ori'],
              'preprocess_text' => $value['preprocessed'],
              'similarity' => $value['sim']
            ];
          }
        }
      }
      else{
        echo "<script>showAlert('Tidak ada hasil crawling dari X.');</script>";
      }
    }
}
  usort($crawling_all_result, function ($x, $y) {
    //semakin besar semakin mirip
    return $y['similarity'] <=> $x['similarity']; //urutin based on index similarity
  });

  ?>
  <!-- BUAT CARDNYA DINAMIS -->
  <?php if(count($crawling_all_result)>0):?>
  <?php foreach ($crawling_all_result as $key => $value): ?>
    <div class="card">
      <div class="source-container">
        <p class="source"><strong><?= $value['source'] ?></strong></p>
        <!-- taruh logo yutup disini, ini sih nanti tergantung hasil crawlingnya dapet apa -->
        <img class="logo" src="<?= $value['image'] ?>" alt="logo youtube">
      </div>
      <div class="text-container">
        <p><strong>Original Text :</strong> <?= $value['ori_text'] ?></p>
        <p><strong>Preprocessing Text :</strong> <?= $value['preprocess_text'] ?></p>
        <p><strong>Similarity :</strong><?= $value['similarity'] ?></p>
      </div>
    </div>
  <?php endforeach; ?>
  <?php endif; ?>
</body>
</html>