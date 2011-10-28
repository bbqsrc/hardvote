<!DOCTYPE html>
<html>
<head>
<style type="text/css">
* {
	margin: 0;
	padding: 0;
}

html, body {
	font-family: "Myriad Pro", "Arial", sans-serif;
	background-color: gray;
}

input[type="text"], textarea {
	width: 95%;
}

input, textarea {
	padding: 3px;
	border: 1px solid #ccc;
}

#poll {
	background-color: white;
	width: 800px;
	margin: 0 auto;
	padding: 3px 0px;
}

.section {
	border: 1px solid black;
	margin: 12px;
	padding: 6px;
}

.question {
	/*border: 1px dotted black;*/
	margin: 6px;
	margin-top: 12px;
	padding: 6px;
}

.multiple ol {
	margin-left: 8px;
	list-style: none;
}

.gauge li {
	display: inline;
	list-style-type: none;
	padding-right: 20px;
}

.gauge input, .multiple input, .preference input {
	margin-right: 8px;
}

.preferential input {
	width: 48px;
	margin-right: 3px;
}

#submit {
	text-align: center;
	font-size: 10pt;
	padding: 6px;
}

.warning {
	margin-top: 2px;
	padding: 3px;
	border: 1px solid red;
	background-color: #FF9999;
}

span.asterisk {
	color: red;
	margin-left: 4px;
}
</style>
<script type='text/javascript' src='/static/es5-shim.min.js'></script>
<script type='text/javascript' src='/static/jquery.min.js'></script>
<script type='text/javascript' src='/static/hardvalidate.js'></script>
<title></title>
</head>
<body>
<div id="poll"></div>
<script type="text/javascript">
$(document).ready(function() {
	HardValidate.bindSubmit("#poll-submit", "#poll-form");
});
</script>
</body>
</html>
