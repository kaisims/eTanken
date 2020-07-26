function authorise(){
    var ajax = new XMLHttpRequest();
    ajax.onreadystatechange = function () {
        //console.log(this.status + " " + this.response + " " + ajax.readyState)
        if (ajax.readyState===4 && ajax.status===200) {
            var link = "http://" + window.document.location.host + "/charge/" + this.responseText
            loadUrl(link);
        }
        else if (ajax.readyState=== 4 && ajax.status===204){
            console.log("again")
            sleep(1000).then(()=>authorise())
        }
        else if (ajax.readyState=== 4){
            link = "http://" + window.document.location.host + "/chooseChargePoint/"
            loadUrl(link);
        }
    }
    ajax.open("OPTIONS", "");
    ajax.send();
}
authorise()
function startTimer(duration, display) {
    var timer = duration, seconds;
    setInterval(function () {
        seconds = parseInt(timer % 60, 10);
        seconds = seconds < 10 ? "0" + seconds : seconds;
        display.textContent = seconds + "s";
        if (--timer < 0) {
            timer = 0;
        }
    }, 1000);
}

window.onload = function () {
    var thirtySeconds = 35,
        display = document.querySelector('#timer');
    startTimer(thirtySeconds, display);
};