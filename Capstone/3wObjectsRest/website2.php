<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Data Analysis Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 1200px;
            margin: auto;
            padding: 20px;
        }
        h1 {
            background-color: #0056b3;
            color: white;
            padding: 15px;
            text-align: center;
            margin: 0;
            border-radius: 5px;
        }
        h2, h3 {
            color: #0056b3;
            text-align: center;
        }
        .form-container {
            text-align: center;
            margin-bottom: 20px;
            background-color: #e7f0ff;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #0056b3;
        }
        table {
            width: 100%;
            max-width: 600px;
            margin: 20px auto;
            border-collapse: collapse;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            background-color: #ffffff;
            border-radius: 5px;
            overflow: hidden;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dddddd;
        }
        th {
            background-color: #0056b3;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .fft-image, .ml-image {
            display: block;
            max-width: 800px; /* Adjust the maximum width to make images bigger */
            margin: 20px auto;
            border: 1px solid #dddddd;
            border-radius: 5px;
        }
        select {
            padding: 5px;
            font-size: 14px;
        }
        input[type="submit"], .redirect-button {
            padding: 5px 10px;
            background-color: #0056b3;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
        }
        input[type="submit"]:hover, .redirect-button:hover {
            background-color: #004494;
        }
        nav {
            background-color: #0056b3;
            padding: 10px 0;
            text-align: center;
        }
        nav a {
            color: white;
            text-decoration: none;
            margin: 0 15px;
            font-size: 18px;
        }
        nav a:hover {
            text-decoration: underline;
        }
    </style>
    <script>
        // Refresh the page every 10 seconds
        setInterval(function() {
            location.reload();
        }, 10000);
    </script>
</head>
<body>

<h1>Data Analysis Page</h1>

<nav>
    <a href="home_page.php">Home</a>
    <a href="website.php">Motor Data</a>
    <a href="website2.php">Data Analysis</a>
    <a href="suggestion.php">Suggestion Page</a>
</nav>

<div class="container">
    <?php
    $servername = "localhost";
    $username = "root";
    $password = "";
    $dbname = "capstone_data";
    $port = 3307; //port

    $esp_ID = 1; 
    $conn = new mysqli($servername, $username, $password, $dbname, $port);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    // Retrieve the last 3 FFT images for the hardcoded esp_ID
    $sql = "SELECT image FROM fft_images WHERE esp_ID = '$esp_ID' ORDER BY reading_time DESC LIMIT 3";
    $result = $conn->query($sql);
    if ($result->num_rows > 0) {
        echo "<h2>FFT Images</h2>";
        $images = [];
        while($row = $result->fetch_assoc()) {
            $images[] = '<img src="data:image/jpeg;base64,'.base64_encode($row['image']).'" alt="FFT Image" class="fft-image" />';
        }
        // Display images in reverse order
        foreach(array_reverse($images) as $image) {
            echo $image;
        }
    } else {
        echo "<p>No images found</p>";
    }

    // Retrieve the last 2 Machine Learning images for the hardcoded esp_ID
    $sql = "SELECT image FROM ml_images WHERE esp_ID = '$esp_ID' ORDER BY reading_time DESC LIMIT 2";
    $result = $conn->query($sql);
    if ($result->num_rows > 0) {
        echo "<h2>Machine Learning Results</h2>";
        while($row = $result->fetch_assoc()) {
            echo '<img src="data:image/jpeg;base64,'.base64_encode($row['image']).'" alt="ML Image" class="ml-image" />';
        }
    } else {
        echo "<p>No images found</p>";
    }

    $conn->close();
    ?>
</div>

</body>
</html>
